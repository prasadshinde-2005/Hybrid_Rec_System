import pandas as pd 
import numpy as np 
from scipy.sparse import load_npz
from sklearn.metrics.pairwise import cosine_similarity

# make class for hybrid recommender system 
class HybridRecommenderSystem:

    def __init__(self , song_name : str ,
                 artist_name : str ,
                  number_of_recommendations : int ,
                    weight_content_base : float ,
                     weight_collaborative_base : float ,
                      songs_df , Transformed_matrix ,
                      interaction_matrix , track_ids): 

        self.number_of_recommendations = number_of_recommendations
        self.song_name = song_name.lower()
        self.artist_name = artist_name.lower()
        self.weight_content_base = weight_content_base
        self.weight_collaborative_base = weight_collaborative_base
        self.songs_df = songs_df
        self.Transformed_matrix = Transformed_matrix
        self.interaction_matrix = interaction_matrix
        self.track_ids = track_ids


    def calculate_content_base_similarities(self , song_name , artist_name , Transformed_matrix , songs_df):
        # filtered out songs data 
        song_row = songs_df.loc[(songs_df["name"] == song_name) & (songs_df["artist"] == artist_name)]

        # get the index of this particular song
        song_index = song_row.index[0]

        # Generate input vector for the cosine similarity 
        input_vector_CB = Transformed_matrix[song_index].reshape(1,-1) 

        # calcualte cosine similarity score 
        content_similarity_score = cosine_similarity(input_vector_CB , Transformed_matrix)
        return content_similarity_score


    def calculate_collaborative_base_similarity(self , song_name , artist_name , track_ids , interaction_matrix , songs_df):
            
        # filtered out songs data 
        song_row = songs_df.loc[(songs_df["name"] == song_name) & (songs_df["artist"] == artist_name)]

        #  find the track_ids of input song
        input_track_ids = song_row["track_id"].values.item()

        # index value of track id 
        ind = np.where(track_ids == input_track_ids)[0].item()

        # fetch input_vector_CF
        input_vector_CF = interaction_matrix[ind]
        
         # get similarity score 
        collaborative_similarity_score = cosine_similarity(input_vector_CF , interaction_matrix)
        return collaborative_similarity_score

    def normalize_similarities(self , similarity_score):
        minimum = np.min(similarity_score)
        maximum = np.max(similarity_score)
        normalized_scores = (similarity_score - minimum) / (similarity_score - maximum)
        return normalized_scores

   # calculate weighted score 
    def weighted_combination(self ,content_similarity_score, collaborative_similarity_score):
        
        weighted_scores = (self.weight_content_base * content_similarity_score) + (self.weight_collaborative_base * collaborative_similarity_score)
        return weighted_scores

    # get recommendations 

    def give_recommendations(self):
        # calculate  content based similarity 
        content_base_similarities = self.calculate_content_base_similarities(song_name = self.song_name ,
                                                                            songs_df = self.songs_df ,
                                                                             artist_name = self.artist_name ,
                                                                             Transformed_matrix =self.Transformed_matrix )

        collaborative_filtered_similarity = self.calculate_collaborative_base_similarity(songs_df = self.songs_df ,
                                                                                         song_name = self.song_name ,
                                                                                         interaction_matrix = self.interaction_matrix ,
                                                                                         track_ids = self.track_ids ,
                                                                                         artist_name = self.artist_name)                                                                       


        # normalize both similarities 
        normalized_content_base_similarities = self.normalize_similarities(content_base_similarities)
        normalized_collaborative_filtering_similarities = self.normalize_similarities(collaborative_filtered_similarity)

        # weighted commbination of similarities 
        weighted_score = self.weighted_combination(content_base_score = normalized_content_base_similarities ,
                                                   collaborative_filtering_score = normalized_collaborative_filtering_similarities)

        # index values of recommendations 
        recommendation_indices = np.argsort(weighted_score.ravel())[-self.number_of_recommendations -1:][::-1]
        
        # get track_ids of top k recommendation  
        recommendation_track_ids = self.track_ids[recommendation_indices]

        # get top score 
        top_scores = np.sort(weighted_score.ravel())[-self.number_of_recommendations -1:][::-1]

        # get songs from data and print 
        scores_df = pd.DataFrame({"track_id" : recommendation_track_ids.tolist() ,
                                  "score" : top_scores})

        # top k songs data 
        top_k_songs = (
                        self.songs_data
                        .loc[self.songs_df["track_id"].isin(recommendation_track_ids)]
                        .merge(scores_df ,on ="track_id")
                        .sort_values(by = "score" , ascending = False)
                        .drop(columns = ["track_id" , "score"])
                        .reset_index(drop = True)

                      )
        return top_k_songs


           
        
