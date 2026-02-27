## Zomato AI Restaurant Recommender – Architecture

This document describes the high-level architecture and phased implementation plan for the **Zomato AI Restaurant Recommender**. The system will:

- Take user parameters: **Price**, **Locality**, **Rating**, **Cuisine (type)**.
- Use the Zomato dataset from Hugging Face (`ManikaSaini/zomato-restaurant-recommendation`) as the primary data source.
- Use a **Groq LLM–based reasoning layer** on top of structured retrieval to generate restaurant recommendations and explanations.

The work is divided into phases so we can build, test, and iterate incrementally.

---

## Phase 0 – Project Setup & Foundations

- **Goals**
  - Set up the project structure, environment, and configuration.
  - Decide on core tech stack (e.g., Python backend with FastAPI/Flask, LLM provider, basic CLI or simple web UI).
- **Key Decisions**
  - **Backend language/framework**: Python with FastAPI (or Flask) for APIs.
  - **Data handling**: `pandas` for data loading and preprocessing.
- **LLM access**: via Groq LLM HTTP API, wrapped behind an abstraction layer so we can mock and swap providers if needed.
  - **Interface**: start with a simple CLI or minimal web form for inputs, then grow.
- **Deliverables**
  - Project skeleton: `src/` (code), `data/` (local copies or cache), `configs/`, `notebooks/` (optional for EDA), `tests/`.
  - Base configuration file(s) (e.g., `config.yaml` or `.env.example`).
  - Basic README explaining how to set up and run the project.
- **Testing & Validation**
  - Verify environment setup and unit-test scaffolding.
  - Confirm we can run a simple “hello world” API/CLI.

---

## Phase 1 – Data Ingestion, Understanding & Preparation

- **Goals**
  - Ingest the Hugging Face dataset and understand its schema, quality, and coverage for fields related to **Price**, **Locality**, **Rating**, **Cuisine**.
  - Clean and normalize the dataset to support structured filtering by user parameters:
    - **Price**: price bands / normalized price level.
    - **Locality**: consistent locality naming and possibly higher-level areas.
    - **Rating**: numeric rating and quality filters.
    - **Cuisine**: standardized cuisine labels / sets.
- **Core Components**
  - `data_ingestion` module:
    - Function to download/load dataset from Hugging Face (`datasets` library or direct CSV).
    - Local caching layer to avoid repeated downloads.
  - `data_schema` definition:
    - Types for price, rating, cuisine, locality, etc.
  - `data_preprocessing` module:
    - Functions for:
      - Handling missing ratings/prices.
      - Normalizing price into discrete buckets (e.g., low/medium/high).
      - Standardizing locality names.
      - Tokenizing/normalizing `cuisines` fields into lists or sets.
  - **Feature schema**:
    - A structured representation for a restaurant (e.g., `Restaurant` model / dataclass).
- **Tasks**
  - Load the dataset into `pandas` DataFrame(s).
  - Inspect columns: restaurant name, location, cost, rating, cuisines, etc.
  - Identify missing values, inconsistencies, and duplicates.
  - Implement cleaning functions and apply them to raw data.
  - Define business rules:
    - Default behavior when rating is missing.
    - Price bucket thresholds.
    - How to handle multiple cuisines per restaurant.
- **Deliverables**
  - Reusable loading utility (e.g., `src/data/load_zomato_dataset.py`).
  - EDA notebook or script summarizing:
    - Distribution of prices, ratings.
    - Top localities and cuisines.
  - Cleaned DataFrame and/or serialized artifact (e.g., Parquet/CSV) for downstream use.
  - `Restaurant` model abstraction to be reused across modules.
- **Testing & Validation**
  - Unit tests to ensure dataset loads and expected key columns exist.
  - Sanity checks on row counts and basic statistics.
  - Unit tests for preprocessing functions (e.g., price binning, cuisine parsing).
  - Spot-check a sample of transformed records for correctness.

---

## Phase 2 – Core Retrieval & Ranking Engine (Non-LLM)

