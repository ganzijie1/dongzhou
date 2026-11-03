"""Constrained MAP-Elites experiment for the 301 BCE Battle of Chuisha.

The historical contract is intentionally narrow: the armies faced each other
across the Bi River, and Kuang Zhang used information about guarded shallow
crossings before a night attack. Terrain outside that contract is a generated
tactical hypothesis, not a historical reconstruction.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


WIDTH = 19
HEIGHT = 14
RIVER_ROWS = (6, 7)
ROUTE_BINS = 5
DEFENSE_BINS = 5
PASSABLE = frozenset("fgFwmv")
OWN_SPAWNS = ((2, 2), (3, 3), (4, 2), (5, 3), (6, 2), (7, 3))
ENEMY_SPAWNS = ((16, 11), (15, 10), (14, 11), (13, 10), (12, 11), (11, 10))
PROTECTED = frozenset(OWN_SPAWNS + ENEMY_SPAWNS)
HISTORICAL_SOURCES = (
    "https://ctext.org/lv-shi-chun-qiu/chu-fang/zh",
    "https://ctext.org/shiji/qin-ben-ji/zh",
)
ALGORITHM_SOURCES = (
    "https://arxiv.org/abs/1504.04909",
    "https://arxiv.org/abs/1907.04053",
    "https://arxiv.org/abs/1806.04718",
)


@dataclass(frozen=True)
class Genome:
    crossings: tuple[tuple[int, int], ...]
    defense: float
    texture_seed: int


@dataclass
class Candidate:
    genome: Genome
    rows: list[str]
    route_count: int
    defense_advantage: float
    descriptor: tuple[int, int]
    quality: float
    metrics: dict[str, float | int | bool | list[float]]


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def normalized_crossings(raw: Iterable[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    accepted: list[tuple[int, int]] = []
    for x, width in sorted(raw):
        width = 1 if width <= 1 else 2
        x = max(2, min(WIDTH - 3 - (width - 1), int(x)))
        cells = set(range(x, x + width))
        if any(cells.intersection(range(ax - 1, ax + aw + 1)) for ax, aw in accepted):
            continue
        accepted.append((x, width))
    return tuple(accepted[:ROUTE_BINS])


def random_genome(rng: random.Random, route_count: int | None = None, defense: float | None = None) -> Genome:
    count = route_count or rng.randint(1, ROUTE_BINS)
    available = list(range(2, WIDTH - 2))
    rng.shuffle(available)
    crossings: list[tuple[int, int]] = []
    for x in available:
        width = 2 if rng.random() < 0.35 else 1
        trial = normalized_crossings((*crossings, (x, width)))
        if len(trial) > len(crossings): crossings = list(trial)
        if len(crossings) >= count: break
    if len(crossings) < count:
        crossings = [(2 + index * 3, 1) for index in range(count)]
    return Genome(normalized_crossings(crossings), clamp(rng.random() if defense is None else defense, 0.0, 0.999), rng.randrange(1, 2**31))


def mutate(genome: Genome, rng: random.Random) -> Genome:
    roll = rng.random()
    crossings = list(genome.crossings)
    defense = genome.defense
    if roll < 0.70:
        if rng.random() < 0.55:
            index = rng.randrange(len(crossings))
            x, width = crossings[index]
            crossings[index] = (x + rng.choice((-2, -1, 1, 2)), width if rng.random() < 0.75 else 3 - width)
            normalized = normalized_crossings(crossings)
            if len(normalized) == len(crossings): crossings = list(normalized)
        else:
            defense = clamp(defense + rng.uniform(-0.16, 0.16), 0.0, 0.999)
    elif roll < 0.90:
        if len(crossings) > 1 and (len(crossings) == ROUTE_BINS or rng.random() < 0.5):
            crossings.pop(rng.randrange(len(crossings)))
        elif len(crossings) < ROUTE_BINS:
            proposal = normalized_crossings((*crossings, (rng.randint(2, WIDTH - 4), rng.choice((1, 1, 2)))))
            if len(proposal) > len(crossings): crossings = list(proposal)
    else:
        return random_genome(rng)
    return Genome(normalized_crossings(crossings), defense, rng.randrange(1, 2**31))


def _noise(seed: int, x: int, y: int) -> float:
    value = (seed ^ (x * 0x45D9F3B) ^ (y * 0x119DE1F3)) & 0xFFFFFFFF
    value = ((value ^ (value >> 16)) * 0x45D9F3B) & 0xFFFFFFFF
    value = ((value ^ (value >> 16)) * 0x45D9F3B) & 0xFFFFFFFF
    return ((value ^ (value >> 16)) & 0xFFFFFFFF) / 0xFFFFFFFF


def build_rows(genome: Genome) -> list[str]:
    grid = [["f" for _ in range(WIDTH)] for _ in range(HEIGHT)]
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if (x, y) in PROTECTED: continue
            value = _noise(genome.texture_seed, x, y)
            if value < 0.07: grid[y][x] = "g"
            elif value > 0.975 and y not in RIVER_ROWS: grid[y][x] = "F"
    for y in RIVER_ROWS:
        for x in range(WIDTH): grid[y][x] = "~"
    for x, width in genome.crossings:
        for y in RIVER_ROWS:
            for dx in range(width): grid[y][x + dx] = "v"

    # Defender-side cover is deliberately clustered around approaches rather
    # than scattered tile noise. Its amount controls the second descriptor.
    target = round(genome.defense * 20)
    sites: list[tuple[float, int, int]] = []
    centers = [x + (width - 1) / 2 for x, width in genome.crossings]
    for y in (8, 9, 10):
        for x in range(1, WIDTH - 1):
            if (x, y) in PROTECTED: continue
            distance = min(abs(x - center) for center in centers)
            if distance <= 3:
                sites.append((distance + _noise(genome.texture_seed ^ 0xA531, x, y), x, y))
    for index, (_, x, y) in enumerate(sorted(sites)[:target]):
        grid[y][x] = "m" if index % 4 == 0 and genome.defense > 0.45 else "F"
    for x, y in PROTECTED: grid[y][x] = "f"
    return ["".join(row) for row in grid]


def _reachable(rows: list[str], starts: Iterable[tuple[int, int]]) -> set[tuple[int, int]]:
    queue = [point for point in starts if rows[point[1]][point[0]] in PASSABLE]
    seen = set(queue)
    while queue:
        x, y = queue.pop(0)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            point = (x + dx, y + dy)
            if not (0 <= point[0] < WIDTH and 0 <= point[1] < HEIGHT) or point in seen: continue
            if rows[point[1]][point[0]] not in PASSABLE: continue
            seen.add(point); queue.append(point)
    return seen


def _route_costs(rows: list[str], crossings: tuple[tuple[int, int], ...]) -> list[float]:
    costs: list[float] = []
    for x, width in crossings:
        center = x + (width - 1) / 2
        approach = 0.0
        for y in (8, 9, 10):
            for px in range(max(0, x - 1), min(WIDTH, x + width + 1)):
                approach += {"F": 1.0, "m": 1.65}.get(rows[y][px], 0.0)
        width_relief = 0.75 if width == 2 else 0.0
        costs.append(abs(center - 4.5) * 0.14 + abs(center - 13.5) * 0.10 + approach - width_relief)
    return costs


def evaluate(genome: Genome) -> Candidate | None:
    if not genome.crossings: return None
    rows = build_rows(genome)
    reachable = _reachable(rows, OWN_SPAWNS[:1])
    hard_valid = all(point in reachable for point in OWN_SPAWNS + ENEMY_SPAWNS)
    if not hard_valid: return None
    actual_routes = 0
    in_route = False
    for x in range(WIDTH):
        shallow = all(rows[y][x] == "v" for y in RIVER_ROWS)
        if shallow and not in_route: actual_routes += 1
        in_route = shallow
    if actual_routes != len(genome.crossings): return None

    defense_cells = sum(rows[y][x] in "Fm" for y in (8, 9, 10) for x in range(WIDTH))
    defense_advantage = clamp(defense_cells / 20.0, 0.0, 0.999)
    defense_bin = min(DEFENSE_BINS - 1, int(defense_advantage * DEFENSE_BINS))
    route_bin = min(ROUTE_BINS - 1, actual_routes - 1)
    centers = [x + (width - 1) / 2 for x, width in genome.crossings]
    if len(centers) == 1:
        spacing = 0.55
    else:
        gaps = [b - a for a, b in zip(centers, centers[1:])]
        ideal = (WIDTH - 5) / len(centers)
        spacing = clamp(1.0 - statistics.pstdev(gaps) / max(1.0, ideal), 0.0, 1.0)
    route_costs = _route_costs(rows, genome.crossings)
    strategy_choices = [
        min(range(len(route_costs)), key=lambda i: route_costs[i]),
        min(range(len(route_costs)), key=lambda i: route_costs[i] + abs(centers[i] - 4.5) * 0.55),
        min(range(len(route_costs)), key=lambda i: route_costs[i] + abs(centers[i] - 9.0) * 0.35),
        min(range(len(route_costs)), key=lambda i: route_costs[i] + abs(centers[i] - 13.5) * 0.55),
    ]
    strategy_diversity = len(set(strategy_choices)) / min(4, len(route_costs))
    shallow_cells = sum(row.count("v") for row in rows)
    readability = clamp(1.0 - (defense_cells + shallow_cells) / (WIDTH * HEIGHT) * 1.45, 0.0, 1.0)
    flank = clamp((max(centers) - min(centers)) / (WIDTH - 5), 0.0, 1.0) if len(centers) > 1 else 0.25
    quality = 0.28 * spacing + 0.27 * strategy_diversity + 0.20 * readability + 0.15 * flank + 0.10
    quality = round(clamp(quality, 0.0, 1.0), 6)
    metrics: dict[str, float | int | bool | list[float]] = {
        "hard_valid": True,
        "reachable_cells": len(reachable),
        "route_spacing": round(spacing, 6),
        "strategy_diversity": round(strategy_diversity, 6),
        "readability": round(readability, 6),
        "flank_span": round(flank, 6),
        "route_costs": [round(value, 4) for value in route_costs],
        "repair_count": 0,
    }
    return Candidate(genome, rows, actual_routes, round(defense_advantage, 6), (route_bin, defense_bin), quality, metrics)


def run_map_elites(seed: int, budget: int, initial: int) -> tuple[dict[tuple[int, int], Candidate], dict[str, int]]:
    rng = random.Random(seed)
    archive: dict[tuple[int, int], Candidate] = {}
    accepted = 0
    invalid = 0
    for iteration in range(budget):
        if iteration < initial or not archive:
            genome = random_genome(rng)
        else:
            genome = mutate(rng.choice(list(archive.values())).genome, rng)
        candidate = evaluate(genome)
        if candidate is None:
            invalid += 1; continue
        accepted += 1
        incumbent = archive.get(candidate.descriptor)
        if incumbent is None or candidate.quality > incumbent.quality:
            archive[candidate.descriptor] = candidate
    return archive, {"evaluations": budget, "valid": accepted, "invalid": invalid}


def run_random(seed: int, budget: int) -> tuple[dict[tuple[int, int], Candidate], dict[str, int]]:
    rng = random.Random(seed)
    archive: dict[tuple[int, int], Candidate] = {}
    accepted = 0
    invalid = 0
    for _ in range(budget):
        candidate = evaluate(random_genome(rng))
        if candidate is None:
            invalid += 1; continue
        accepted += 1
        incumbent = archive.get(candidate.descriptor)
        if incumbent is None or candidate.quality > incumbent.quality:
            archive[candidate.descriptor] = candidate
    return archive, {"evaluations": budget, "valid": accepted, "invalid": invalid}


def archive_metrics(archive: dict[tuple[int, int], Candidate], counts: dict[str, int]) -> dict[str, float | int]:
    values = [candidate.quality for candidate in archive.values()]
    return {
        "coverage": round(len(archive) / (ROUTE_BINS * DEFENSE_BINS), 6),
        "filled_cells": len(archive),
        "qd_score": round(sum(values), 6),
        "max_quality": round(max(values, default=0.0), 6),
        "mean_quality": round(statistics.mean(values) if values else 0.0, 6),
        "valid_rate": round(counts["valid"] / max(1, counts["evaluations"]), 6),
    }


def summarize_runs(rows: list[dict[str, float | int]]) -> dict[str, dict[str, float]]:
    summary: dict[str, dict[str, float]] = {}
    for key in ("coverage", "qd_score", "max_quality", "mean_quality", "valid_rate"):
        values = [float(row[key]) for row in rows]
        mean = statistics.mean(values)
        half = 1.96 * statistics.stdev(values) / math.sqrt(len(values)) if len(values) > 1 else 0.0
        summary[key] = {"mean": round(mean, 6), "ci95_low": round(mean - half, 6), "ci95_high": round(mean + half, 6)}
    return summary


def _candidate_json(candidate: Candidate) -> dict[str, object]:
    return {
        "cell": [candidate.descriptor[0], candidate.descriptor[1]],
        "routeCount": candidate.route_count,
        "defenseAdvantage": candidate.defense_advantage,
        "quality": candidate.quality,
        "rows": candidate.rows,
        "genome": asdict(candidate.genome),
        "metrics": candidate.metrics,
    }


def render_archive(archive: dict[tuple[int, int], Candidate], output: Path) -> None:
    from PIL import Image, ImageDraw

    cell = 12
    gap = 24
    map_w, map_h = WIDTH * cell, HEIGHT * cell
    canvas = Image.new("RGB", (gap + ROUTE_BINS * (map_w + gap), gap + DEFENSE_BINS * (map_h + gap)), "#111713")
    draw = ImageDraw.Draw(canvas)
    colors = {"f": "#7d8b58", "g": "#6f8756", "F": "#405d40", "w": "#887857", "m": "#625f50", "~": "#456f83", "v": "#77a8b1"}
    for (route_bin, defense_bin), candidate in archive.items():
        ox = gap + route_bin * (map_w + gap)
        oy = gap + (DEFENSE_BINS - 1 - defense_bin) * (map_h + gap)
        for y, row in enumerate(candidate.rows):
            for x, char in enumerate(row):
                draw.rectangle((ox + x * cell, oy + y * cell, ox + (x + 1) * cell - 1, oy + (y + 1) * cell - 1), fill=colors.get(char, "#77745f"))
        draw.rectangle((ox, oy, ox + map_w - 1, oy + map_h - 1), outline="#e4d6a3", width=2)
        draw.text((ox + 4, oy + 3), f"R{candidate.route_count} D{defense_bin + 1} Q{candidate.quality:.2f}", fill="white")
    for index in range(ROUTE_BINS): draw.text((gap + index * (map_w + gap), 4), f"routes {index + 1}", fill="#e4d6a3")
    for index in range(DEFENSE_BINS): draw.text((2, gap + (DEFENSE_BINS - 1 - index) * (map_h + gap)), f"D{index + 1}", fill="#e4d6a3")
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("web-game/scenario/map-elites-chuisha.archive.json"))
    parser.add_argument("--report", type=Path, default=Path("output/map-elites-chuisha/report.json"))
    parser.add_argument("--image", type=Path, default=Path("output/map-elites-chuisha/archive.png"))
    parser.add_argument("--budget", type=int, default=5000)
    parser.add_argument("--initial", type=int, default=350)
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20261103)
    args = parser.parse_args()
    all_map: list[dict[str, float | int]] = []
    all_random: list[dict[str, float | int]] = []
    best_archive: dict[tuple[int, int], Candidate] = {}
    best_qd = -1.0
    run_details: list[dict[str, object]] = []
    for index in range(args.runs):
        seed = args.seed + index * 7919
        archive, counts = run_map_elites(seed, args.budget, args.initial)
        baseline, baseline_counts = run_random(seed, args.budget)
        metrics = archive_metrics(archive, counts)
        random_metrics = archive_metrics(baseline, baseline_counts)
        all_map.append(metrics); all_random.append(random_metrics)
        run_details.append({"seed": seed, "mapElites": metrics, "random": random_metrics})
        if float(metrics["qd_score"]) > best_qd:
            best_qd = float(metrics["qd_score"]); best_archive = archive
    archive_payload = {
        "schemaVersion": "chuisha-map-elites-1",
        "battle": "垂沙之战",
        "year": "前301年",
        "historicalBoundary": "夹沘水相持、浅渡守备观察与夜袭来自《吕氏春秋·处方》；其余地形、部署与数值均为演武生成，不作为史实结论。",
        "dimensions": {"x": "routeCount", "y": "defenseAdvantage", "bins": [ROUTE_BINS, DEFENSE_BINS]},
        "grid": [WIDTH, HEIGHT],
        "riverRows": list(RIVER_ROWS),
        "sources": {"history": list(HISTORICAL_SOURCES), "algorithm": list(ALGORITHM_SOURCES)},
        "entries": [_candidate_json(best_archive[key]) for key in sorted(best_archive)],
    }
    report = {
        "schemaVersion": "chuisha-map-elites-report-1",
        "parameters": {"budgetPerMethod": args.budget, "initialPopulation": args.initial, "runs": args.runs, "baseSeed": args.seed, "mutationMix": {"local": 0.70, "topology": 0.20, "large": 0.10}},
        "mapElites": summarize_runs(all_map),
        "randomBaseline": summarize_runs(all_random),
        "runs": run_details,
        "releaseGate": {
            "fullArchive": len(best_archive) == ROUTE_BINS * DEFENSE_BINS,
            "allElitesHardValid": all(bool(candidate.metrics["hard_valid"]) for candidate in best_archive.values()),
            "mapElitesMeanQdAtLeastRandom": statistics.mean(float(row["qd_score"]) for row in all_map) >= statistics.mean(float(row["qd_score"]) for row in all_random),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(archive_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    render_archive(best_archive, args.image)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not all(report["releaseGate"].values()): raise SystemExit(1)


if __name__ == "__main__":
    main()
