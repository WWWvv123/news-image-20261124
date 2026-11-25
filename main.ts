// Entry point for the news-image-20261124 bounty entry.
//
// Copies the front-page image (entry.png) into the output directory named
// by MAKEFUN_OUTPUT_DIR, then self-checks the copy: it must exist, be a
// real PNG file, and measure exactly 1024 by 1024 pixels.

import { copyFileSync, existsSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";

const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR;
if (!OUTPUT_DIR) {
  console.error("MAKEFUN_OUTPUT_DIR is not set. Run with e.g.:");
  console.error("  mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts");
  process.exit(1);
}

const SOURCE = new URL("./entry.png", import.meta.url).pathname;
const TARGET = join(OUTPUT_DIR, "entry.png");

if (!existsSync(SOURCE)) {
  console.error(`Source image not found: ${SOURCE}`);
  process.exit(1);
}

copyFileSync(SOURCE, TARGET);

// --- self-check ----------------------------------------------------------
if (!existsSync(TARGET)) {
  console.error(`Output image missing after copy: ${TARGET}`);
  process.exit(1);
}

const bytes = readFileSync(TARGET);
const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (bytes.length < 33 || !bytes.subarray(0, 8).equals(PNG_MAGIC)) {
  console.error("Output is not a valid PNG file.");
  process.exit(1);
}

// In a PNG, the IHDR chunk holds width (bytes 16-19) and height (20-23).
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width !== 1024 || height !== 1024) {
  console.error(`Expected a 1024x1024 image, got ${width}x${height}.`);
  process.exit(1);
}

const size = statSync(TARGET).size;
console.log(`OK: wrote ${TARGET} (${width}x${height}, ${size} bytes).`);
