"""Turn highlight moments into a cut: keep windows at 1x, fast-forward everything else,
adding lower-priority moments only while the reel stays within its time budget."""

KEEP, FAST = "keep", "fast"
SPEED, GAP_MAX = 10.0, 2.5  # fast-forward at least 10x, and no gap longer than 2.5s on screen


def merge(windows: list[tuple]) -> list[tuple[float, float]]:
    spans: list[list[float]] = []
    for a, b, *_ in sorted(windows):
        if spans and a - spans[-1][1] < 1.5:  # tiny gaps aren't worth a fast-forward
            spans[-1][1] = max(spans[-1][1], b)
        else:
            spans.append([a, b])
    return [(a, b) for a, b in spans]


def gap_out(gap: float) -> float:
    return min(GAP_MAX, gap / SPEED)


def runtime(keeps: list[tuple[float, float]], end: float) -> float:
    edges = [0.0] + [x for k in keeps for x in k] + [end]
    gaps = [edges[i + 1] - edges[i] for i in range(0, len(edges), 2)]
    return sum(b - a for a, b in keeps) + sum(gap_out(g) for g in gaps if g > 0)


def plan(windows: list[tuple], end: float, budget: float) -> list[tuple[str, float, float]]:
    chosen: list[tuple] = []
    for prio in (0, 1, 2):
        for w in sorted((w for w in windows if w[2] == prio), key=lambda w: -w[3]):
            if prio == 0 or runtime(merge(chosen + [w]), end) <= budget:
                chosen.append(w)
    segments, cursor = [], 0.0
    for a, b in merge(chosen):
        if a > cursor:
            segments.append((FAST, cursor, a))
        segments.append((KEEP, a, b))
        cursor = b
    if end - cursor > 0.5:
        segments.append((FAST, cursor, end))
    return segments
