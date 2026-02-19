#!/usr/bin/env node
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

const HOMUNCULUS_DIR = path.join(os.homedir(), '.claude', 'homunculus');
const INSTINCTS_DIR = path.join(HOMUNCULUS_DIR, 'instincts', 'personal');
const LOG_FILE = path.join(HOMUNCULUS_DIR, 'observer.log');

function log(msg) {
  try { fs.appendFileSync(LOG_FILE, `[${new Date().toISOString()}] ${msg}\n`, 'utf8'); } catch {}
}

function writeInstincts(output) {
  const blocks = output.split('===INSTINCT===').slice(1);
  let count = 0;
  for (const block of blocks) {
    const content = block.split('===END===')[0].trim();
    if (!content) continue;
    const id = content.match(/^id:\s*(.+)$/m)?.[1]?.trim();
    if (!id) continue;
    const trigger = content.match(/^trigger:\s*(.+)$/m)?.[1]?.trim() || '';
    const confidence = content.match(/^confidence:\s*(.+)$/m)?.[1]?.trim() || '0.3';
    const domain = content.match(/^domain:\s*(.+)$/m)?.[1]?.trim() || 'workflow';
    const title = content.match(/^title:\s*(.+)$/m)?.[1]?.trim() || id;
    const action = content.match(/^action:\s*(.+)$/m)?.[1]?.trim() || '';
    const evidence = content.match(/^evidence:\s*(.+)$/m)?.[1]?.trim() || '';
    const today = new Date().toISOString().slice(0, 10);

    const md = `---\nid: ${id}\ntrigger: "${trigger}"\nconfidence: ${confidence}\ndomain: "${domain}"\nsource: session-observation\nlast_observed: ${today}\n---\n\n# ${title}\n\n## Action\n${action}\n\n## Evidence\n- ${evidence}\n`;

    try {
      if (!fs.existsSync(INSTINCTS_DIR)) fs.mkdirSync(INSTINCTS_DIR, { recursive: true });
      fs.writeFileSync(path.join(INSTINCTS_DIR, `${id}.md`), md, 'utf8');
      count++;
    } catch (e) { log(`Write failed for ${id}: ${e.message}`); }
  }
  return count;
}

const promptFile = process.argv[2];
const sessionId = process.argv[3] || 'unknown';

if (!promptFile || !fs.existsSync(promptFile)) {
  log(`[${sessionId}] Prompt file not found: ${promptFile}`);
  process.exit(1);
}

log(`[${sessionId}] Observer started`);

try {
  const cmd = `claude --model haiku --max-turns 1 --print --no-session-persistence --disable-slash-commands --tools "" < "${promptFile}"`;
  const output = execSync(cmd, { encoding: 'utf8', timeout: 120000, windowsHide: true });

  if (output.includes('NO_PATTERNS_DETECTED')) {
    log(`[${sessionId}] No patterns detected`);
  } else {
    const count = writeInstincts(output);
    log(`[${sessionId}] Created ${count} instincts`);
  }
  log(`[${sessionId}] Output preview: ${output.slice(0, 500)}`);
} catch (err) {
  log(`[${sessionId}] Failed: ${err.message?.slice(0, 200)} | stderr: ${(err.stderr || '').slice(0, 200)}`);
}

try { fs.unlinkSync(promptFile); } catch {}
