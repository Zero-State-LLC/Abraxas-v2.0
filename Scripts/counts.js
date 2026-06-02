#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const repoRoot = path.resolve(__dirname, '..');
const statusDir = path.join(repoRoot, 'docs', 'status');
const badgesDir = path.join(statusDir, 'badges');
const continuityPath = path.join(statusDir, 'continuity-spine.json');

const IGNORED_DIRS = new Set(['.git', '.venv', '.mypy_cache', '.pytest_cache', '.ruff_cache', '__pycache__']);

function walkFiles(start) {
  if (!fs.existsSync(start)) return [];
  const out = [];
  const stack = [start];
  while (stack.length > 0) {
    const current = stack.pop();
    const stat = fs.statSync(current);
    if (stat.isDirectory()) {
      const entries = fs.readdirSync(current).sort();
      for (const entry of entries.reverse()) {
        if (IGNORED_DIRS.has(entry)) continue;
        stack.push(path.join(current, entry));
      }
    } else if (stat.isFile()) {
      out.push(current);
    }
  }
  return out.sort();
}

function readJsonOrNull(filePath) {
  if (!fs.existsSync(filePath)) return null;
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function countByPredicate(files, predicate) {
  let count = 0;
  for (const file of files) {
    if (predicate(file)) count += 1;
  }
  return count;
}

function readRuneCount() {
  const runeCatalogPath = path.join(repoRoot, 'contracts', 'runes', 'catalog.v1.json');
  const runeCatalog = readJsonOrNull(runeCatalogPath);
  if (!runeCatalog || !Array.isArray(runeCatalog.runes)) {
    return 'NOT_COMPUTABLE';
  }
  return runeCatalog.runes.length;
}

function readContinuityLaneCount() {
  const continuity = readJsonOrNull(continuityPath);
  if (!continuity || !Array.isArray(continuity.continuity_lanes)) {
    return 'NOT_COMPUTABLE';
  }
  return continuity.continuity_lanes.length;
}

function readCanonStatus() {
  const canonStatePath = path.join(repoRoot, 'out', 'canon_resume_state', 'latest.json');
  const canonState = readJsonOrNull(canonStatePath);
  if (!canonState || typeof canonState.canonical_status !== 'string') {
    return 'NOT_COMPUTABLE';
  }
  return canonState.canonical_status;
}

function readGovernanceStatus() {
  const governancePath = path.join(repoRoot, 'out', 'audit', 'governance_freeze_baseline_001.latest.json');
  const governance = readJsonOrNull(governancePath);
  if (!governance || typeof governance.freeze_status !== 'string') {
    return 'NOT_COMPUTABLE';
  }
  return governance.freeze_status;
}

function readVersion() {
  const versionPath = path.join(repoRoot, 'VERSION');
  if (!fs.existsSync(versionPath)) return 'NOT_COMPUTABLE';
  const value = fs.readFileSync(versionPath, 'utf8').trim();
  if (!value) return 'NOT_COMPUTABLE';
  if (value.includes('Your complete updated code here')) return 'NOT_COMPUTABLE';
  return value;
}

function readLastScanTime() {
  try {
    return execSync('git log -1 --format=%cI', { cwd: repoRoot, stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim() || 'NOT_COMPUTABLE';
  } catch {
    return 'NOT_COMPUTABLE';
  }
}

function toBadgeEndpoint(label, message, color) {
  return {
    schemaVersion: 1,
    label,
    message: String(message),
    color,
    cacheSeconds: 300,
  };
}

function writeJson(filePath, data) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, `${JSON.stringify(data, null, 2)}\n`, 'utf8');
}

const allFiles = walkFiles(repoRoot);

const contractCount = countByPredicate(allFiles, (file) => file.startsWith(path.join(repoRoot, 'contracts') + path.sep));
const schemaCount = countByPredicate(allFiles, (file) => file.endsWith('.schema.json'));
const testCount = countByPredicate(allFiles, (file) => file.startsWith(path.join(repoRoot, 'tests') + path.sep) && file.endsWith('.py'));
const artifactCount = countByPredicate(allFiles, (file) => file.startsWith(path.join(repoRoot, 'out') + path.sep));

const continuityLaneCount = readContinuityLaneCount();
const runeCount = readRuneCount();
const governanceStatus = readGovernanceStatus();
const canonStatus = readCanonStatus();
const version = readVersion();
const lastScanTime = readLastScanTime();

const badges = {
  schema_version: 'repo_status_surface.v1',
  generated_by: 'Scripts/counts.js',
  mock_data: false,
  deterministic: true,
  signals: {
    build_status: 'NOT_COMPUTABLE',
    test_status: 'NOT_COMPUTABLE',
    coverage_status: 'NOT_COMPUTABLE',
    contract_count: contractCount,
    schema_count: schemaCount,
    rune_count: runeCount,
    continuity_lane_count: continuityLaneCount,
    governance_status: governanceStatus,
    canon_status: canonStatus,
  },
  live_status: {
    current_version: version,
    observed_contracts: contractCount,
    observed_schemas: schemaCount,
    observed_tests: testCount,
    observed_artifacts: artifactCount,
    observed_runes: runeCount,
    observed_continuity_lanes: continuityLaneCount,
    last_scan_time: lastScanTime,
  },
  note: 'All repository signal values are generated from local repository scans and should be treated as observational rather than authoritative.',
};

writeJson(path.join(statusDir, 'badges.json'), badges);

const endpointPayloads = {
  contracts: toBadgeEndpoint('contracts', contractCount, '4f46e5'),
  schemas: toBadgeEndpoint('schemas', schemaCount, '4f46e5'),
  tests: toBadgeEndpoint('tests', testCount, '0891b2'),
  runes: toBadgeEndpoint('runes', runeCount, '0891b2'),
  continuity: toBadgeEndpoint('continuity_lanes', continuityLaneCount, 'b18b2a'),
  governance: toBadgeEndpoint('governance', governanceStatus, governanceStatus === 'FROZEN' ? '2ea043' : '9f9f9f'),
  canon: toBadgeEndpoint('canon', canonStatus, canonStatus === 'NOT_COMPUTABLE' ? '9f9f9f' : '2ea043'),
  build: toBadgeEndpoint('build', 'NOT_COMPUTABLE', '9f9f9f'),
  coverage: toBadgeEndpoint('coverage', 'NOT_COMPUTABLE', '9f9f9f'),
};

for (const [name, payload] of Object.entries(endpointPayloads)) {
  writeJson(path.join(badgesDir, `${name}.json`), payload);
}
