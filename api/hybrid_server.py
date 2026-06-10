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


# ============================================================
# Pydantic Validation Models
# ============================================================

class SignalInput(BaseModel):
    features: List[float] = Field(..., min_items=1, description="Feature vector for processing")
    target: Optional[float] = Field(None, ge=0.0, le=1.0, description="Optional target for Brier scoring")

    @validator('features')
    def validate_features(cls, v):
        if len(v) > 50:  # Reasonable upper limit
            raise ValueError('Feature vector too large (max 50)')
        return v


class WebSocketMessage(BaseModel):
    type: str = Field(..., description="Message type: 'signal', 'ping', etc.")
    features: Optional[List[float]] = None
    target: Optional[float] = None


# ============================================================
# WebSocket Endpoint with Validation
# ============================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    ws_connections.append(websocket)
    logger.info(f"WebSocket client connected. Total: {len(ws_connections)}")

    try:
        while True:
            try:
                data = await websocket.receive_text()
            except Exception as e:
                logger.warning(f"WebSocket receive error: {e}")
                break

            try:
                raw_message = json.loads(data)
                message = WebSocketMessage(**raw_message)  # Pydantic validation
            except Exception as e:
                await websocket.send_json({"error": "Invalid message format", "details": str(e)})
                continue

            if message.type == "signal":
                if message.features is None:
                    await websocket.send_json({"error": "'features' field is required for signal type"})
                    continue

                if intelligence_system is None:
                    await websocket.send_json({"error": "IntelligenceSystem not available"})
                    continue

                try:
                    result = intelligence_system.process(
                        data=message.features,
                        target=message.target
                    )
                    await websocket.send_json({
                        "type": "signal_result",
                        "result": result
                    })
                except Exception as proc_error:
                    logger.error(f"Processing error: {proc_error}")
                    await websocket.send_json({
                        "error": "Processing failed",
                        "details": str(proc_error)
                    })

            elif message.type == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"Unexpected WebSocket error: {e}")
    finally:
        if websocket in ws_connections:
            ws_connections.remove(websocket)


# ============================================================
# SSE Endpoint
# ============================================================

async def sse_event_generator(request: Request) -> AsyncGenerator[str, None]:
    try:
        while True:
            if await request.is_disconnected():
                break
            yield f"event: heartbeat\ndata: {json.dumps({'ts': asyncio.get_event_loop().time()})}\n\n"
            await asyncio.sleep(5)
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


# ============================================================
# HTTP Process Endpoint with Pydantic Validation
# ============================================================

@app.post("/process")
async def http_process(signal: SignalInput):
    if intelligence_system is None:
        raise HTTPException(status_code=503, detail="IntelligenceSystem not available")

    try:
        result = intelligence_system.process(
            data=signal.features,
            target=signal.target
        )
        return {"status": "processed", "result": result}
    except Exception as e:
        logger.error(f"HTTP processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@app.get("/health")
async def health():
    try:
        return {
            "status": "ok",
            "websocket_connections": len(ws_connections),
            "intelligence_system": intelligence_system is not None
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
