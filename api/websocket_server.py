from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
import json

try:
    from core.intelligence.intelligence_system import IntelligenceSystem
except ImportError:
    IntelligenceSystem = None

app = FastAPI(title="Abraxas Intelligence WebSocket API")

# Active connections
active_connections: List[WebSocket] = []

# Shared intelligence system
intelligence_system = IntelligenceSystem(config={"calibration_method": "beta"}) if IntelligenceSystem else None


@app.websocket("/ws/signals")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            # Receive signal from client
            data = await websocket.receive_text()
            try:
                signal = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON"})
                continue

            # Process through IntelligenceSystem
            if intelligence_system:
                result = intelligence_system.process(
                    data=signal.get("features", []),
                    target=signal.get("target")
                )
            else:
                result = {"error": "IntelligenceSystem not available"}

            # Broadcast result to all connected clients
            message = {
                "type": "signal_result",
                "signal": signal,
                "result": result
            }

            for connection in active_connections:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass  # Remove dead connections later

    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception:
        if websocket in active_connections:
            active_connections.remove(websocket)
        await websocket.close()


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "active_connections": len(active_connections),
        "intelligence_system": intelligence_system is not None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