- **Goals**
  - Build a deterministic, LLM-agnostic retrieval layer that:
    - Filters restaurants based on user constraints (Price, Locality, Rating, Cuisine).
    - Ranks them using simple heuristics (e.g., rating, review count, popularity).
  - This becomes the “candidate generator” that feeds into the LLM.
- **Core Components**
  - `retrieval` module:
    - Filtering function(s) using structured inputs:
      - `price_range`, `locality`, `min_rating`, `desired_cuisines`.
    - Scoring/ranking function, e.g.:
      - Sort by rating, break ties by number of votes or cost, etc.
  - `recommendation_core` module:
    - High-level function that:
      - Takes user parameters.
      - Calls the retrieval module to get top-N candidate restaurants.
- **Tasks**
  - Implement filtering logic with reasonable defaults (e.g., fallback to nearby localities if none match exactly).
  - Implement ranking heuristics (e.g., weighted score combining rating and popularity).
  - Define API for “candidate restaurants” that the LLM will consume.
- **Deliverables**
  - Deterministic recommendation function that returns a ranked list of restaurant objects.
  - Ability to get sensible recommendations even without the LLM.
- **Testing & Validation**
  - Unit tests for filtering and ranking logic.
  - Scenario tests:
    - Typical queries (popular localities and cuisines).
    - Edge cases (rare cuisines, strict price constraints).

---

## Phase 3 – LLM Integration & Reasoning Layer

- **Goals**
  - Integrate an LLM to:
    - Interpret user preferences (Price, Locality, Rating, Cuisine) from structured inputs (or natural language later).
    - Generate **natural language justifications and descriptions** for recommendations.
    - Optionally re-rank or group the candidate restaurants by nuanced preference reasoning.
- **Core Components**
  - `llm_client` module:
    - Abstract interface for calling the chosen LLM provider (e.g., `LLMClient` base class).
    - Concrete implementation for the selected provider/API key management.
  - `prompt_templates` module:
    - System and user prompts that:
      - Explain the data schema and constraints.
      - Provide candidate restaurants and ask the LLM to choose and justify top-K.
  - `llm_recommender` module:
    - Function that:
      - Accepts user parameters and candidate restaurants.
      - Crafts prompts.
      - Calls the LLM.
      - Parses the LLM response into a structured format (e.g., list of recommended restaurant IDs + explanations).
- **Tasks**
  - Design robust prompt templates (e.g., few-shot examples).
  - Decide on output format (JSON-like structure inside LLM response).
  - Implement parsing and error-handling for malformed responses.
- **Deliverables**
  - End-to-end function: `get_llm_recommendations(user_preferences)` that:
    - Uses the core retrieval to get candidates.
    - Uses the LLM to produce a final recommendation list with explanations.
- **Testing & Validation**
  - Unit tests for prompt construction and parsing logic (using mocked LLM responses).
  - Integration tests mocking the LLM client to ensure the pipeline runs without external calls.
  - Manual tests with a real LLM (e.g., via API key in dev environment).

---

## Phase 4 – API / Application Layer

- **Goals**
  - Expose the recommender via a clean interface:
    - **Option A**: REST API (e.g., FastAPI).
    - **Option B**: Simple CLI application.
    - **Option C**: Minimal web UI (form-based).
  - Allow users to input **Price**, **Locality**, **Rating**, and **Cuisine** and receive recommendations.
- **Core Components**
  - `api` module (if using REST):
    - Endpoint(s), e.g. `POST /recommendations` with JSON body:
      - `{ price_range, locality, min_rating, cuisines }`.
    - Request validation with schemas (e.g., Pydantic models).
  - `cli` module (optional):
    - Interactive command-line interface to input parameters.
  - Simple UI (optional in this phase, or deferred to Phase 6).
- **Tasks**
  - Wire the `llm_recommender` to the chosen interface(s).
  - Implement input validation and sensible defaults.
  - Serialize recommendations (including explanations) to JSON for responses.
- **Deliverables**
  - Running service or CLI that:
    - Accepts user parameters.
    - Returns a ranked list of restaurants with LLM-generated text.
