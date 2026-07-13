#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

const ROOT = process.cwd();
const OUT = path.join(ROOT, "docs", "status", "continuity-spine.json");

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function writeJson(filePath, payload) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
}

function findFiles(dir, predicate, result = []) {
  if (!fs.existsSync(dir)) return result;
  for (const name of fs.readdirSync(dir).sort()) {
    const fullPath = path.join(dir, name);
    const stat = fs.statSync(fullPath);
    if (stat.isDirectory()) {
      findFiles(fullPath, predicate, result);
    } else if (predicate(fullPath)) {
      result.push(path.relative(ROOT, fullPath).split(path.sep).join("/"));
    }
  }
  return result;
}

function fallbackSurface() {
  const continuityFiles = findFiles(
    path.join(ROOT, "out"),
    (filePath) => filePath.includes("temporal_continuity") || filePath.includes("continuity")
  );
  const lanes = continuityFiles.map((evidencePath, index) => ({
    lane_id: `P${index}`,
    sequence_index: index + 1,
    evidence_count: 1,
    status: "OBSERVED",
    evidence_paths: [evidencePath],
  }));
  return {
    schema_version: "continuity_spine_surface.v1",
    generated_by: "scripts/continuity-spine.js",
    mock_data: false,
    deterministic: true,
    lane_count: lanes.length,
    highest_lane: lanes.length ? lanes[lanes.length - 1].lane_id : "NOT_COMPUTABLE",
    continuity_lanes: lanes,
  };
}

const existing = fs.existsSync(OUT) ? readJson(OUT) : fallbackSurface();
existing.schema_version = existing.schema_version || "continuity_spine_surface.v1";
existing.generated_by = "scripts/continuity-spine.js";
existing.mock_data = false;
existing.deterministic = true;
existing.continuity_lanes = existing.continuity_lanes || [];
existing.lane_count = existing.continuity_lanes.length;
existing.highest_lane =
  existing.highest_lane ||
  (existing.continuity_lanes.length
    ? existing.continuity_lanes[existing.continuity_lanes.length - 1].lane_id
    : "NOT_COMPUTABLE");

writeJson(OUT, existing);
