import numpy as np
import pandas as pd
from numpy import load
from scipy.sparse import load_npz
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional

from Content_base_filtered import content_recommendation
from hybrid_recommendations import HybridRecommenderSystem


app = FastAPI(title="Spotify Song Recommender API", version="1.0")

# ============ CORS (Frontend ko access dene ke liye) ============
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Production mein specific URL daalna
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ DATA LOAD (Startup pe ek baar) ============
def normalize(df: pd.DataFrame) -> pd.DataFrame:
    """Trim + lowercase name/artist so they match the user's input exactly."""
    for col in ("name", "artist"):
        df[col] = df[col].astype(str).str.strip().str.lower()
    return df


print("Loading data...")
songs_data = normalize(pd.read_csv("data/cleaned_data.csv"))
filtered_data = normalize(pd.read_csv("data/collab_filtered_data.csv"))
transformed_data = load_npz("data/transformed_data.npz")
interaction_matrix = load_npz("data/interaction_matrix.npz")
transformed_hybrid_data = load_npz("data/transformed_hybrid_data.npz")
track_ids = load("data/track_ids.npy", allow_pickle=True)
print("Data loaded successfully!")


# ============ HELPERS ============
def song_exists(df: pd.DataFrame, song: str, artist: str) -> bool:
    return bool(((df["name"] == song) & (df["artist"] == artist)).any())


# ============ REQUEST / RESPONSE MODELS ============
class RecommendRequest(BaseModel):
    song_name: str
    artist_name: str
    k: int = Field(default=10, ge=1, le=50)
    diversity: int = Field(default=5, ge=1, le=9)


class SongOut(BaseModel):
    name: str
    artist: str
    spotify_preview_url: Optional[str] = None


class RecommendResponse(BaseModel):
    engine: str
    recommendations: List[SongOut]


# ============ ENDPOINTS ============
@app.get("/")
def root():
    return {"message": "Song Recommender API is running. Test at /docs"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "songs": len(songs_data),
        "filtered_songs": len(filtered_data),
    }


@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    song = req.song_name.strip().lower()
    artist = req.artist_name.strip().lower()

    if not song or not artist:
        raise HTTPException(status_code=400, detail="Song name and artist name are required.")

    # ---- Decide engine: hybrid -> content-based -> not found ----
    if song_exists(filtered_data, song, artist):
        engine = "hybrid"
    elif song_exists(songs_data, song, artist):
        engine = "content"
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Sorry, we couldn't find '{req.song_name}' by '{req.artist_name}' in our database.",
        )

    # ---- Run correct recommender ----
    try:
        if engine == "hybrid":
            weight_cb = 1 - (req.diversity / 10)
            recommender = HybridRecommenderSystem(
                number_of_recommendations=req.k,
                weight_content_base=weight_cb,
            )
            recs = recommender.give_recommendations(
                song_name=song,
                artist_name=artist,
                songs_df=filtered_data,
                transformed_matrix=transformed_hybrid_data,
                track_ids=track_ids,
                interaction_matrix=interaction_matrix,
            )
        else:
            recs = content_recommendation(
                song_name=song,
                artist_name=artist,
                songs_data=songs_data,
                transformed_data=transformed_data,
                k=req.k,
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommender error: {str(e)}")

    # ---- Build JSON-friendly list ----
    output = []
    for _, row in recs.iterrows():
        url = row.get("spotify_preview_url")
        output.append(SongOut(
            name=str(row["name"]).title(),
            artist=str(row["artist"]).title(),
            spotify_preview_url=url if isinstance(url, str) and url.strip() else None,
        ))

    return RecommendResponse(engine=engine, recommendations=output)