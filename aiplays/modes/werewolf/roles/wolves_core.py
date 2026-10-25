"""The pack's backbone: Alpha (the kill), Wolf, Heir, Loner, Turncoat; Alpha succession."""
from aiplays.core.events import Kind
from aiplays.core.moderator import Moderator
from aiplays.core.state import GameState, Player
from aiplays.modes.werewolf.roles import effects
from aiplays.modes.werewolf.roles.base import ROLES, WOLF_DEN, WOLVES, act, role
from aiplays.modes.werewolf.status import role_of, status

ALPHA_KILL = act("kill", "killing", "Carry out the pack's kill: visit a non-wolf and kill them.",
                 effects.kill("killed by the werewolves"), pool="non_wolves")


def wolf_team(state: GameState) -> list[Player]:
    return [p for p in state.alive() if ROLES[role_of(state, p)].team == WOLVES]


class Succession:
    """Whenever the pack has no Alpha: Heir/Loner first, then a Wolf, then any wolf role."""

    @staticmethod
    async def before_night(mod: Moderator, p: Player) -> None:
        st = mod.state
        pack = wolf_team(st)
        if not pack or any("alpha" in (role_of(st, q), *status(st, q).marks.get("titles", ()))
                           for q in pack):
            return
        rank = {"heir": 0, "loner": 0, "wolf": 1}
        new = min(pack, key=lambda q: (rank.get(role_of(st, q), 2), q.seat))
        s = status(st, new)
        if role_of(st, new) in rank:
            s.acting_as = "alpha"
        else:  # keep their own powers, gain the pack's kill
            s.marks.setdefault("titles", []).append("alpha")
            s.marks.setdefault("borrowed", []).append(ALPHA_KILL)
        if WOLF_DEN not in ROLES[role_of(st, new)].chats:
            s.marks.setdefault("chats", []).append(WOLF_DEN)
        await mod.emit(Kind.ACTION, "You are now the Alpha: you carry out the pack's kill.",
                       actor=new.id, visible_to=[new.id], data={"action": "result"})


def _den(state: GameState, p: Player) -> str:
    return f"The werewolves are: {state.names([q for q in state.players if q.team == WOLVES])}."


class Knows:
    knowledge = staticmethod(_den)


role(id="alpha", label="Alpha", team=WOLVES, emoji="🐺", classes=("killing",), weight=-7,
     chats=(WOLF_DEN,), hooks=Succession, summary="Leads the pack and performs its nightly kill.",
     card="Each night you visit a non-wolf and kill them; agree on the victim with your pack "
          "first. If you die, another wolf becomes Alpha.",
     actions=(ALPHA_KILL,))
role(id="wolf", label="Wolf", team=WOLVES, emoji="🐾", classes=("support",), weight=-5,
     chats=(WOLF_DEN,), hooks=Succession,
     summary="A plain werewolf. Plots in the den; may become the next Alpha.",
     card="You have no night action of your own, but you help choose the pack's victim in the "
          "wolf den. If the Alpha dies, you may be chosen as the new Alpha.")
role(id="heir", label="Heir", team=WOLVES, emoji="👑", classes=("support",), weight=-4,
     hooks=Succession, summary="A hidden wolf outside the den; becomes Alpha if the Alpha dies.",
     card="You do not start in the wolf den and do not know the other wolves. If the Alpha "
          "dies, you join the den and become the new Alpha.")
role(id="loner", label="Loner", team=WOLVES, emoji="🌒", classes=("support",), weight=-4,
     hooks=type("LonerHooks", (Succession, Knows), {}),
     summary="Knows the wolves but they don't know them; becomes Alpha if the Alpha dies.",
     card="You start outside the wolf den. You know who the wolves are, but they don't know "
          "you. If the Alpha dies, you become the new Alpha and join the den.")
role(id="turncoat", label="Turncoat", team=WOLVES, emoji="🎭", classes=("support",), weight=-3,
     hooks=Knows, summary="A wolf ally outside the den who knows who the wolves are.",
     card="You are on the Werewolf team but never join the wolf den. You know who the wolves "
          "are; help them win from the shadows by misleading the village.")
