#!/usr/bin/env node
/**
 * Continuous Learning v2 - Observation Hook (Node.js port for Windows)
 *
 * Captures tool use events for pattern analysis.
 * Claude Code passes hook data via stdin as JSON.
 *
 * Port of observe.sh for cross-platform compatibility.
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

const CONFIG_DIR = path.join(os.homedir(), '.claude', 'homunculus');
const OBSERVATIONS_FILE = path.join(CONFIG_DIR, 'observations.jsonl');
const MAX_FILE_SIZE_MB = 10;

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function archiveIfNeeded() {
  if (!fs.existsSync(OBSERVATIONS_FILE)) return;
  try {
    const stats = fs.statSync(OBSERVATIONS_FILE);
    const sizeMB = stats.size / (1024 * 1024);
    if (sizeMB >= MAX_FILE_SIZE_MB) {
      const archiveDir = path.join(CONFIG_DIR, 'observations.archive');
      ensureDir(archiveDir);
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
      fs.renameSync(OBSERVATIONS_FILE, path.join(archiveDir, `observations-${timestamp}.jsonl`));
    }
  } catch {
    // Ignore errors
  }
}

async function main() {
  let data = '';
  process.stdin.setEncoding('utf8');

  for await (const chunk of process.stdin) {
    data += chunk;
  }

  if (!data.trim()) {
    process.exit(0);
  }

  try {
    const input = JSON.parse(data);

    // Check if disabled
    if (fs.existsSync(path.join(CONFIG_DIR, 'disabled'))) {
      process.exit(0);
    }

    ensureDir(CONFIG_DIR);

    const toolName = input.tool_name || input.tool || 'unknown';
    const toolInput = input.tool_input || input.input || {};
    const toolOutput = input.tool_output || input.output || '';
    const sessionId = input.session_id || 'unknown';
    const hookType = input.hook_type || 'unknown';

    // Truncate large inputs/outputs
    let inputStr;
    if (typeof toolInput === 'object') {
      inputStr = JSON.stringify(toolInput).slice(0, 5000);
    } else {
      inputStr = String(toolInput).slice(0, 5000);
    }

    let outputStr;
    if (typeof toolOutput === 'object') {
      outputStr = JSON.stringify(toolOutput).slice(0, 5000);
    } else {
      outputStr = String(toolOutput).slice(0, 5000);
    }

    const event = hookType.includes('Pre') ? 'tool_start' : 'tool_complete';

    const observation = {
      timestamp: new Date().toISOString(),
      event,
      tool: toolName,
      session: sessionId
    };

    if (event === 'tool_start') {
      observation.input = inputStr;
    } else {
      observation.output = outputStr;
    }

    // Archive if file too large
    archiveIfNeeded();

    // Append observation
    fs.appendFileSync(OBSERVATIONS_FILE, JSON.stringify(observation) + '\n', 'utf8');

  } catch {
    // Hook must not block tool execution
  }

  process.exit(0);
}

main();
