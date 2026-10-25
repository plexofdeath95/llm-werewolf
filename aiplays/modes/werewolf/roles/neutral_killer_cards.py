"""Role cards for the neutral killers (logic lives in neutral_killers.py)."""
from aiplays.modes.werewolf.roles import effects
from aiplays.modes.werewolf.roles import neutral_killers as k
from aiplays.modes.werewolf.roles.base import NEUTRAL, act, role
from aiplays.modes.werewolf.roles.neutral_kit import GOAL_TEXT

LAST = (" You also win if the game ends with you alive as the last threat standing. "
        "The Village cannot win while you live.")

role(id="arsonist", label="Arsonist", team=NEUTRAL, emoji="🔥", classes=k.KILLER, weight=-5,
     hostile=True, hooks=k.Arsonist,
     summary="Douses homes in petrol, then ignites every doused player at once.",
     card="Each night either DOUSE one player (you visit them; they are told their home was "
          "doused) or IGNITE: every doused player burns to death. Burning cannot be healed or "
          "protected against. Anyone who role-blocks you is doused instead of your target. "
          f"You win once you have burned at least {GOAL_TEXT} players." + LAST,
     actions=(act("douse", "killing", "Visit a player and soak their home in petrol.", k.douse),
              act("ignite", "killing", "Set fire to every doused player at once (no visit).",
                  k.ignite, movement="none", targets=0, ready=k.has_doused)))

role(id="murderer", label="Murderer", team=NEUTRAL, emoji="🔪", classes=k.KILLER, weight=-5,
     hostile=True, hooks=k.Murderer,
     summary="Kills one player a night; anyone who visits them dies instead.",
     card="Each night you may visit one player and kill them. If anyone visits YOUR home on a "
          "night you hunt, you kill the first such visitor (by night priority) instead of your "
          f"target. You win once you have killed at least {GOAL_TEXT} Village players." + LAST,
     actions=(act("murder", "killing", "Visit a player and kill them.", k.murder),))

role(id="crone", label="Crone", team=NEUTRAL, emoji="🧙", classes=("role_block", "killing"),
     weight=-4, hostile=True, hooks=k.Crone,
     summary="Waits outside a home and kills the owner if they step out.",
     card="Each night you travel to one player's home and lie in wait (never the same player "
          "two nights in a row). If they leave home that night (use any ability that visits or "
          "travels), you kill them; the body is found outside their door. You win once you have "
          f"killed at least {GOAL_TEXT} players." + LAST,
     actions=(act("stalk", "killing", "Wait outside a player's home; kill them if they go out.",
                  effects.kill_if_leaves("killed by the Crone"), movement="travel",
                  no_repeat=True),))

role(id="vampire", label="Vampire", team=NEUTRAL, emoji="🧛", classes=("killing", "role_copy"),
     weight=-5, hostile=True, hooks=k.Vampire,
     summary="Drains a victim each night and borrows their powers the next night.",
     card="Each night you may DRAIN one player: you visit and kill them. On a night you drain "
          "(and are not blocked), killing attacks cannot harm you. Anyone who role-blocks you "
          "dies in place of your victim. The night after a successful drain you may also use "
          "your victim's night abilities, and investigators see you as their role. You win once "
          f"you have drained at least {GOAL_TEXT} players." + LAST,
     actions=(act("drain", "killing", "Visit a player and drain them dry.", k.drain,
                  after=k.feed),))
