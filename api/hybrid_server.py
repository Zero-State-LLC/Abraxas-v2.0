from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, AsyncGenerator
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
# WebSocket Endpoint with Error Handling
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
                message = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON format"})
                continue

            msg_type = message.get("type")

            if msg_type == "signal":
                if intelligence_system is None:
                    await websocket.send_json({"error": "IntelligenceSystem not available"})
                    continue

                try:
                    result = intelligence_system.process(
                        data=message.get("features", []),
                        target=message.get("target")
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

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"Unexpected WebSocket error: {e}")
    finally:
        if websocket in ws_connections:
            ws_connections.remove(websocket)


# ============================================================
# SSE Endpoint with Error Handling
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
        logger.error(f"SSE generator error: {e}")
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
# HTTP Process Endpoint with Error Handling
# ============================================================

@app.post("/process")
async def http_process(signal: dict):
    if intelligence_system is None:
        raise HTTPException(status_code=503, detail="IntelligenceSystem not available")

    try:
        result = intelligence_system.process(
            data=signal.get("features", []),
            target=signal.get("target")
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
