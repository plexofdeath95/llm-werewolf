"""WebSocket: replay stored events, then stream live ones; accept pause/resume/step."""
import asyncio
import contextlib

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from aiplays.core.hub import get_hub
from aiplays.core.session import GameSession

router = APIRouter()


def _state(s: GameSession | None) -> dict:
    if not s:
        return {"type": "state", "live": False, "paused": False, "spent": 0, "max_usd": 0}
    return {"type": "state", "live": s.running, "paused": s.gate.paused,
            "spent": round(s.budget.spent, 4), "max_usd": s.budget.max_usd}


@router.websocket("/api/games/{game_id}/ws")
async def stream(ws: WebSocket, game_id: str) -> None:
    await ws.accept()
    hub = get_hub()
    session = hub.live(game_id)
    await ws.send_json(_state(session))
    if not session or not session.running:  # finished game: plain replay from the DB
        for ev in await hub.repo.load_events(game_id):
            await ws.send_json({"type": "event", "event": ev.model_dump(mode="json")})
        await ws.send_json({"type": "end"})
        with contextlib.suppress(WebSocketDisconnect):
            while True:
                await ws.receive_text()
        return
    queue = session.bus.subscribe()  # subscribe first so nothing falls in the gap
    try:
        sent = 0
        for ev in list(session.bus.history):
            await ws.send_json({"type": "event", "event": ev.model_dump(mode="json")})
            sent = ev.seq
        await asyncio.gather(_forward(ws, queue, sent), _controls(ws, session))
    except WebSocketDisconnect:
        pass
    finally:
        session.bus.unsubscribe(queue)


async def _forward(ws: WebSocket, queue: asyncio.Queue, sent: int) -> None:
    while True:
        msg = await queue.get()
        if msg["type"] == "event" and msg["event"]["seq"] <= sent:
            continue
        await ws.send_json(msg)
        if msg["type"] == "event" and msg["event"]["kind"] == "game_over":
            await ws.send_json({"type": "end"})


async def _controls(ws: WebSocket, session: GameSession) -> None:
    while True:
        msg = await ws.receive_json()
        session.control(msg.get("action", ""), float(msg.get("amount", 5)))
        await ws.send_json(_state(session))
