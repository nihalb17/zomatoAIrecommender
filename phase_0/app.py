from fastapi import FastAPI

app = FastAPI(title="Zomato AI Recommender - Phase 0")


@app.get("/health")
def health_check() -> dict:
  return {
    "status": "ok",
    "phase": 0,
    "message": "Zomato AI Recommender Phase 0 is running.",
  }

