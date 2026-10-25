"""Village tinkerers: the Mechanist's traps and the Jack of All Trades' one-time tricks."""
from aiplays.modes.werewolf.roles import effects
from aiplays.modes.werewolf.roles.base import VILLAGE, act, role
from aiplays.modes.werewolf.roles.traps import BUILD_TRAP, PLACE_TRAP, TrapHooks
from aiplays.modes.werewolf.roles.village_kill import ALERT, KILL

role(id="mechanist", label="Mechanist", team=VILLAGE, emoji="⚙️", classes=KILL, weight=3,
     hooks=TrapHooks, summary="Builds and lays traps that kill the first visitor of a home.",
     card="Each night either build a trap or lay one at a home (or move your laid trap). "
          "Only one trap can be laid at a time. The first player to visit that home dies.",
     actions=(BUILD_TRAP, PLACE_TRAP))
role(id="jack_of_all_trades", label="Jack of All Trades", team=VILLAGE, emoji="🃏",
     classes=("protection", "role_block", "killing"), weight=4,
     summary="Once each per game: heal like a Doctor, block like an Escort, alert like a Veteran.",
     card="You have three one-time tricks: heal a player, block a player, or go on alert at "
          "home (killing all visitors). Each can be used once per game.",
     actions=(act("heal", "protection", "Heal a player tonight.", effects.heal, pool="anyone",
                  uses=1),
              act("block", "role_block", "Keep a player busy.", effects.block, uses=1),
              act("alert", "killing", "Kill all your visitors.", ALERT, movement="none",
                  targets=0, uses=1)))
