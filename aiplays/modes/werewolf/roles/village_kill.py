"""Village killers and blockers: hunter, inquisitor, veteran, vigilante, crusader, sentry..."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiplays.modes.werewolf.roles import effects
from aiplays.modes.werewolf.roles.base import ROLES, VILLAGE, WOLVES, act, role
from aiplays.modes.werewolf.status import role_of, status

if TYPE_CHECKING:
    from aiplays.modes.werewolf.night.context import Act, Night

KILL = ("killing",)
ALERT = effects.kill_visitors(True, "shot by someone on alert")


def _refund_immune(n: Night, a: Act) -> None:
    """Hunter: a shot that hits a night-immune target is not spent."""
    t = a.targets[0]
    if t.id not in n.deaths and n.role(t).night_immune:
        s = n.st(a.actor)
        s.uses[a.action.name] = s.uses.get(a.action.name, 0) + 1


def _guilt(n: Night, a: Act) -> None:
    t = a.targets[0]
    if t.id in n.deaths and n.team(t) == VILLAGE:
        n.deaths[a.actor.id] = "turned themselves in after killing a villager"


class Hunter:
    @staticmethod
    def decides(state, p) -> str | None:
        """Last stand: the Hunter (shots left) vs a single wolf is a village victory."""
        alive = state.alive()
        wolves = [q for q in alive if ROLES[role_of(state, q)].team == WOLVES]
        shots = status(state, p).uses.get("shoot", 3)
        return VILLAGE if len(alive) == 2 and len(wolves) == 1 and shots > 0 else None


role(id="hunter", label="Hunter", team=VILLAGE, emoji="🏹", classes=KILL, weight=5, hooks=Hunter,
     summary="Has 3 shots to kill at night. Wins a last stand against a single wolf.",
     card="Up to 3 times per game, visit a player at night and kill them. A shot at a "
          "night-immune player is not used up. If only you and one wolf remain and you have "
          "shots left, the village wins.",
     actions=(act("shoot", "killing", "Shoot a player.", effects.kill("shot by the Hunter"),
                  uses=3, after=_refund_immune),))
role(id="inquisitor", label="Inquisitor", team=VILLAGE, emoji="🔥", classes=KILL, weight=5,
     summary="3 uses total: either kill a visited player or go on alert at home.",
     card="You have 3 uses in total. Each night you may either visit and kill a player, or "
          "stay home on alert and kill everyone who visits you.",
     actions=(act("shoot", "killing", "Visit and kill a player.",
                  effects.kill("burned by the Inquisitor"), uses=3, uses_key="inquisitor"),
              act("alert", "killing", "Stay home on alert; kill all visitors.", ALERT,
                  movement="none", targets=0, uses=3, uses_key="inquisitor")))
role(id="veteran", label="Veteran", team=VILLAGE, emoji="🎖️", classes=KILL, weight=4,
     summary="Goes on alert (3 times): kills everyone who visits that night.",
     card="Up to 3 times per game, stay home on alert: everyone who visits you that night "
          "dies (friend or foe).",
     actions=(act("alert", "killing", "Go on alert tonight.", ALERT, movement="none",
                  targets=0, uses=3),))
role(id="vigilante", label="Vigilante", team=VILLAGE, emoji="🔫", classes=KILL, weight=5,
     summary="Can kill each night; if they kill a villager, they turn themselves in.",
     card="Visit a player at night and kill them. If your victim was on the village side, "
          "you turn yourself in at dawn and die. No protection can stop that.",
     actions=(act("shoot", "killing", "Shoot a player.", effects.kill("shot by the Vigilante"),
                  after=_guilt),))
role(id="crusader", label="Crusader", team=VILLAGE, emoji="⚔️", classes=("role_block",) + KILL,
     weight=4, summary="Watches a home 3 times: kills the owner if they go out.",
     card="Up to 3 times, travel to a player's home. If they leave home tonight, you kill "
          "them; their body is found outside their own door. Not the same player twice in a row.",
     actions=(act("watch", "killing", "Kill a player if they leave home tonight.",
                  effects.kill_if_leaves("struck down by the Crusader"), movement="travel",
                  uses=3, no_repeat=True),))
role(id="sentry", label="Sentry", team=VILLAGE, emoji="🗼", classes=("protection",) + KILL,
     weight=4, summary="Guards a home 3 times, killing anyone who comes to it.",
     card="Up to 3 times, travel to a player's home and kill every other player who visits "
          "or travels there tonight, whatever their intent. Not the same player twice in a row.",
     actions=(act("stand_guard", "killing", "Kill everyone who comes to a player's home.",
                  effects.kill_visitors(False, "cut down by a Sentry", travellers=True),
                  movement="travel", uses=3, no_repeat=True),))
role(id="escort", label="Escort", team=VILLAGE, emoji="💃", classes=("role_block",), weight=4,
     summary="Visits a player and keeps them home: their action fails.",
     card="Visit a player each night: they cannot leave home or use their ability (they are "
          "told). Not the same player two nights in a row. Seers and Mystics can't be blocked.",
     actions=(act("block", "role_block", "Keep a player busy all night.", effects.block),))
