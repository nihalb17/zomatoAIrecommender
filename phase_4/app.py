import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

from phase_2.models import UserPreferences, Restaurant
from phase_2.retrieval import get_recommendations, load_prepared_dataframe
from phase_3.llm_recommender import get_llm_recommendations
from phase_3.client import GroqClientError
from phase_4.models import RecommendationRequest, RecommendationResponse, RecommendationResponseItem, RestaurantInfo

# Load environment variables (GROQ_API_KEY)
load_dotenv()

app = FastAPI(
    title="Zomato AI Recommender API",
    description="API for getting LLM-powered restaurant recommendations from the Zomato dataset.",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(PHASE_5_DIR, "index.html"))

@app.get("/meta/localities")
def get_localities():
    df = load_prepared_dataframe()
    # "location" is the original column name in the dataset
    localities = sorted(df["location"].dropna().unique().tolist())
    return {"localities": localities}

@app.get("/meta/cuisines")
def get_cuisines():
    df = load_prepared_dataframe()
    # Extract unique cuisines from the comma-separated strings
    all_cuisines = set()
    for c_str in df["cuisines"].dropna():
        for c in c_str.split(","):
            all_cuisines.add(c.strip())
    return {"cuisines": sorted(list(all_cuisines))}

@app.post("/recommend", response_model=RecommendationResponse)
async def recommend(request: RecommendationRequest):
    """
    Generate restaurant recommendations based on user preferences.
    """
    # Map API request to Phase 2/3 internal preference model
    prefs = UserPreferences(
        min_price=request.min_price,
        max_price=request.max_price,
        locality=request.locality,
        min_rating=request.min_rating,
        desired_cuisines=request.desired_cuisines
    )

    try:
        # Pipeline: Dataset -> Phase 2 (Retrieval) -> Phase 3 (LLM Reasoning)
        llm_recs = get_llm_recommendations(prefs, max_candidates=15, max_results=5)
    except GroqClientError as exc:
        raise HTTPException(status_code=502, detail=f"Groq API Error: {str(exc)}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected Error: {str(exc)}")

    # Format the response
    results = []
    for rec in llm_recs:
        r = rec.restaurant
        results.append(RecommendationResponseItem(
            restaurant=RestaurantInfo(
                name=r.name,
                location=r.location,
                price_for_two=r.price_for_two,
                rating=r.rating,
                cuisines=r.cuisines,
                votes=r.votes
            ),
            reason=rec.reason
        ))

    return RecommendationResponse(
        preferences=request,
        recommendations=results
    )

# Static file serving for Phase 5 UI
PHASE_5_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "phase_5")

app.mount("/static", StaticFiles(directory=PHASE_5_DIR), name="static")
