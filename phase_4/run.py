import uvicorn
import os
import sys

# Ensure project root is in path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if __name__ == "__main__":
    print("Starting Zomato AI Recommender API server...")
    uvicorn.run("phase_4.app:app", host="127.0.0.1", port=8000, reload=True)
