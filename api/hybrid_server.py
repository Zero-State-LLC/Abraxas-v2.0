from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, AsyncGenerator
import asyncio
import json

try:
    from core.intelligence.intelligence_system import IntelligenceSystem
except ImportError:
    IntelligenceSystem = None

app = FastAPI(title="Abraxas Hybrid Intelligence API (WebSocket + SSE)")

# Shared system
intelligence_system = IntelligenceSystem(config={"calibration_method": "beta"}) if IntelligenceSystem else None

# WebSocket connections
ws_connections: List[WebSocket] = []


# ============================================================
# WebSocket Endpoint (Client → Server commands / signals)
# ============================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    ws_connections.append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON"})
                continue

            msg_type = message.get("type")

            if msg_type == "signal":
                # Process signal through IntelligenceSystem
                if intelligence_system:
                    result = intelligence_system.process(
                        data=message.get("features", []),
                        target=message.get("target")
                    )
                    response = {
                        "type": "signal_result",
                        "result": result
                    }
                    await websocket.send_json(response)
                else:
                    await websocket.send_json({"error": "IntelligenceSystem not available"})

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        if websocket in ws_connections:
            ws_connections.remove(websocket)
    except Exception as e:
        if websocket in ws_connections:
            ws_connections.remove(websocket)
        await websocket.close()


# ============================================================
# Server-Sent Events (Server → Client updates)
# ============================================================

async def sse_event_generator(request: Request) -> AsyncGenerator[str, None]:
    while True:
        if await request.is_disconnected():
            break

        # Heartbeat
        yield f"event: heartbeat\ndata: {json.dumps({'ts': asyncio.get_event_loop().time()})}\n\n"
        await asyncio.sleep(5)


@app.get("/events")
async def sse_endpoint(request: Request):
    return StreamingResponse(
        sse_event_generator(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


# ============================================================
# HTTP Fallback
# ============================================================

@app.post("/process")
async def http_process(signal: dict):
    if intelligence_system is None:
        return {"error": "IntelligenceSystem not available"}

    result = intelligence_system.process(
        data=signal.get("features", []),
        target=signal.get("target")
    )
    return {"status": "processed", "result": result}


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "websocket_connections": len(ws_connections),
        "intelligence_system": intelligence_system is not None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
