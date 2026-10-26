"""Insight tables as {title: (columns, rows)}: printed by scripts/insights.py or saved as CSV."""
from aiplays.modes.werewolf.insights import minds, moods, talk
from aiplays.modes.werewolf.insights.load import Game

Table = tuple[list[str], list[list]]


def pct(a: float, b: float) -> int | None:
    return round(100 * a / b) if b else None


def per(a: float, b: float, nd: int = 1) -> float | None:
    return round(a / b, nd) if b else None


def tables(games: list[Game]) -> dict[str, Table]:
    sus, tk = minds.suspicion(games), talk.per_model(games)
    order = sorted(tk, key=lambda m: -tk[m]["seats"])
    s = {m: sus["models"].get(m, {}) for m in order}
    out: dict[str, Table] = {}
    out["Reading wolves: was the village's prime suspect a real wolf?"] = (
        ["model", "village reads", "on a wolf %", "changes of mind %", "switches", "switch on a wolf %"],
        [[m, s[m].get("reads", 0), pct(s[m].get("hits", 0), s[m].get("reads", 0)),
          pct(s[m].get("changes", 0), s[m].get("pairs", 0)), s[m].get("switches", 0),
          pct(s[m].get("switch_hits", 0), s[m].get("switches", 0))] for m in order])
    oc = sus["outcomes"]
    out["Does changing your mind pay? (village suspects, all models)"] = (
        ["case", "on a wolf", "reads", "on a wolf %"],
        [["random pick", "", "", round(100 * sus["baseline"])]]
        + [[k, oc[k][0], oc[k][1], pct(*oc[k])] for k in ("first", "kept", "switched")]
        + [[f"switch: {k}", n, "", ""] for k, n in sorted(sus["moves"].items())])
    out["Talk"] = (
        ["model", "lines", "words/line", "passes %", "interruptions %", "drafts spoken %",
         "cut-off complaints"],
        [[m, t["lines"], per(t["words"], t["lines"]), pct(t["passes"], t["reactions"]),
          pct(t["interrupts"], t["lines"]), pct(t["lines"], t["drafts"]), t["unheard"]]
         for m, t in ((m, tk[m]) for m in order)])
    out["Role claims: honest / made, by team"] = (
        ["model", "as village", "as wolf", "as neutral"],
        [[m] + [f"{tk[m][f'honest_{team}']}/{tk[m][f'claims_{team}']}"
                for team in ("village", "wolves", "neutral")] for m in order])
    out["Seats, wins, reasoning and cost"] = (
        ["model", "seats", "wins/finished", "native reasoning chars/call", "thought words",
         "cost per seat $"],
        [[m, t["seats"], f"{t['wins']}/{t['finished']}", per(t["native_chars"], t["native_calls"], 0),
          per(t["thought_words"], t["thoughts"], 0), per(t["cost_usd"], t["seats"], 3)]
         for m, t in ((m, tk[m]) for m in order)])
    mm = moods.moods_by_model(games)
    out["Mood words per 100 private thoughts"] = (
        ["model", *moods.MOODS, "thoughts"], [[m, *mm[m].values()] for m in order if m in mm])
    ft = moods.focus_by_team(games)
    out["Focus words per 100 private thoughts, by team"] = (
        ["team", *moods.FOCUS, "thoughts"], [[t, *v.values()] for t, v in ft.items()])
    return out
