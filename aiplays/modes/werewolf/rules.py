"""Player-facing rules text, generated from the same RoleDefs the engine enforces."""
from pathlib import Path

from aiplays.agents.prompts import render
from aiplays.core.state import GameState, Player
from aiplays.modes.werewolf.roles.base import ROLES, WOLF_DEN, RoleDef
from aiplays.modes.werewolf.status import role_of
from aiplays.settings import get_catalog

PROMPTS = Path(__file__).parent / "prompts"
_MOVES = {"visit": "visits", "travel": "travels", "none": "does not move"}


def ability_lines(r: RoleDef) -> list[str]:
    out = []
    for a in r.actions:
        limits = [f"{a.uses} uses per game"] if a.uses is not None else []
        limits += [f"from night {a.from_night}"] if a.from_night > 1 else []
        limits += [f"only on night {a.only_night}"] if a.only_night else []
        limits += [f"{a.cooldown}-night cooldown"] if a.cooldown else []
        extra = f" ({'; '.join(limits)})" if limits else ""
        out.append(f'  - Night ability "{a.name}" [{a.cls}, {_MOVES[a.movement]}]: {a.help}{extra}')
    return out


def role_card(r: RoleDef) -> str:
    head = f"{r.emoji} {r.label} (team: {r.team.upper()}). {r.summary}"
    return "\n".join([head, r.card, *ability_lines(r)]).strip()


def deck_text(roles: list[str]) -> str:
    counts: dict[str, int] = {}
    for r in roles:
        counts[r] = counts.get(r, 0) + 1
    return "\n".join(f"- {ROLES[r].label} x{c} [{ROLES[r].team}]: {ROLES[r].summary}"
                     for r, c in counts.items())


def briefing(state: GameState, p: Player, reveal_models: bool) -> str:
    cat = get_catalog()
    roster = "\n".join(
        f"{q.seat + 1}. {q.name}" + (f" (played by {cat.get(q.model_id).label})"
                                     if reveal_models else "") for q in state.players)
    rules = render("rules", PROMPTS, count=len(state.players),
                   deck=deck_text([q.role for q in state.players]))
    r = ROLES[role_of(state, p)]
    return render("briefing", PROMPTS, name=p.name, rules=rules, roster=roster,
                  role=role_card(r), knowledge=knowledge(state, p))


def knowledge(state: GameState, p: Player) -> str:
    """Private starting knowledge: your den mates, plus whatever your role's hook adds."""
    r = ROLES[role_of(state, p)]
    lines = []
    if WOLF_DEN in r.chats:
        den = [q for q in state.players if q is not p and WOLF_DEN in ROLES[q.role].chats]
        lines.append(f"Your pack in the wolf den: {state.names(den) or 'none, you hunt alone'}.")
    hook = r.hook("knowledge")
    if hook:
        lines.append(hook(state, p))
    return "\n".join(lines)
