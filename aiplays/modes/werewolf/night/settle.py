"""Turn the night's attacks into deaths, honouring jail, guards, martyrs, heals, armor, lives."""
from aiplays.core.state import Player
from aiplays.modes.werewolf.night.context import Attack, Night


def settle(n: Night) -> None:
    for atk in n.attacks:
        t = atk.target
        if t.id in n.deaths or not t.alive:
            continue
        if atk.unstoppable or not _saved(n, atk):
            kill(n, t, atk.cause, atk.by)


def kill(n: Night, p: Player, cause: str, by: Player | None) -> None:
    n.deaths[p.id] = cause
    if by is not None and by is not p:
        s = n.st(by)
        s.kills += 1
        team = n.team(p)
        s.kills_by_team[team] = s.kills_by_team.get(team, 0) + 1
        s.flags.add("has_killed")


def _saved(n: Night, atk: Attack) -> bool:
    t, s = atk.target, n.st(atk.target)
    if t.id in n.jailed:
        n.note(t, "Someone tried to attack you in your cell, but the Jailor kept you safe.")
        return True
    if n.guards.get(t.id):
        guard = n.guards[t.id].pop(0)
        kill(n, guard, "died bodyguarding", atk.by)
        if atk.by is not None and atk.by.id not in n.deaths:
            kill(n, atk.by, "killed by a Bodyguard", guard)
        n.note(t, "You were attacked, but a Bodyguard fought off your attacker.")
        return True
    if n.martyrs.get(t.id):
        martyr = n.martyrs[t.id].pop(0)
        kill(n, martyr, "sacrificed themselves as a Martyr", atk.by)
        n.note(t, "You were attacked, but someone gave their life for yours.")
        return True
    if n.heals.get(t.id):
        for doc in n.heals[t.id]:
            n.note(doc, f"{t.name} was attacked tonight, and you saved them.")
        n.note(t, "You were attacked, but someone nursed you back to health.")
        return True
    for flag in ("armor_on", "steroid"):
        if flag in s.flags:
            s.flags.discard(flag)
            n.note(t, "You were attacked, but your protection held and is now spent.")
            return True
    hook = n.role(t).hook("on_attacked")
    if hook and hook(n, atk):
        return True
    if s.lives > 1:
        s.lives -= 1
        n.note(t, f"You were attacked and lost a life ({s.lives} left).")
        return True
    if n.role(t).night_immune:
        n.note(t, "Someone attacked you tonight, but you are immune at night.")
        return True
    return False
