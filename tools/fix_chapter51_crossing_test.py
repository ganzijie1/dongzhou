from pathlib import Path


path = Path(__file__).resolve().parents[1] / "rl/chapter51_test.py"
text = path.read_text(encoding="utf-8")
old_func = '''def reachable(rows, start, goal):
    queue, seen = deque([tuple(start)]), {tuple(start)}
    while queue:
        point = queue.popleft()
        if point == tuple(goal):
            return True
        x, y = point
        for nxt in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if nxt not in seen and passable(rows, nxt):
                seen.add(nxt)
                queue.append(nxt)
    return False
'''
new_func = '''def find_path(rows, start, goal):
    queue = deque([tuple(start)])
    previous = {tuple(start): None}
    while queue:
        point = queue.popleft()
        if point == tuple(goal):
            path = []
            while point is not None:
                path.append(point)
                point = previous[point]
            return list(reversed(path))
        x, y = point
        for nxt in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if nxt not in previous and passable(rows, nxt):
                previous[nxt] = point
                queue.append(nxt)
    return []


def reachable(rows, start, goal):
    return bool(find_path(rows, start, goal))
'''
old_assert = '''    assert not reachable(rows, (24, 25), (24, 31))
    assert reachable(rows, (24, 25), (45, 31))'''
new_assert = '''    cross_river_path = find_path(rows, (24, 25), (24, 31))
    assert cross_river_path
    assert any(x >= 44 and 27 <= y <= 29 for x, y in cross_river_path)
    assert reachable(rows, (24, 25), (45, 31))'''
if old_func not in text or old_assert not in text:
    raise RuntimeError("chapter 51 path test anchor missing")
text = text.replace(old_func, new_func, 1).replace(old_assert, new_assert, 1)
path.write_text(text, encoding="utf-8")
print("Qinghe regression now requires every north-south route to use the east ford.")
