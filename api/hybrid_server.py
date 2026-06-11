from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, AsyncGenerator, Optional
import asyncio
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hybrid_server")

try:
    from core.intelligence.intelligence_system import IntelligenceSystem
except ImportError:
    IntelligenceSystem = None

app = FastAPI(title="Abraxas Hybrid Intelligence API")

intelligence_system = IntelligenceSystem(config={"calibration_method": "beta"}) if IntelligenceSystem else None
ws_connections: List[WebSocket] = []
client_subscriptions: Dict[WebSocket, Dict[str, Any]] = {}  # Per-client filters

HEARTBEAT_INTERVAL = 5


# ============================================================
# Pydantic Models
# ============================================================

class SignalInput(BaseModel):
    features: List[float] = Field(..., min_items=1)
    target: Optional[float] = Field(None, ge=0.0, le=1.0)

    @validator('features')
    def validate_features(cls, v):
        if len(v) > 50:
            raise ValueError('Feature vector too large (max 50)')
        return v

class WebSocketMessage(BaseModel):
    type: str
    features: Optional[List[float]] = None
    target: Optional[float] = None
    signal_type: Optional[str] = None  # For filtering
    min_severity: Optional[float] = None


# ============================================================
# Filtering Logic
# ============================================================

def should_send_to_client(client: WebSocket, result: dict, original_message: dict = None) -> bool:
    """Check if a result should be sent to a specific client based on their subscription."""
    if client not in client_subscriptions:
        return True  # No subscription = receive everything

    sub = client_subscriptions[client]

    # Filter by signal_type
    if sub.get("signal_types"):
        signal_type = original_message.get("signal_type") if original_message else None
        if signal_type and signal_type not in sub["signal_types"]:
            return False

    # Filter by minimum severity (if result contains severity info)
    if sub.get("min_severity") is not None:
        # Try to extract severity from result (flexible)
        severity = None
        if "result" in result and isinstance(result["result"], dict):
            severity = result["result"].get("severity")
        if severity is not None and severity < sub["min_severity"]:
            return False

    return True


async def broadcast_to_websockets(message: dict, original_message: dict = None):
    """Broadcast message only to clients who match their subscription filters."""
    dead_connections = []
    for connection in ws_connections:
        if should_send_to_client(connection, message, original_message):
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)

    for dead in dead_connections:
        if dead in ws_connections:
            ws_connections.remove(dead)
        if dead in client_subscriptions:
            del client_subscriptions[dead]


# ============================================================
# WebSocket Endpoint with Filtering Support
# ============================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    ws_connections.append(websocket)
    logger.info(f"WebSocket client connected. Total: {len(ws_connections)}")

    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=HEARTBEAT_INTERVAL + 2)
            except asyncio.TimeoutError:
                try:
                    await websocket.send_json({"type": "ping"})
                except Exception:
                    break
                continue

            try:
                raw_message = json.loads(data)
                message = WebSocketMessage(**raw_message)
            except Exception as e:
                await websocket.send_json({"error": "Invalid message", "details": str(e)})
                continue

            if message.type == "subscribe":
                # Client wants to set filters
                filters = {}
                if message.signal_type:
                    filters["signal_types"] = [message.signal_type]
                if message.min_severity is not None:
                    filters["min_severity"] = message.min_severity

                client_subscriptions[websocket] = filters
                await websocket.send_json({
                    "type": "subscription_updated",
                    "filters": filters
                })
                logger.info(f"Client subscribed with filters: {filters}")

            elif message.type == "signal":
                if message.features is None:
                    await websocket.send_json({"error": "features required"})
                    continue

                if intelligence_system is None:
                    await websocket.send_json({"error": "IntelligenceSystem not available"})
                    continue

                try:
                    result = intelligence_system.process(data=message.features, target=message.target)

                    broadcast_message = {
                        "type": "signal_result",
                        "result": result
                    }

                    # Broadcast with filtering
                    await broadcast_to_websockets(broadcast_message, raw_message)

                    # Always send back to sender
                    await websocket.send_json(broadcast_message)

                except Exception as e:
                    await websocket.send_json({"error": "Processing failed", "details": str(e)})

            elif message.type == "pong":
                pass

            elif message.type == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if websocket in ws_connections:
            ws_connections.remove(websocket)
        if websocket in client_subscriptions:
            del client_subscriptions[websocket]


# ============================================================
# SSE (kept simple for now)
# ============================================================

async def sse_event_generator(request: Request) -> AsyncGenerator[str, None]:
    try:
        while True:
            if await request.is_disconnected():
                break
            yield f"event: heartbeat\ndata: {json.dumps({'timestamp': asyncio.get_event_loop().time()})}\n\n"
            await asyncio.sleep(HEARTBEAT_INTERVAL)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"SSE error: {e}")
        yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"


@app.get("/events")
async def sse_endpoint(request: Request):
    try:
        return StreamingResponse(
            sse_event_generator(request),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )
    except Exception as e:
        logger.error(f"SSE endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process")
async def http_process(signal: SignalInput):
    if intelligence_system is None:
        raise HTTPException(status_code=503, detail="IntelligenceSystem not available")

    try:
        result = intelligence_system.process(data=signal.features, target=signal.target)
        await broadcast_to_websockets({"type": "signal_result", "result": result, "source": "http"})
        return {"status": "processed", "result": result}
    except Exception as e:
        logger.error(f"HTTP processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    try:
        return {
            "status": "ok",
            "websocket_connections": len(ws_connections),
            "subscribed_clients": len(client_subscriptions),
            "intelligence_system": intelligence_system is not None
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
