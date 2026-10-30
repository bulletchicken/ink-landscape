/* Execute the unmodified drawing functions from Lingdong Huang's pinned source.
 * The browser UI/chunk loader is intentionally not part of this offline adapter.
 * Source and MIT license are preserved in ../vendor/.
 */
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const crypto = require('crypto');

const source = fs.readFileSync(path.join(__dirname, '../vendor/index.html'), 'utf8');
const blocks = [...source.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)].map(m => ({attrs:m[1],code:m[2]}));
function hashSeed(value) {
  return crypto.createHash('sha256').update(String(value)).digest().readUInt32LE(0);
}
function createEngine() {
  const ctx = vm.createContext({
    console: {log() {},warn() {},error() {}},
    window: {btoa: value => Buffer.from(value, 'binary').toString('base64')},
  });
  for (const id of ['PRNG','PerlinNoise','PolyTools','Util']) {
    const block = blocks.find(b => b.attrs.includes(`id="${id}"`));
    if (!block) throw new Error(`Missing original source block ${id}`);
    vm.runInContext(block.code, ctx, {filename:`LingDong/index.html#${id}`});
  }
  const drawing = blocks.find(b => b.code.includes('function stroke(ptlist, args)'));
  const boundary = drawing.code.indexOf('  function mountplanner(');
  if (boundary < 0) throw new Error('Original drawing/UI boundary changed');
  vm.runInContext(drawing.code.slice(0,boundary),ctx,{filename:'LingDong/index.html#drawing-functions'});
  const api = vm.runInContext('({Prng, Noise, Tree, Mount, Arch, Man, water, stroke, poly, texture, seed:Math.seed})',ctx);
  api.reset = value => {
    const seed = hashSeed(value);
    api.seed(seed);
    api.Noise.noiseSeed(seed);
    return seed;
  };
  return api;
}
module.exports = {createEngine,hashSeed};
