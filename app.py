import streamlit as st
from Content_base_filtered import content_recommendation
from scipy.sparse import load_npz
import pandas as pd
from numpy import load
from hybrid_recommendations import HybridRecommenderSystem


# ============ DATA LOAD (with lowercase fix) ============
songs_data = pd.read_csv("data/cleaned_data.csv")
songs_data["name"] = songs_data["name"].str.lower().str.strip()
songs_data["artist"] = songs_data["artist"].str.lower().str.strip()

transformed_data = load_npz("data/transformed_data.npz")
track_ids = load("data/track_ids.npy", allow_pickle=True)

filtered_data = pd.read_csv("data/collab_filtered_data.csv")
filtered_data["name"] = filtered_data["name"].str.lower().str.strip()
filtered_data["artist"] = filtered_data["artist"].str.lower().str.strip()

interaction_matrix = load_npz("data/interaction_matrix.npz")
transformed_hybrid_data = load_npz("data/transformed_hybrid_data.npz")


# ============ UI ============
st.title('Welcome to the Spotify Song Recommender!')
st.write('### Enter the name of a song and the recommender will suggest similar songs 🎵🎧')

song_name = st.text_input('Enter a song name:').lower().strip()
artist_name = st.text_input('Enter the artist name:').lower().strip()

if song_name:
    st.write('You entered:', song_name, '-', artist_name)

k = st.selectbox('How many recommendations do you want?', [5, 10, 15, 20], index=1)

# ============ DECIDE FILTERING TYPE ============
# Sirf tab check karo jab user ne kuch type kiya ho
if not song_name:
    filtering_type = None
elif ((filtered_data["name"] == song_name) & (filtered_data["artist"] == artist_name)).any():
    filtering_type = "Hybrid Recommender System"
else:
    filtering_type = "Content-Based Filtering"

# ============ HYBRID: Show diversity slider ============
if filtering_type == "Hybrid Recommender System":
    diversity = st.slider("Diversity in Recommendations", min_value=1, max_value=9, value=5, step=1)
    content_based_weight = 1 - (diversity / 10)

    chart_data = pd.DataFrame({
        "type": ["Personalized", "Diverse"],
        "ratio": [10 - diversity, diversity]
    })
    st.bar_chart(chart_data, x="type", y="ratio")

# ============ BUTTON + LOGIC ============
if filtering_type is None:
    st.info("👆 Please enter a song name to get recommendations.")

elif st.button('Get Recommendations'):

    if filtering_type == "Content-Based Filtering":
        # Double check: song exists in content-based data?
        if ((songs_data["name"] == song_name) & (songs_data["artist"] == artist_name)).any():
            st.write('Recommendations for', f"**{song_name.title()}** by **{artist_name.title()}**")
            recommendations = content_recommendation(
                song_name=song_name,
                artist_name=artist_name,
                songs_data=songs_data,
                transformed_data=transformed_data,
                k=k
            )
        else:
            recommendations = None
            st.warning(f"Sorry, we couldn't find **{song_name.title()}** by **{artist_name.title()}** in our database. Please try another song.")

    elif filtering_type == "Hybrid Recommender System":
        st.write('Recommendations for', f"**{song_name.title()}** by **{artist_name.title()}**")
        recommender = HybridRecommenderSystem(
            number_of_recommendations=k,
            weight_content_based=content_based_weight
        )
        recommendations = recommender.give_recommendations(
            song_name=song_name,
            artist_name=artist_name,
            songs_data=filtered_data,
            transformed_matrix=transformed_hybrid_data,
            track_ids=track_ids,
            interaction_matrix=interaction_matrix
        )

    # ============ DISPLAY (session_state mein save karo) ============
    if recommendations is not None:
        st.session_state["recommendations"] = recommendations

# ============ DISPLAY FROM SESSION STATE (survives reruns) ============
if "recommendations" in st.session_state and filtering_type is not None:
    for ind, recommendation in st.session_state["recommendations"].iterrows():
        rec_song_name = recommendation['name'].title()
        rec_artist_name = recommendation['artist'].title()

        if ind == 0:
            st.markdown("## Currently Playing")
            st.markdown(f"#### **{rec_song_name}** by **{rec_artist_name}**")
            st.audio(recommendation['spotify_preview_url'])
            st.write('---')
        elif ind == 1:
            st.markdown("### Next Up 🎵")
            st.markdown(f"#### {ind}. **{rec_song_name}** by **{rec_artist_name}**")
            st.audio(recommendation['spotify_preview_url'])
            st.write('---')
        else:
            st.markdown(f"#### {ind}. **{rec_song_name}** by **{rec_artist_name}**")
            st.audio(recommendation['spotify_preview_url'])
            st.write('---')