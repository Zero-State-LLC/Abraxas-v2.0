from fastapi import FastAPI

app = FastAPI(title="ABRAXAS v2")

@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "system": "abraxas-v2"
    }
