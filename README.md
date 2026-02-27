## Zomato AI Restaurant Recommender

This project builds an AI-powered restaurant recommender on top of the Zomato dataset from Hugging Face, using a Groq LLM reasoning layer over a structured retrieval engine.

The implementation is organized **phase by phase**, with separate folders per phase under `src/`.

### Getting Started (Phase 0)

1. **Create and activate a virtual environment** (optional but recommended).
2. **Install dependencies** (from the project root):

```bash
pip install -r requirements.txt
```

3. **Run the Phase 0 FastAPI app**:

```bash
uvicorn phase_0.app:app --reload
```

4. Open `http://127.0.0.1:8000/health` in your browser to verify Phase 0 is working.

Phase-specific code and config for Phase 0 now live under the `phase_0/` folder. Future phases will follow the same pattern (e.g., `phase_1/`, `phase_2/`, etc.).

See `ARCHITECTURE.md` for the full phase-wise design.

