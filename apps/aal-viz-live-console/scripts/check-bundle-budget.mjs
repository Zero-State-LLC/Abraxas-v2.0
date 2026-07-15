import { readFileSync, statSync } from 'node:fs';
import { gzipSync } from 'node:zlib';

const BUDGET_BYTES = 512000;
const manifest = JSON.parse(readFileSync('dist/.vite/manifest.json', 'utf8'));
const entries = Object.entries(manifest).filter(([, value]) => value.isEntry === true);
if (entries.length !== 1) throw new Error(`Expected one Vite entry, found ${entries.length}`);

const visited = new Set();
function collectStatic(key) {
  if (visited.has(key)) return;
  visited.add(key);
  const record = manifest[key];
  if (record == null) throw new Error(`Manifest import is missing: ${key}`);
  for (const dependency of record.imports ?? []) collectStatic(dependency);
}

collectStatic(entries[0][0]);
const initialFiles = [...visited].map((key) => manifest[key].file).filter((file) => file.endsWith('.js'));
const initialBytes = initialFiles.reduce((total, file) => total + statSync(`dist/${file}`).size, 0);
const initialGzipBytes = initialFiles.reduce(
  (total, file) => total + gzipSync(readFileSync(`dist/${file}`)).byteLength,
  0,
);
const asyncChunks = Object.values(manifest)
  .filter((record) => record.file?.endsWith('.js') && !initialFiles.includes(record.file))
  .map((record) => ({ file: record.file, bytes: statSync(`dist/${record.file}`).size }))
  .sort((left, right) => right.bytes - left.bytes);

console.log(JSON.stringify({ budget_bytes: BUDGET_BYTES, initial_bytes: initialBytes, initial_gzip_bytes: initialGzipBytes, initial_files: initialFiles, async_chunks: asyncChunks }, null, 2));
if (initialBytes > BUDGET_BYTES) {
  throw new Error(`Initial JavaScript ${initialBytes} bytes exceeds ${BUDGET_BYTES}-byte budget`);
}
