#!/usr/bin/env node
/**
 * Phase Manager Hook - Detect phase transitions via AskUserQuestion
 * PostToolUse hook for AskUserQuestion tool calls
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

const PHASE_KEYWORDS = ['进入 Discovery', '进入 Planning', '进入 Execution', '进入 Documentation-update', '进入 Deploy', '返回 Execution', '进入 Planning'];
const PHASE_MAP = {
  'Discovery': 'discovery',
  'Planning': 'planning',
  'Execution': 'execution',
  'Documentation-update': 'documentation-update',
  'Deploy': 'deploy'
};

function getProjectDir() {
  const projectsDir = path.join(os.homedir(), '.claude', 'projects');
  const cwd = process.cwd();
  const projectKey = cwd.replace(/[^a-zA-Z0-9]/g, '-').replace(/-+/g, '-');

  if (!fs.existsSync(projectsDir)) return null;

  const dirs = fs.readdirSync(projectsDir);
  for (const dir of dirs) {
    if (projectKey.includes(dir) || dir.includes(projectKey.slice(0, 20))) {
      return path.join(projectsDir, dir);
    }
  }
  return null;
}

async function main() {
  let data = '';
  process.stdin.setEncoding('utf8');
  for await (const chunk of process.stdin) {
    data += chunk;
  }
  if (!data.trim()) { process.exit(0); }

  try {
    const input = JSON.parse(data);
    const toolName = input.tool_name || '';

    if (toolName !== 'AskUserQuestion') { process.exit(0); }

    const toolOutput = input.tool_output || '';
    const outputStr = typeof toolOutput === 'object' ? JSON.stringify(toolOutput) : String(toolOutput);

    // Check if user selected a phase transition option
    let newPhase = null;
    for (const keyword of PHASE_KEYWORDS) {
      if (outputStr.includes(keyword)) {
        const phaseName = keyword.replace(/^(进入|返回)\s*/, '');
        newPhase = PHASE_MAP[phaseName] || phaseName.toLowerCase();
        break;
      }
    }

    if (!newPhase) { process.exit(0); }

    // Update phase-state.json
    const projectDir = getProjectDir();
    if (!projectDir) { process.exit(0); }

    const phaseFile = path.join(projectDir, 'phase-state.json');
    const phaseState = {
      current_phase: newPhase,
      last_transition: new Date().toISOString()
    };

    fs.mkdirSync(projectDir, { recursive: true });
    fs.writeFileSync(phaseFile, JSON.stringify(phaseState, null, 2), 'utf8');

    console.error(`[系统] 阶段已切换到 ${newPhase}，请加载 Skill(skill: "${newPhase}")`);

  } catch {}

  process.exit(0);
}

main();
