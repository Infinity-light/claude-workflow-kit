#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const CLAUDE_DIR = path.resolve(__dirname);
const SETTINGS_PATH = path.join(CLAUDE_DIR, 'settings.json');
const HOOKS_TEMPLATE = path.join(CLAUDE_DIR, 'hooks.template.json');

// Runtime directories to ensure exist
const RUNTIME_DIRS = [
  'sessions', 'cache', 'debug', 'telemetry', 'projects',
  'plans', 'tasks', 'todos', 'ide', 'session-env', 'paste-cache',
  'homunculus/instincts/personal', 'homunculus/instincts/inherited',
  'homunculus/evolved/agents', 'homunculus/evolved/commands', 'homunculus/evolved/skills',
  'skills/learned'
];

function loadHooksTemplate() {
  const raw = fs.readFileSync(HOOKS_TEMPLATE, 'utf8');
  const claudePath = CLAUDE_DIR.replace(/\\/g, '/');
  return JSON.parse(raw.replace(/__DIR__/g, claudePath));
}

function ensureDirs() {
  let created = 0;
  for (const dir of RUNTIME_DIRS) {
    const full = path.join(CLAUDE_DIR, dir);
    if (!fs.existsSync(full)) {
      fs.mkdirSync(full, { recursive: true });
      created++;
    }
  }
  return created;
}

function setup() {
  console.log('=== Claude Workflow Kit Setup ===\n');

  // 1. Ensure runtime directories
  const dirsCreated = ensureDirs();
  console.log(`[dirs] ${dirsCreated} directories created`);

  // 2. Load hooks template
  const hooks = loadHooksTemplate();

  // 3. Merge into settings.json
  if (fs.existsSync(SETTINGS_PATH)) {
    const settings = JSON.parse(fs.readFileSync(SETTINGS_PATH, 'utf8'));
    settings.hooks = hooks;
    fs.writeFileSync(SETTINGS_PATH, JSON.stringify(settings, null, 2) + '\n');
    console.log('[hooks] merged into existing settings.json');
  } else {
    const settings = {
      "$schema": "https://json.schemastore.org/claude-code-settings.json",
      "alwaysThinkingEnabled": true,
      "model": "opus",
      "env": { "ANTHROPIC_AUTH_TOKEN": "", "ANTHROPIC_BASE_URL": "" },
      "hooks": hooks
    };
    fs.writeFileSync(SETTINGS_PATH, JSON.stringify(settings, null, 2) + '\n');
    console.log('[hooks] created new settings.json (fill in your API token!)');
  }

  console.log('\nDone. Run `claude` to start.');
}

setup();
