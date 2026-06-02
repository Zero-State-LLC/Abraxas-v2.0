#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const repoRoot = path.resolve(__dirname, '..');
const outputPath = path.join(repoRoot, 'docs', 'status', 'continuity-spine.json');
const plansDir = path.join(repoRoot, 'docs', 'plans');
const outDir = path.join(repoRoot, 'out');

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
        stack.push(path.join(current, entry));
      }
    } else if (stat.isFile()) {
      out.push(current);
    }
  }
  return out.sort();
}

function parseLaneId(raw) {
  const normalized = raw.toUpperCase();
  const match = normalized.match(/^P(\d+)([A-Z]?)$/);
  if (!match) return null;
  return {
    lane_id: `P${match[1]}${match[2]}`,
    number: Number(match[1]),
    suffix: match[2] || '',
  };
}

function laneSort(a, b) {
  if (a.number !== b.number) return a.number - b.number;
  return a.suffix.localeCompare(b.suffix);
}

const laneEvidence = new Map();

for (const file of walkFiles(plansDir)) {
  const name = path.basename(file);
  const match = name.match(/^(P\d+[A-Z]?)_/i);
  if (!match) continue;
  const parsed = parseLaneId(match[1]);
  if (!parsed) continue;
  if (!laneEvidence.has(parsed.lane_id)) laneEvidence.set(parsed.lane_id, new Set());
  laneEvidence.get(parsed.lane_id).add(path.relative(repoRoot, file));
}

for (const file of walkFiles(outDir)) {
  const rel = path.relative(repoRoot, file);
  const matches = rel.match(/(?:^|[_\/-])p(\d+[a-z]?)(?=[_\/.\-]|$)/gi) || [];
  for (const m of matches) {
    const raw = m.replace(/^[^p]*p/i, 'P');
    const parsed = parseLaneId(raw);
    if (!parsed) continue;
    if (!laneEvidence.has(parsed.lane_id)) laneEvidence.set(parsed.lane_id, new Set());
    laneEvidence.get(parsed.lane_id).add(rel);
  }
}

const lanes = Array.from(laneEvidence.keys())
  .map((laneId) => {
    const parsed = parseLaneId(laneId);
    return {
      ...parsed,
      evidence_paths: Array.from(laneEvidence.get(laneId)).sort(),
    };
  })
  .filter(Boolean)
  .sort(laneSort)
  .map((lane, index) => ({
    lane_id: lane.lane_id,
    sequence_index: index + 1,
    evidence_count: lane.evidence_paths.length,
    status: 'OBSERVED',
    evidence_paths: lane.evidence_paths,
  }));

const highestLane = lanes.length > 0 ? lanes[lanes.length - 1].lane_id : 'NOT_COMPUTABLE';

const payload = {
  schema_version: 'continuity_spine_surface.v1',
  generated_by: 'Scripts/continuity-spine.js',
  mock_data: false,
  deterministic: true,
  lane_count: lanes.length,
  highest_lane: highestLane,
  continuity_lanes: lanes,
};

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, `${JSON.stringify(payload, null, 2)}\n`, 'utf8');
