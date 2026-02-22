#!/usr/bin/env node
/**
 * Continuous Learning - Session Evaluator
 *
 * Runs on SessionEnd hook. Filters current session's observations,
 * then spawns a background claude --model haiku process to extract
 * reusable patterns as instinct files.
 *
 * Anti-recursion: observer sessions are short (max-turns 5),
 * naturally filtered by minSessionLength threshold.
 */

const path = require('path');
const fs = require('fs');
const os = require('os');
const { spawn } = require('child_process');
const {
  ensureDir,
  readFile,
  countInFile,
  commandExists,
  log
} = require('../lib/utils');

const HOMUNCULUS_DIR = path.join(os.homedir(), '.claude', 'homunculus');
const OBSERVATIONS_FILE = path.join(HOMUNCULUS_DIR, 'observations.jsonl');
const INSTINCTS_DIR = path.join(HOMUNCULUS_DIR, 'instincts', 'personal');
const PROMPT_FILE = path.join(HOMUNCULUS_DIR, 'observer-prompt.md');
const LOG_FILE = path.join(HOMUNCULUS_DIR, 'observer.log');
const MIN_SESSION_LENGTH = 5;
const MIN_OBSERVATIONS = 5;

function appendLog(msg) {
  const ts = new Date().toISOString();
  try {
    fs.appendFileSync(LOG_FILE, `[${ts}] ${msg}\n`, 'utf8');
  } catch {}
}

function filterObservationsBySession(sessionId) {
  if (!fs.existsSync(OBSERVATIONS_FILE)) return [];
  const lines = fs.readFileSync(OBSERVATIONS_FILE, 'utf8').split('\n').filter(Boolean);
  return lines.filter(line => {
    try {
      const obj = JSON.parse(line);
      return obj.session && obj.session === sessionId;
    } catch { return false; }
  });
}

async function main() {
  // Claude Code passes hook data via stdin as JSON
  let stdinData = '';
  try {
    process.stdin.setEncoding('utf8');
    for await (const chunk of process.stdin) {
      stdinData += chunk;
    }
  } catch {}

  let transcriptPath, sessionId;
  if (stdinData.trim()) {
    try {
      const input = JSON.parse(stdinData);
      transcriptPath = input.transcript_path;
      sessionId = input.session_id;
    } catch {}
  }

  if (!transcriptPath) {
    appendLog('SKIP: no transcript_path in stdin');
    process.exit(0);
  }
  if (!fs.existsSync(transcriptPath)) {
    appendLog(`SKIP: transcript not found: ${transcriptPath}`);
    process.exit(0);
  }

  const messageCount = countInFile(transcriptPath, /"type":"user"/g);
  if (messageCount < MIN_SESSION_LENGTH) {
    appendLog(`SKIP: only ${messageCount} user messages (need ${MIN_SESSION_LENGTH})`);
    process.exit(0);
  }

  // Filter observations for this session
  const sessionObs = filterObservationsBySession(sessionId);
  if (sessionObs.length < MIN_OBSERVATIONS) {
    appendLog(`Session ${sessionId?.slice(-8)}: only ${sessionObs.length} observations, skipping`);
    process.exit(0);
  }

  // Build prompt with embedded observations
  let prompt = readFile(PROMPT_FILE);
  if (!prompt) {
    appendLog('observer-prompt.md not found, skipping');
    process.exit(0);
  }
  ensureDir(INSTINCTS_DIR);
  prompt = prompt.replace(/\{\{OBSERVATIONS\}\}/g, sessionObs.join('\n'));

  // Check claude CLI available
  if (!commandExists('claude')) {
    appendLog('claude CLI not found in PATH, skipping');
    process.exit(0);
  }

  // Write prompt to temp file
  const promptFile = path.join(os.tmpdir(), `claude-prompt-${Date.now()}.txt`);
  fs.writeFileSync(promptFile, prompt, 'utf8');

  // Spawn run-observer.js as detached background process
  appendLog(`Session ${sessionId?.slice(-8)}: ${sessionObs.length} observations, spawning observer`);

  const runObserver = path.join(__dirname, 'run-observer.js');
  const child = spawn(process.execPath, [runObserver, promptFile, sessionId || 'unknown'], {
    detached: true,
    stdio: 'ignore',
    windowsHide: true
  });

  child.unref();
  process.exit(0);
}

main().catch(err => {
  appendLog(`Error: ${err.message}`);
  process.exit(0);
});
