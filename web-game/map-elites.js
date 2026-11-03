(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.DongzhouMapElitesRuntime = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const WIDTH = 19;
  const HEIGHT = 14;
  const RIVER_ROWS = [6, 7];
  const PASSABLE = new Set(["f", "g", "F", "w", "m", "v"]);
  const SPAWNS = [[2, 2], [3, 3], [4, 2], [5, 3], [6, 2], [7, 3], [16, 11], [15, 10], [14, 11], [13, 10], [12, 11], [11, 10]];

  function reachable(rows, start) {
    const seen = new Set([`${start[0]},${start[1]}`]);
    const queue = [start];
    while (queue.length) {
      const [x, y] = queue.shift();
      for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const nx = x + dx; const ny = y + dy; const key = `${nx},${ny}`;
        if (nx < 0 || nx >= WIDTH || ny < 0 || ny >= HEIGHT || seen.has(key) || !PASSABLE.has(rows[ny]?.[nx])) continue;
        seen.add(key); queue.push([nx, ny]);
      }
    }
    return seen;
  }

  function validate(entry) {
    const rows = entry?.rows;
    if (!Array.isArray(rows) || rows.length !== HEIGHT || rows.some((row) => [...row].length !== WIDTH)) return { valid: false, reason: "invalid-size" };
    const seen = reachable(rows, SPAWNS[0]);
    const spawnsReachable = SPAWNS.every(([x, y]) => seen.has(`${x},${y}`));
    let routes = 0; let inRoute = false;
    for (let x = 0; x < WIDTH; x++) {
      const shallow = RIVER_ROWS.every((y) => rows[y][x] === "v");
      if (shallow && !inRoute) routes++;
      inRoute = shallow;
    }
    const riverSemantics = RIVER_ROWS.every((y) => [...rows[y]].every((char) => char === "~" || char === "v"));
    return { valid: spawnsReachable && riverSemantics && routes === Number(entry.routeCount), spawnsReachable, riverSemantics, routeCount: routes, reachableCells: seen.size };
  }

  function selectElite(archive, difficulty = "medium", seed = 1) {
    const entries = Array.isArray(archive?.entries) ? archive.entries : [];
    const allowedDefense = { easy: [0, 1], medium: [2, 3], hard: [4] }[difficulty] || [2, 3];
    let candidates = entries.filter((entry) => allowedDefense.includes(Number(entry.cell?.[1])));
    if (!candidates.length) candidates = entries;
    const desiredRoute = Math.abs(Number(seed) || 1) % 5;
    const exact = candidates.filter((entry) => Number(entry.cell?.[0]) === desiredRoute);
    if (exact.length) candidates = exact;
    if (!candidates.length) throw new Error("MAP-Elites archive is empty");
    const entry = candidates[Math.abs((Number(seed) || 1) >>> 5) % candidates.length];
    const validation = validate(entry);
    if (!validation.valid) throw new Error(`MAP-Elites elite failed hard validation: ${validation.reason || "contract"}`);
    return {
      rows: entry.rows.slice(),
      meta: {
        source: "constrained-map-elites",
        fallback: false,
        archiveCell: entry.cell.slice(),
        routeCount: Number(entry.routeCount),
        defenseAdvantage: Number(entry.defenseAdvantage),
        quality: Number(entry.quality),
        repairs: Number(entry.metrics?.repair_count || 0),
        validation
      }
    };
  }

  return { WIDTH, HEIGHT, RIVER_ROWS, SPAWNS, validate, selectElite };
});
