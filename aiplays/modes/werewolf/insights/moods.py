"""Mood and focus words in private thoughts, per 100 thoughts. Simple word lists, not a feelings
detector: "wait" counts as caution and "kill" as planning."""
import re
from collections import Counter, defaultdict

from aiplays.modes.werewolf.insights.load import Game

MOODS = {
    "fear": r"\b(nervous|worried|worry|scared|afraid|fear|risk|danger|exposed|panic)\w*",
    "confidence": r"\b(confident|sure|certain|clearly|obvious|definitely|proof|proven)\w*",
    "suspicion": r"\b(suspicious|suspect|doubt|odd|off|fishy|lying|lie|bluff)\w*",
    "caution": r"\b(careful|cautious|wait|patient|quiet|low profile|blend)\w*",
    "aggression": r"\b(push|pressure|attack|force|hammer|corner|accuse)\w*",
    "guilt": r"\b(sorry|feel bad|awful|guilt|apolog|hurt)\w*",
    "strategy": r"\b(plan|strategy|deflect|narrative|frame|credib|trust|target)\w*",
}
FOCUS = {
    "plans and head-counts": r"\b(plan|kill|parity|win condition|two|three|four|alive|numbers?|"
                             r"tonight|target)\b",
    "covering tracks": r"\b(cover|blend|low|quiet|attention|safe|exposed?|suspicion on me)\b",
    "reading people": r"\b(seems|feels|odd|suspicious|evasive|defensive|nervous|lying|trust|honest)\b",
}


def _thoughts(games: list[Game]):
    for g in games:
        for e in g.events:
            thought = (e.data.get("thought") or "").lower()
            if thought and e.actor in g.seats:
                yield g.seats[e.actor], thought


def _per_100(groups: dict[str, Counter], lexicon: dict[str, str]) -> dict[str, dict[str, int]]:
    return {k: {w: round(100 * c[w] / c["n"]) for w in lexicon} | {"thoughts": c["n"]}
            for k, c in groups.items()}


def moods_by_model(games: list[Game]) -> dict[str, dict[str, int]]:
    groups: dict[str, Counter] = defaultdict(Counter)
    for seat, thought in _thoughts(games):
        groups[seat.model]["n"] += 1
        for word, rx in MOODS.items():
            groups[seat.model][word] += len(re.findall(rx, thought))
    return _per_100(groups, MOODS)


def focus_by_team(games: list[Game]) -> dict[str, dict[str, int]]:
    groups: dict[str, Counter] = defaultdict(Counter)
    for seat, thought in _thoughts(games):
        groups[seat.team]["n"] += 1
        for word, rx in FOCUS.items():
            groups[seat.team][word] += len(re.findall(rx, thought))
    return _per_100(groups, FOCUS)
