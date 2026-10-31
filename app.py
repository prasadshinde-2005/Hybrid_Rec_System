from contextlib import asynccontextmanager
from typing import Literal
import pandas as pd
from fastapi import FastAPI, HTTPException
from numpy import load
from pydantic import BaseModel, Field
from scipy.sparse import load_npz

from Content_base_filtered import content_recommendation
from hybrid_recommendations import HybridRecommenderSystem

# Holds all data loaded once at startup (shared by every request)
DATA: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load all datasets ONE time when the server starts."""
    DATA["songs_data"] = pd.read_csv("data/cleaned_data.csv")
    DATA["transformed_data"] = load_npz("data/transformed_data.npz")
    DATA["track_ids"] = load("data/track_ids.npy", allow_pickle=True)
    DATA["filtered_data"] = pd.read_csv("data/collab_filtered_data.csv")
    DATA["interaction_matrix"] = load_npz("data/interaction_matrix.npz")
    DATA["transformed_hybrid_data"] = load_npz("data/transformed_hybrid_data.npz")
    yield
    DATA.clear()


app = FastAPI(
    title="Spotify Song Recommender API",
    description="Suggests similar songs using content-based or hybrid filtering.",
    lifespan=lifespan,
)


# ---------- Request / response schemas ----------
class RecommendationRequest(BaseModel):
    song_name: str = Field(..., min_length=1, examples=["shape of you"])
    artist_name: str = Field(..., min_length=1, examples=["ed sheeran"])
    k: Literal[5, 10, 15, 20] = 10
    # Only used when the hybrid recommender is available (1 = personalized, 9 = diverse)
    diversity: int = Field(5, ge=1, le=9)


class Track(BaseModel):
    position: int
    name: str
    artist: str
    spotify_preview_url: str | None = None


class RecommendationResponse(BaseModel):
    filtering_type: str
    diversity: int | None = None
    currently_playing: Track
    next_up: list[Track]


# ---------- Helpers ----------
def normalize(text: str) -> str:
    return text.strip().lower()


def song_exists(df: pd.DataFrame, song: str, artist: str) -> bool:
    return ((df["name"] == song) & (df["artist"] == artist)).any()


def to_tracks(recommendations: pd.DataFrame) -> list[Track]:
    tracks = []
    for position, (_, row) in enumerate(recommendations.iterrows()):
        tracks.append(
            Track(
                position=position,
                name=row["name"].title(),
                artist=row["artist"].title(),
                spotify_preview_url=row.get("spotify_preview_url"),
            )
        )
    return tracks


# ---------- Endpoints ----------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/filtering-type")
def filtering_type(song_name: str, artist_name: str):
    """Tells the client which recommender will be used (so it can show the diversity slider)."""
    song, artist = normalize(song_name), normalize(artist_name)
    if song_exists(DATA["filtered_data"], song, artist):
        return {"filtering_type": "Hybrid Recommender System", "supports_diversity": True}
    return {"filtering_type": "Content-Based Filtering", "supports_diversity": False}


# Plain `def` (not async) because the work is CPU-bound;
# FastAPI runs it in a thread pool so the server isn't blocked.
@app.post("/recommend", response_model=RecommendationResponse)
def recommend(req: RecommendationRequest):
    song = normalize(req.song_name)
    artist = normalize(req.artist_name)

    # ----- Hybrid: song exists in the collaborative-filtered data -----
    if song_exists(DATA["filtered_data"], song, artist):
        content_based_weight = 1 - (req.diversity / 10)

        recommender = HybridRecommenderSystem(
            number_of_recommendations=req.k,
            weight_content_based=content_based_weight,
        )
        recommendations = recommender.give_recommendations(
            song_name=song,
            artist_name=artist,
            songs_data=DATA["filtered_data"],
            transformed_matrix=DATA["transformed_hybrid_data"],
            track_ids=DATA["track_ids"],
            interaction_matrix=DATA["interaction_matrix"],
        )
        used_type, used_diversity = "Hybrid Recommender System", req.diversity

    # ----- Content-based: fall back to the general songs data -----
    elif song_exists(DATA["songs_data"], song, artist):
        recommendations = content_recommendation(
            song_name=song,
            artist_name=artist,
            songs_data=DATA["songs_data"],
            transformed_data=DATA["transformed_data"],
            k=req.k,
        )
        used_type, used_diversity = "Content-Based Filtering", None

    else:
        raise HTTPException(
            status_code=404,
            detail=f"Sorry, we couldn't find '{song}' by '{artist}' in our database.",
        )

    tracks = to_tracks(recommendations)
    return RecommendationResponse(
        filtering_type=used_type,
        diversity=used_diversity,
        currently_playing=tracks[0],   # first row is the song you searched for
        next_up=tracks[1:],            # the rest are the recommendations
    )
