from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import asyncio
import json

try:
    from core.intelligence.intelligence_system import IntelligenceSystem
except ImportError:
    IntelligenceSystem = None

app = FastAPI(title="Abraxas Intelligence SSE API")

intelligence_system = IntelligenceSystem(config={"calibration_method": "beta"}) if IntelligenceSystem else None


async def event_generator(request: Request) -> AsyncGenerator[str, None]:
    """
    Server-Sent Events generator.
    Sends periodic updates and can push processed results.
    """
    last_id = 0

    while True:
        if await request.is_disconnected():
            break

        # Example: Send a heartbeat every 5 seconds
        yield f"event: heartbeat\ndata: {json.dumps({'timestamp': asyncio.get_event_loop().time()})}\n\n"

        await asyncio.sleep(5)


@app.get("/events")
async def sse_endpoint(request: Request):
    """
    Server-Sent Events endpoint.
    Clients can connect here to receive real-time updates.
    """
    return StreamingResponse(
        event_generator(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Important for nginx
        }
    )


@app.post("/process")
async def process_signal(signal: dict):
    """
    Process a signal and (in a real implementation) would push via SSE.
    For now, just returns the result.
    """
    if intelligence_system is None:
        return {"error": "IntelligenceSystem not available"}

    result = intelligence_system.process(
        data=signal.get("features", []),
        target=signal.get("target")
    )
    return {
        "status": "processed",
        "result": result
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "intelligence_system_available": intelligence_system is not None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
