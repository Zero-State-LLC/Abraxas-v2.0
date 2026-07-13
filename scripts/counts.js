#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

const ROOT = process.cwd();
const STATUS_DIR = path.join(ROOT, "docs", "status");
const BADGE_DIR = path.join(STATUS_DIR, "badges");

function readJson(filePath, fallback = {}) {
  if (!fs.existsSync(filePath)) return fallback;
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function writeJson(filePath, payload) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
}

function countFiles(dir, predicate = () => true) {
  if (!fs.existsSync(dir)) return 0;
  let count = 0;
  for (const name of fs.readdirSync(dir).sort()) {
    const fullPath = path.join(dir, name);
    const stat = fs.statSync(fullPath);
    if (stat.isDirectory()) {
      count += countFiles(fullPath, predicate);
    } else if (predicate(fullPath)) {
      count += 1;
    }
  }
  return count;
}

function badge(label, message, color) {
  return {
    schemaVersion: 1,
    label,
    message: String(message),
    color,
    cacheSeconds: 300,
  };
}

function existingBadgeMessage(name, fallback) {
  const payload = readJson(path.join(BADGE_DIR, `${name}.json`));
  return payload.message || fallback;
}

const existing = readJson(path.join(STATUS_DIR, "badges.json"));
const continuity = readJson(path.join(STATUS_DIR, "continuity-spine.json"), {
  lane_count: 0,
});

const signals = {
  build_status: existing.signals?.build_status || "NOT_COMPUTABLE",
  test_status: existing.signals?.test_status || "NOT_COMPUTABLE",
  coverage_status: existing.signals?.coverage_status || "NOT_COMPUTABLE",
  contract_count: existing.signals?.contract_count || countFiles(path.join(ROOT, "out", "contracts")),
  schema_count:
    existing.signals?.schema_count ||
    countFiles(path.join(ROOT, "contracts"), (filePath) => filePath.endsWith(".schema.json")),
  rune_count: existing.signals?.rune_count || countFiles(path.join(ROOT, "runes")),
  continuity_lane_count: continuity.lane_count || 0,
  governance_status: existing.signals?.governance_status || "ACTIVE",
  canon_status: existing.signals?.canon_status || "ADVISORY_ONLY",
};

const liveStatus = {
  current_version: existing.live_status?.current_version || "2.5.0",
  observed_contracts: signals.contract_count,
  observed_schemas: signals.schema_count,
  observed_tests: existing.live_status?.observed_tests || countFiles(path.join(ROOT, "tests")),
  observed_artifacts: existing.live_status?.observed_artifacts || countFiles(path.join(ROOT, "out")),
  observed_runes: signals.rune_count,
  observed_continuity_lanes: signals.continuity_lane_count,
  last_scan_time: "NOT_COMPUTABLE",
  last_observed_commit_time: "NOT_COMPUTABLE",
};

writeJson(path.join(STATUS_DIR, "badges.json"), {
  schema_version: "repo_status_surface.v1",
  generated_by: "scripts/counts.js",
  mock_data: false,
  deterministic: true,
  signals,
  live_status: liveStatus,
  note:
    "All repository signal values are generated from local repository scans and should be treated as observational rather than authoritative.",
});

const badgePayloads = {
  build: badge("build", existingBadgeMessage("build", signals.build_status), "9f9f9f"),
  canon: badge("canon", existingBadgeMessage("canon", signals.canon_status), "2ea043"),
  continuity: badge("continuity_lanes", signals.continuity_lane_count, "b18b2a"),
  contracts: badge("contracts", signals.contract_count, "4f46e5"),
  coverage: badge("coverage", existingBadgeMessage("coverage", signals.coverage_status), "9f9f9f"),
  governance: badge(
    "governance",
    existingBadgeMessage("governance", signals.governance_status),
    "2ea043"
  ),
  runes: badge("runes", signals.rune_count, "0891b2"),
  schemas: badge("schemas", signals.schema_count, "4f46e5"),
  tests: badge("tests", liveStatus.observed_tests, "0891b2"),
};

for (const [name, payload] of Object.entries(badgePayloads)) {
  writeJson(path.join(BADGE_DIR, `${name}.json`), payload);
}
