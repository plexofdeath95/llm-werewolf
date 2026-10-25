"""Pure turn-taking logic for parallel-react conversations: who gets the floor next."""
import random
from dataclasses import dataclass

from aiplays.core.config import TalkConfig


@dataclass
class Bid:
    pid: str
    urgency: int
    message: str
    seq: int = 0  # REACTION event seq, linked from the resulting SPEECH


def is_pass(bid: Bid, cfg: TalkConfig) -> bool:
    return not bid.message.strip() or bid.urgency < cfg.pass_threshold


def score(bid: Bid, recent: list[str], named: set[str], spoken: dict[str, int],
          cfg: TalkConfig, rng: random.Random) -> float:
    s = float(bid.urgency)
    if bid.pid in named:
        s += cfg.named_bonus
    said = spoken.get(bid.pid, 0)
    s += cfg.unheard_bonus if said == 0 else -cfg.repeat_penalty * said
    if recent and recent[-1] == bid.pid:
        s -= cfg.last_penalty
    elif len(recent) > 1 and recent[-2] == bid.pid:
        s -= cfg.second_last_penalty
    return s + rng.uniform(-cfg.jitter, cfg.jitter)


def pick(bids: list[Bid], recent: list[str], named: set[str], spoken: dict[str, int],
         cfg: TalkConfig, rng: random.Random) -> tuple[Bid, float] | None:
    """Highest-scoring non-pass bid, or None when everyone passes."""
    scored = [(score(b, recent, named, spoken, cfg, rng), b) for b in bids if not is_pass(b, cfg)]
    if not scored:
        return None
    best_score, best = max(scored, key=lambda t: t[0])
    return best, round(best_score, 2)


def is_interrupt(bid: Bid, named: set[str], cfg: TalkConfig) -> bool:
    return bid.pid in named and bid.urgency >= cfg.interrupt_urgency


def limit(n_alive: int, cfg: TalkConfig) -> int:
    """Message budget (the discussion's time limit) for n_alive participants."""
    return max(n_alive, min(cfg.max_messages, cfg.rounds * n_alive))
