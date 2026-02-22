#!/usr/bin/env node
/**
 * SessionStart Hook - Load previous context on new session
 *
 * Cross-platform (Windows, macOS, Linux)
 *
 * Runs when a new Claude session starts. Checks for recent session
 * files and notifies Claude of available context to load.
 */

const path = require('path');
const fs = require('fs');
const {
  getClaudeDir,
  getSessionsDir,
  getLearnedSkillsDir,
  findFiles,
  ensureDir,
  log
} = require('../lib/utils');
const { getPackageManager, getSelectionPrompt } = require('../lib/package-manager');
const { listAliases } = require('../lib/session-aliases');

async function main() {
  const sessionsDir = getSessionsDir();
  const learnedDir = getLearnedSkillsDir();

  // Ensure directories exist
  ensureDir(sessionsDir);
  ensureDir(learnedDir);

  // Check for recent session files (last 7 days)
  // Match both old format (YYYY-MM-DD-session.tmp) and new format (YYYY-MM-DD-shortid-session.tmp)
  const recentSessions = findFiles(sessionsDir, '*-session.tmp', { maxAge: 7 });

  if (recentSessions.length > 0) {
    const latest = recentSessions[0];
    log(`[SessionStart] Found ${recentSessions.length} recent session(s)`);
    log(`[SessionStart] Latest: ${latest.path}`);
  }

  // Check for learned skills
  const learnedSkills = findFiles(learnedDir, '*.md');

  if (learnedSkills.length > 0) {
    log(`[SessionStart] ${learnedSkills.length} learned skill(s) available in ${learnedDir}`);
  }

  // Load instincts into session context (output to stdout so Claude can see them)
  const instinctsDir = path.join(getClaudeDir(), 'homunculus', 'instincts', 'personal');
  const instinctLines = [];
  if (fs.existsSync(instinctsDir)) {
    const instinctFiles = findFiles(instinctsDir, '*.md');
    if (instinctFiles.length > 0) {
      instinctLines.push(`[直觉系统] 已加载 ${instinctFiles.length} 条经验：`);
      for (const f of instinctFiles) {
        try {
          const content = fs.readFileSync(f.path, 'utf8');
          const trigger = content.match(/^trigger:\s*"?(.+?)"?\s*$/m)?.[1] || '';
          const action = content.match(/## Action\n([\s\S]*?)(?:\n##|$)/)?.[1]?.trim() || '';
          const confidence = content.match(/^confidence:\s*(.+)$/m)?.[1] || '?';
          if (trigger && action) {
            instinctLines.push(`  - [${confidence}] 当${trigger} → ${action.slice(0, 150)}`);
          }
        } catch {}
      }
      log(instinctLines.join('\n')); // stderr for terminal logging
    }
  }

  // Check for available session aliases
  const aliases = listAliases({ limit: 5 });

  if (aliases.length > 0) {
    const aliasNames = aliases.map(a => a.name).join(', ');
    log(`[SessionStart] ${aliases.length} session alias(es) available: ${aliasNames}`);
    log(`[SessionStart] Use /sessions load <alias> to continue a previous session`);
  }

  // Check for active phase state
  const projectsDir = path.join(getClaudeDir(), 'projects');
  const cwd = process.cwd();
  // Sanitize cwd to match Claude's project directory naming
  const projectKey = cwd.replace(/[^a-zA-Z0-9]/g, '-').replace(/-+/g, '-');

  // Try to find matching project directory
  let phaseState = null;
  if (fs.existsSync(projectsDir)) {
    const dirs = fs.readdirSync(projectsDir);
    for (const dir of dirs) {
      if (projectKey.includes(dir) || dir.includes(projectKey.slice(0, 20))) {
        const phaseFile = path.join(projectsDir, dir, 'phase-state.json');
        if (fs.existsSync(phaseFile)) {
          try {
            phaseState = JSON.parse(fs.readFileSync(phaseFile, 'utf8'));
          } catch {}
        }
        break;
      }
    }
  }

  const contextLines = [];

  // Collect instinct context for Claude
  if (instinctLines.length > 0) {
    contextLines.push(...instinctLines);
  }

  // Collect phase context for Claude
  if (phaseState && phaseState.current_phase && phaseState.current_phase !== 'idle') {
    contextLines.push(`[系统] 当前阶段：${phaseState.current_phase}`);
    contextLines.push(`[系统] 请执行：Skill(skill: "${phaseState.current_phase}")`);
    if (phaseState.task_ref) {
      contextLines.push(`[系统] 任务引用：${phaseState.task_ref}`);
    }
  }

  // Output to stdout so Claude receives it as context
  if (contextLines.length > 0) {
    console.log(contextLines.join('\n'));
  }

  // Detect and report package manager (stderr only, not needed in Claude context)
  const pm = getPackageManager();
  log(`[SessionStart] Package manager: ${pm.name} (${pm.source})`);

  if (pm.source === 'fallback' || pm.source === 'default') {
    log('[SessionStart] No package manager preference found.');
    log(getSelectionPrompt());
  }

  process.exit(0);
}

main().catch(err => {
  console.error('[SessionStart] Error:', err.message);
  process.exit(0); // Don't block on errors
});