- **Testing & Validation**
  - API/CLI integration tests.
  - Manual tests for UX and correctness of responses.

---

## Phase 5 – UI/UX Layer (Optional but Recommended)

- **Goals**
  - Provide a simple, user-friendly interface (web frontend) to consume the recommender.
- **Core Components**
  - Frontend (could be React, simple HTML/JS, or Streamlit/Gradio).
  - Input form fields for: Price range, Locality, Minimum Rating, Cuisine.
  - Results view:
    - List of recommended restaurants with:
      - Name, locality, rating, price info, cuisines.
      - LLM explanation: *“Why this restaurant?”*.
- **Tasks**
  - Build minimal UI and connect it to the backend API.
  - Handle loading state, error messages, and display formatting.
- **Deliverables**
  - Basic web app/dashboard running locally.
- **Testing & Validation**
  - Manual UI testing.
  - Optional end-to-end tests (e.g., Playwright/Cypress) if needed.

---

## Phase 6 – Evaluation, Metrics & Iteration

- **Goals**
  - Evaluate recommendation quality and iterate on retrieval and prompting.
- **Core Components**
  - `evaluation` module:
    - Simple offline metrics, e.g.:
      - Coverage rates (how often we find valid recommendations for given constraints).
      - Diversity of cuisines/localities in results.
    - (Optional) small user-study framework or heuristic scoring.
- **Tasks**
  - Design qualitative evaluation scenarios:
    - Different budgets, localities, and cuisine types.
  - Adjust:
    - Retrieval filters and ranking heuristics.
    - Prompt templates and instructions to the LLM.
- **Deliverables**
  - Evaluation scripts or notebooks.
  - Documented insights and tuned parameters/prompt changes.
- **Testing & Validation**
  - Before/after comparisons of recommendation sets.
  - Stability checks for changes (no major regressions in coverage).

---

## Phase 7 – Packaging, Configuration & Deployment (Optional)

- **Goals**
  - Make the system easy to run, configure, and (optionally) deploy.
- **Core Components**
  - Packaging:
    - `requirements.txt` or `pyproject.toml`.
  - Configuration:
    - `.env` / config files for:
      - LLM API keys.
      - Dataset location/cache paths.
      - Model/provider toggles.
  - Deployment (optional):
    - Dockerfile and simple deployment instructions (e.g., run on a VM or platform-as-a-service).
- **Tasks**
  - Externalize configuration values (no secrets in code).
  - Package the app for local and/or cloud deployment.
- **Deliverables**
  - Installable / runnable package with clear instructions.
  - Optional Docker image definition + deployment guide.
- **Testing & Validation**
  - Fresh-environment install and run test.
  - Smoke tests in the target deployment environment (if used).

---

## Data & Control Flow Overview

- **User Input Layer**
  - User specifies: `price_range`, `locality`, `min_rating`, `cuisine(s)`.
- **Core Flow**
  1. Input validation and normalization.
  2. Structured retrieval:
    - Query cleaned dataset using the specified parameters.
    - Generate candidate restaurant list (Phase 2).
  3. LLM reasoning:
    - Construct prompt with user preferences + candidate restaurants.
    - Call LLM and parse structured recommendation response (Phase 3).
  4. Output formatting:
    - Combine LLM-chosen restaurants with metadata and explanations.
    - Return to API/CLI/UI.
- **Separation of Concerns**
  - **Data layer** (Phase 1): dataset loading, cleaning, and feature representation.
  - **Retrieval layer** (Phase 2): rule-based candidate search and ranking.
  - **LLM layer** (Phase 3): high-level reasoning and explanation.
  - **Interface layer** (Phases 4–5): how users interact with the system.
  - **Ops layer** (Phases 6–7): evaluation, packaging, deployment.

---

## Next Step

The **next concrete step** after this architecture is to start **Phase 0 and Phase 1**:

- Finalize tech stack and project folder layout.
- Implement a data loading utility for the Hugging Face Zomato dataset and perform basic EDA to confirm that all parameters (Price, Locality, Rating, Cuisine) are present and usable.

