import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


class HybridRecommenderSystem:

    def __init__(self, number_of_recommendations: int, weight_content_base: float):
        self.number_of_recommendations = number_of_recommendations
        self.weight_content_base = weight_content_base
        self.weight_collaborative_base = 1 - weight_content_base

    def calculate_content_base_similarities(self, song_name, artist_name, Transformed_matrix, songs_df):
        song_row = songs_df.loc[(songs_df["name"] == song_name) & (songs_df["artist"] == artist_name)]
        song_index = song_row.index[0]  # first match (safe if duplicates exist)

        input_vector_CB = Transformed_matrix[song_index]  # already shape (1, n_features)
        return cosine_similarity(input_vector_CB, Transformed_matrix)

    def calculate_collaborative_base_similarity(self, song_name, artist_name, track_ids, interaction_matrix, songs_df):
        song_row = songs_df.loc[(songs_df["name"] == song_name) & (songs_df["artist"] == artist_name)]
        input_track_id = song_row["track_id"].iloc[0]  # .iloc[0] instead of .values.item()

        ind = np.where(track_ids == input_track_id)[0][0]  # [0][0] instead of .item()
        input_vector_CF = interaction_matrix[ind]
        return cosine_similarity(input_vector_CF, interaction_matrix)

    def normalize_similarities(self, similarity_score):
        minimum = np.min(similarity_score)
        maximum = np.max(similarity_score)
        if maximum == minimum:  # avoid divide-by-zero
            return np.zeros_like(similarity_score)
        return (similarity_score - minimum) / (maximum - minimum)  # FIXED denominator

    def weighted_combination(self, content_base_score, collaborative_filtering_score):  # FIXED names
        return (self.weight_content_base * content_base_score) + (
            self.weight_collaborative_base * collaborative_filtering_score
        )

    def give_recommendations(self, song_name, artist_name, songs_df, interaction_matrix, transformed_matrix, track_ids):
        content_sim = self.calculate_content_base_similarities(
            song_name=song_name, artist_name=artist_name,
            Transformed_matrix=transformed_matrix, songs_df=songs_df,
        )
        collab_sim = self.calculate_collaborative_base_similarity(
            song_name=song_name, artist_name=artist_name, track_ids=track_ids,
            interaction_matrix=interaction_matrix, songs_df=songs_df,
        )

        # Both score arrays must be in the same song order
        if content_sim.shape != collab_sim.shape or content_sim.shape[1] != len(track_ids):
            raise ValueError(
                "Content matrix, interaction matrix and track_ids must have the same rows in the same order."
            )

        weighted_score = self.weighted_combination(
            content_base_score=self.normalize_similarities(content_sim),
            collaborative_filtering_score=self.normalize_similarities(collab_sim),
        )

        k = self.number_of_recommendations
        order = np.argsort(weighted_score.ravel())[::-1][: k + 1]  # +1 = the input song itself
        recommendation_track_ids = track_ids[order]  # FIXED: was self.track_ids
        top_scores = weighted_score.ravel()[order]   # same order as the ids

        scores_df = pd.DataFrame({"track_id": recommendation_track_ids.tolist(), "score": top_scores})

        return (
            songs_df.loc[songs_df["track_id"].isin(recommendation_track_ids)]  # FIXED: was self.songs_data / self.songs_df
            .drop_duplicates(subset="track_id")
            .merge(scores_df, on="track_id")
            .sort_values(by="score", ascending=False)
            .drop(columns=["track_id", "score"])
            .reset_index(drop=True)
        )