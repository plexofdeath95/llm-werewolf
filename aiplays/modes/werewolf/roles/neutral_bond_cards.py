"""Role cards for the Cult Leader and Cupid (logic lives in neutral_bonds.py)."""
from aiplays.modes.werewolf.roles import neutral_bonds as b
from aiplays.modes.werewolf.roles.base import NEUTRAL, act, role

role(id="cult_leader", label="Cult Leader", team=NEUTRAL, emoji="🛐", classes=("influence",),
     weight=-6, hostile=True, in_deck=False, chats=(b.CULT,), hooks=b.CultLeader,
     summary="Converts one player a night; wins when every living player is in the cult.",
     card="Each night you visit one other player and convert them to your cult. Converts keep "
          "their role and abilities, join the private cult chat, and from then on win only with "
          "the cult. Anyone who role-blocks you joins the cult instead. You (and every convert) "
          "win the moment all living players are in the cult. If you die, every cult member "
          "dies with you. The Village cannot win while you live.",
     actions=(act("convert", "influence", "Visit a player and convert them to your cult.",
                  b._convert),))

role(id="cupid", label="Cupid", team=NEUTRAL, emoji="💘", classes=("influence",), weight=0,
     hooks=b.Cupid, summary="On night 1 makes two players fall in love; wins if both survive.",
     card="On night 1 only, choose any two players (yourself allowed). They fall in love: both "
          "keep their roles, learn who their lover is, get a private lovers' chat, and each "
          "night may choose to sleep at the same home (whatever happens there happens to both). "
          "You win if both lovers are alive when the game ends, whoever else wins.",
     actions=(act("shoot", "influence", "Night 1: pick two players to fall in love.", b._shoot,
                  movement="none", targets=2, pool="anyone", only_night=1),))
