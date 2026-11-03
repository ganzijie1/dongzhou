(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.DongzhouPcgrlRuntime = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const WIDTH = 19;
  const HEIGHT = 14;
  const CELL_COUNT = WIDTH * HEIGHT;
  const TILE_CHARS = ["f", "F", "r", "~"];
  const CHAR_TILES = Object.fromEntries(TILE_CHARS.map((char, index) => [char, index]));
  const COMPATIBLE = [0b1111, 0b1111, 0b0111, 0b1011];
  const TARGET_RATIOS = { easy: 0.12, medium: 0.19, hard: 0.26 };
  const GEOMETRY_LIMITS = Object.freeze({ transitionRatio: 0.60, patchDensity: 0.32, articulationRatio: 0.08 });
  const SPAWNS = [
    [2, 6], [3, 4], [3, 6], [3, 8], [4, 3], [4, 9], [5, 5],
    [16, 6], [15, 5], [15, 7], [14, 4], [14, 8], [13, 6]
  ];

  function pointKey(x, y) { return `${x},${y}`; }

  function protectedCells() {
    const cells = new Set();
    for (const [x, y] of SPAWNS) {
      cells.add(pointKey(x, y));
      for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const nx = x + dx; const ny = y + dy;
        if (nx >= 0 && nx < WIDTH && ny >= 0 && ny < HEIGHT) cells.add(pointKey(nx, ny));
      }
    }
    for (let x = 2; x < WIDTH - 2; x++) cells.add(pointKey(x, Math.floor(HEIGHT / 2)));
    return cells;
  }

  const PROTECTED = protectedCells();

  function seededRandom(seed) {
    let value = seed >>> 0;
    return function () {
      value = (value + 0x6D2B79F5) >>> 0;
      let result = value;
      result = Math.imul(result ^ (result >>> 15), result | 1);
      result ^= result + Math.imul(result ^ (result >>> 7), result | 61);
      return ((result ^ (result >>> 14)) >>> 0) / 4294967296;
    };
  }

  function bitCount(mask) {
    let count = 0;
    while (mask) { mask &= mask - 1; count++; }
    return count;
  }

  function entropy(mask, weights) {
    let sum = 0; let weightedLog = 0;
    for (let tile = 0; tile < 4; tile++) {
      if (!(mask & (1 << tile))) continue;
      const weight = Math.max(1e-6, weights[tile]);
      sum += weight;
      weightedLog += weight * Math.log(weight);
    }
    return sum <= 0 ? Infinity : Math.log(sum) - weightedLog / sum;
  }

  function cellWeights(predicted, difficulty, index) {
    const ratio = TARGET_RATIOS[difficulty] ?? TARGET_RATIOS.medium;
    const weights = [(1 - ratio) * 1.15, (1 - ratio) * 0.85, ratio, ratio * 0.85];
    const preferred = Number(predicted[index]);
    if (preferred >= 0 && preferred < 4) weights[preferred] *= 6;
    return weights;
  }

  function allowedByNeighbor(neighborMask) {
    let allowed = 0;
    for (let tile = 0; tile < 4; tile++) {
      if (neighborMask & (1 << tile)) allowed |= COMPATIBLE[tile];
    }
    return allowed;
  }

  function propagate(domains, queue) {
    while (queue.length) {
      const index = queue.shift();
      const x = index % WIDTH; const y = Math.floor(index / WIDTH);
      for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const nx = x + dx; const ny = y + dy;
        if (nx < 0 || nx >= WIDTH || ny < 0 || ny >= HEIGHT) continue;
        const neighbor = ny * WIDTH + nx;
        const revised = domains[neighbor] & allowedByNeighbor(domains[index]);
        if (!revised) return false;
        if (revised !== domains[neighbor]) { domains[neighbor] = revised; queue.push(neighbor); }
      }
    }
    return true;
  }

  function weightedChoice(mask, weights, random) {
    let total = 0;
    for (let tile = 0; tile < 4; tile++) if (mask & (1 << tile)) total += weights[tile];
    let roll = random() * total;
    for (let tile = 0; tile < 4; tile++) {
      if (!(mask & (1 << tile))) continue;
      roll -= weights[tile];
      if (roll <= 0) return tile;
    }
    return 0;
  }

  function wfcRefine(predictedTiles, difficulty = "medium", seed = 1) {
    if (!Array.isArray(predictedTiles) || predictedTiles.length !== CELL_COUNT) {
      return { ok: false, reason: "invalid-policy-output", tiles: null, contradictions: 0, attempts: 0 };
    }
    for (let attempt = 0; attempt < 3; attempt++) {
      const random = seededRandom((seed + attempt * 0x9E3779B9) >>> 0);
      const domains = Array(CELL_COUNT).fill(0b1111);
      const initialQueue = [];
      for (const key of PROTECTED) {
        const [x, y] = key.split(",").map(Number);
        const index = y * WIDTH + x;
        domains[index] = 0b0011;
        initialQueue.push(index);
      }
      if (!propagate(domains, initialQueue)) continue;
      let contradiction = false;
      for (;;) {
        let selected = -1; let selectedEntropy = Infinity;
        for (let index = 0; index < CELL_COUNT; index++) {
          if (bitCount(domains[index]) <= 1) continue;
          const score = entropy(domains[index], cellWeights(predictedTiles, difficulty, index)) + random() * 1e-7;
          if (score < selectedEntropy) { selectedEntropy = score; selected = index; }
        }
        if (selected < 0) break;
        const tile = weightedChoice(domains[selected], cellWeights(predictedTiles, difficulty, selected), random);
        domains[selected] = 1 << tile;
        if (!propagate(domains, [selected])) { contradiction = true; break; }
      }
      if (!contradiction) {
        return { ok: true, tiles: domains.map((mask) => Math.log2(mask) | 0), contradictions: attempt, attempts: attempt + 1 };
      }
    }
    return { ok: false, reason: "wfc-contradiction", tiles: null, contradictions: 3, attempts: 3 };
  }

  function neighbors(index) {
    const x = index % WIDTH; const y = Math.floor(index / WIDTH); const result = [];
    for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
      const nx = x + dx; const ny = y + dy;
      if (nx >= 0 && nx < WIDTH && ny >= 0 && ny < HEIGHT) result.push(ny * WIDTH + nx);
    }
    return result;
  }

  function reachable(tiles, start) {
    const startIndex = start[1] * WIDTH + start[0];
    if (tiles[startIndex] >= 2) return new Set();
    const seen = new Set([startIndex]); const queue = [startIndex];
    while (queue.length) {
      const index = queue.shift();
      for (const next of neighbors(index)) {
        if (tiles[next] >= 2 || seen.has(next)) continue;
        seen.add(next); queue.push(next);
      }
    }
    return seen;
  }

  function distanceMap(tiles, start) {
    const startIndex = start[1] * WIDTH + start[0];
    if (tiles[startIndex] >= 2) return new Map();
    const distances = new Map([[startIndex, 0]]); const queue = [startIndex];
    while (queue.length) {
      const index = queue.shift();
      for (const next of neighbors(index)) {
        if (tiles[next] >= 2 || distances.has(next)) continue;
        distances.set(next, distances.get(index) + 1); queue.push(next);
      }
    }
    return distances;
  }

  function tacticalProxy(tiles) {
    if (!Array.isArray(tiles) || tiles.length !== CELL_COUNT) return { valid: false, reason: "invalid-tiles" };
    const own = SPAWNS.slice(0, 7); const enemy = SPAWNS.slice(7);
    const nearestAverage = (sources, targets) => {
      const values = sources.map((source) => {
        const distances = distanceMap(tiles, source);
        return Math.min(...targets.map(([x, y]) => distances.get(y * WIDTH + x) ?? Infinity));
      });
      return values.every(Number.isFinite) ? values.reduce((sum, value) => sum + value, 0) / values.length : Infinity;
    };
    const ownEngagement = nearestAverage(own, enemy);
    const enemyEngagement = nearestAverage(enemy, own);
    const balanceDelta = Math.abs(ownEngagement - enemyEngagement);
    const centerCrossings = Array.from({ length: HEIGHT }, (_, y) => y * WIDTH + Math.floor(WIDTH / 2))
      .filter((index) => tiles[index] < 2).length;
    const spawnFreedom = SPAWNS.map(([x, y]) => neighbors(y * WIDTH + x).filter((index) => tiles[index] < 2).length);
    const minSpawnFreedom = Math.min(...spawnFreedom);
    const valid = Number.isFinite(balanceDelta) && balanceDelta <= 3 && centerCrossings >= 3 && minSpawnFreedom >= 2;
    return { valid, ownEngagement, enemyEngagement, balanceDelta, centerCrossings, minSpawnFreedom };
  }

  function geometryProxy(tiles) {
    if (!Array.isArray(tiles) || tiles.length !== CELL_COUNT) return { valid: false, reason: "invalid-tiles" };
    let transitions = 0; let comparedEdges = 0; let patches = 0;
    const patchVisited = new Set();
    for (let index = 0; index < CELL_COUNT; index++) {
      const x = index % WIDTH; const y = Math.floor(index / WIDTH);
      for (const [dx, dy] of [[1, 0], [0, 1]]) {
        const nx = x + dx; const ny = y + dy;
        if (nx >= WIDTH || ny >= HEIGHT) continue;
        comparedEdges++;
        if (tiles[index] !== tiles[ny * WIDTH + nx]) transitions++;
      }
      if (patchVisited.has(index)) continue;
      patches++;
      patchVisited.add(index);
      const queue = [index];
      for (let cursor = 0; cursor < queue.length; cursor++) {
        for (const next of neighbors(queue[cursor])) {
          if (patchVisited.has(next) || tiles[next] !== tiles[index]) continue;
          patchVisited.add(next);
          queue.push(next);
        }
      }
    }

    const passable = new Set(Array.from({ length: CELL_COUNT }, (_, index) => index).filter((index) => tiles[index] < 2));
    const discovery = new Map(); const low = new Map(); const parent = new Map(); const articulation = new Set();
    let time = 0;
    function visit(node) {
      discovery.set(node, ++time);
      low.set(node, discovery.get(node));
      let children = 0;
      for (const next of neighbors(node).filter((index) => passable.has(index))) {
        if (!discovery.has(next)) {
          parent.set(next, node);
          children++;
          visit(next);
          low.set(node, Math.min(low.get(node), low.get(next)));
          if (!parent.has(node) && children > 1) articulation.add(node);
          if (parent.has(node) && low.get(next) >= discovery.get(node)) articulation.add(node);
        } else if (parent.get(node) !== next) low.set(node, Math.min(low.get(node), discovery.get(next)));
      }
    }
    for (const node of passable) if (!discovery.has(node)) visit(node);
    return {
      valid: true,
      transitionRatio: transitions / Math.max(1, comparedEdges),
      patchDensity: patches / CELL_COUNT,
      articulationPoints: articulation.size,
      articulationRatio: articulation.size / Math.max(1, passable.size),
      articulationCells: [...articulation]
    };
  }

  function smoothLabels(tiles, changed, limit) {
    for (let pass = 0; pass < 4 && changed.size < limit; pass++) {
      let passChanges = 0;
      for (let index = 0; index < CELL_COUNT && changed.size < limit; index++) {
        const x = index % WIDTH; const y = Math.floor(index / WIDTH);
        if (PROTECTED.has(pointKey(x, y))) continue;
        const blocked = tiles[index] >= 2;
        const votes = new Map();
        for (const next of neighbors(index)) {
          if ((tiles[next] >= 2) !== blocked) continue;
          votes.set(tiles[next], (votes.get(tiles[next]) || 0) + 1);
        }
        const preferred = [...votes.entries()].sort((left, right) => right[1] - left[1] || left[0] - right[0])[0];
        if (!preferred || preferred[1] < 2 || preferred[0] === tiles[index]) continue;
        tiles[index] = preferred[0];
        changed.add(index);
        passChanges++;
      }
      if (!passChanges) break;
    }
  }

  function openBottleneckBypasses(tiles, changed, limit, targetRatio = 0.08) {
    for (let pass = 0; pass < 3 && changed.size < limit; pass++) {
      const geometry = geometryProxy(tiles);
      if (geometry.articulationRatio <= targetRatio) break;
      let opened = 0;
      for (const articulation of geometry.articulationCells) {
        const candidates = neighbors(articulation).filter((index) => {
          const x = index % WIDTH; const y = Math.floor(index / WIDTH);
          return tiles[index] >= 2 && !PROTECTED.has(pointKey(x, y));
        }).map((index) => ({
          index,
          passableNeighbors: neighbors(index).filter((next) => tiles[next] < 2).length
        })).filter((entry) => entry.passableNeighbors >= 2)
          .sort((left, right) => right.passableNeighbors - left.passableNeighbors || left.index - right.index);
        if (!candidates.length) continue;
        tiles[candidates[0].index] = 0;
        changed.add(candidates[0].index);
        opened++;
        if (changed.size >= limit || opened >= 12) break;
      }
      if (!opened) break;
    }
  }

  function validate(tiles, difficulty = "medium") {
    if (!Array.isArray(tiles) || tiles.length !== CELL_COUNT || tiles.some((tile) => !Number.isInteger(tile) || tile < 0 || tile > 3)) {
      return { valid: false, reason: "invalid-tiles" };
    }
    const seen = reachable(tiles, SPAWNS[0]);
    const connected = SPAWNS.every(([x, y]) => seen.has(y * WIDTH + x));
    const spawnClear = [...PROTECTED].every((key) => {
      const [x, y] = key.split(",").map(Number);
      return tiles[y * WIDTH + x] < 2;
    });
    const blockedRatio = tiles.filter((tile) => tile >= 2).length / CELL_COUNT;
    const targetRatio = TARGET_RATIOS[difficulty] ?? TARGET_RATIOS.medium;
    let incompatibleEdges = 0;
    for (let index = 0; index < CELL_COUNT; index++) {
      const x = index % WIDTH; const y = Math.floor(index / WIDTH);
      for (const [dx, dy] of [[1, 0], [0, 1]]) {
        const nx = x + dx; const ny = y + dy;
        if (nx >= WIDTH || ny >= HEIGHT) continue;
        if (new Set([tiles[index], tiles[ny * WIDTH + nx]]).size === 2 && tiles[index] + tiles[ny * WIDTH + nx] === 5) incompatibleEdges++;
      }
    }
    const ratioOk = Math.abs(blockedRatio - targetRatio) <= 0.10;
    const proxy = tacticalProxy(tiles);
    const geometry = geometryProxy(tiles);
    const geometryOk = geometry.valid
      && geometry.transitionRatio <= GEOMETRY_LIMITS.transitionRatio
      && geometry.patchDensity <= GEOMETRY_LIMITS.patchDensity
      && geometry.articulationRatio <= GEOMETRY_LIMITS.articulationRatio;
    return { valid: connected && spawnClear && ratioOk && incompatibleEdges === 0 && proxy.valid && geometryOk, connected, spawnClear, ratioOk, blockedRatio, targetRatio, incompatibleEdges, proxy, geometry, geometryOk };
  }

  function carvePath(tiles, from, to, changed, limit) {
    let [x, y] = from;
    while ((x !== to[0] || y !== to[1]) && changed.size < limit) {
      const index = y * WIDTH + x;
      if (tiles[index] >= 2) { tiles[index] = 0; changed.add(index); }
      if (x !== to[0]) x += Math.sign(to[0] - x);
      else if (y !== to[1]) y += Math.sign(to[1] - y);
    }
    const index = y * WIDTH + x;
    if (tiles[index] >= 2 && changed.size < limit) { tiles[index] = 0; changed.add(index); }
  }

  function repair(tiles, difficulty = "medium", seed = 1, limit = 64) {
    const output = tiles.slice(); const changed = new Set();
    for (const key of PROTECTED) {
      const [x, y] = key.split(",").map(Number); const index = y * WIDTH + x;
      if (output[index] >= 2 && changed.size < limit) { output[index] = 0; changed.add(index); }
    }
    for (const spawn of SPAWNS.slice(1)) carvePath(output, spawn, SPAWNS[0], changed, limit);
    const random = seededRandom((seed ^ 0xA5A5A5A5) >>> 0);
    const targetBlocked = Math.round((TARGET_RATIOS[difficulty] ?? TARGET_RATIOS.medium) * CELL_COUNT);
    let blocked = output.filter((tile) => tile >= 2).length;
    const candidates = Array.from({ length: CELL_COUNT }, (_, index) => ({
      index,
      affinity: neighbors(index).filter((next) => output[next] >= 2).length,
      tie: random()
    })).sort((left, right) => blocked < targetBlocked
      ? right.affinity - left.affinity || left.tie - right.tie
      : left.affinity - right.affinity || left.tie - right.tie);
    for (const candidate of candidates) {
      const index = candidate.index;
      if (changed.size >= limit || blocked === targetBlocked) break;
      const x = index % WIDTH; const y = Math.floor(index / WIDTH);
      if (PROTECTED.has(pointKey(x, y))) continue;
      if (blocked < targetBlocked && output[index] < 2) { output[index] = 2; blocked++; changed.add(index); }
      else if (blocked > targetBlocked && output[index] >= 2) { output[index] = 0; blocked--; changed.add(index); }
    }
    // A single blocked type after repair guarantees the WFC hill/water adjacency rule.
    for (let index = 0; index < CELL_COUNT; index++) if (output[index] === 3) output[index] = 2;
    openBottleneckBypasses(output, changed, limit);
    smoothLabels(output, changed, limit);
    return { tiles: output, repairs: changed.size, validation: validate(output, difficulty) };
  }

  function rowsToTiles(rows) {
    if (!Array.isArray(rows) || rows.length !== HEIGHT || rows.some((row) => [...row].length !== WIDTH)) return null;
    return rows.flatMap((row) => [...row].map((char) => CHAR_TILES[char] ?? 0));
  }

  function tilesToRows(tiles) {
    const rows = [];
    for (let y = 0; y < HEIGHT; y++) rows.push(tiles.slice(y * WIDTH, (y + 1) * WIDTH).map((tile) => TILE_CHARS[tile] || "f").join(""));
    return rows;
  }

  function generate(rawTiles, fallbackRows, difficulty = "medium", seed = 1) {
    const fallback = rowsToTiles(fallbackRows);
    if (!fallback) throw new Error("invalid PCGRL fallback template");
    if (!Array.isArray(rawTiles) || rawTiles.length !== CELL_COUNT) {
      const fallbackValidation = validate(fallback, difficulty);
      return { rows: fallbackRows.slice(), meta: { source: "template-fallback", fallback: true, reason: "policy-unavailable", validation: fallbackValidation, repairs: 0, wfc: null } };
    }
    const wfc = wfcRefine(rawTiles.map(Number), difficulty, seed);
    if (!wfc.ok) {
      return { rows: fallbackRows.slice(), meta: { source: "template-fallback", fallback: true, reason: wfc.reason, validation: validate(fallback, difficulty), repairs: 0, wfc } };
    }
    const repaired = repair(wfc.tiles, difficulty, seed);
    if (!repaired.validation.valid) {
      return { rows: fallbackRows.slice(), meta: { source: "template-fallback", fallback: true, reason: "hard-validation-failed", validation: validate(fallback, difficulty), repairs: repaired.repairs, wfc } };
    }
    return { rows: tilesToRows(repaired.tiles), meta: { source: "pcgrl+wfc", fallback: false, validation: repaired.validation, repairs: repaired.repairs, wfc } };
  }

  return { WIDTH, HEIGHT, CELL_COUNT, SPAWNS, TARGET_RATIOS, GEOMETRY_LIMITS, wfcRefine, validate, tacticalProxy, geometryProxy, repair, rowsToTiles, tilesToRows, generate };
});
