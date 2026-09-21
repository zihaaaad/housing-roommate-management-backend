from datetime import datetime, timezone
import json
from collections import defaultdict
from typing import Dict, List
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status
from app.core.security import decode_access_token
from app.database import SessionLocal
from app.models.message import DirectMessage
from app.models.user import User

ws_router = APIRouter(tags=["WebSockets"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = defaultdict(list)

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id].append(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_to_user(self, user_id: int, data: dict):
        if user_id in self.active_connections:
            dead_sockets = []
            for ws in self.active_connections[user_id]:
                try:
                    await ws.send_json(data)
                except Exception:
                    dead_sockets.append(ws)
            for dead in dead_sockets:
                self.disconnect(user_id, dead)


manager = ConnectionManager()


@ws_router.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket, token: str = Query(...)):
    try:
        payload = decode_access_token(token)
        user_id_str = payload.get("sub")
        if not user_id_str:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        user_id = int(user_id_str)
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(user_id, websocket)
    try:
        while True:
            text = await websocket.receive_text()
            data = json.loads(text)
            receiver_id = int(data.get("receiver_id", 0))
            content = str(data.get("content", "")).strip()
            if not receiver_id or not content:
                continue

            db = SessionLocal()
            try:
                receiver = db.query(User).filter(User.id == receiver_id, User.is_active == True).first()
                if not receiver:
                    await websocket.send_json({"error": "Recipient not found or inactive."})
                    continue

                msg = DirectMessage(
                    sender_id=user_id,
                    receiver_id=receiver_id,
                    content=content,
                    created_at=datetime.now(timezone.utc),
                    is_read=False
                )
                db.add(msg)
                db.commit()
                db.refresh(msg)

                outbound_data = {
                    "id": msg.id,
                    "sender_id": user_id,
                    "receiver_id": receiver_id,
                    "content": content,
                    "created_at": msg.created_at.isoformat(),
                    "is_read": False
                }
                await manager.send_to_user(receiver_id, outbound_data)
                await websocket.send_json({"status": "sent", "data": outbound_data})
            finally:
                db.close()
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
    except Exception:
        manager.disconnect(user_id, websocket)
