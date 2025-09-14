"""
🎬 Moteur de recommandations ML pour Cinetopia
Utilise KNN (K-Nearest Neighbors) + TF-IDF pour recommander des films similaires
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import os
import unicodedata
import re
from django.conf import settings
from .models import Movie

def normalize_text(text):
    """Normalise le texte : supprime accents, met en minuscules, nettoie."""
    if not text:
        return ""
    
    # Supprime les accents
    text = unicodedata.normalize('NFD', str(text))
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    
    # Minuscules et nettoyage
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)  # Garde seulement lettres/chiffres/espaces
    text = re.sub(r'\s+', ' ', text).strip()  # Nettoie espaces multiples
    
    return text

class CinetopiaRecommender:
    """Moteur de recommandations basé sur le contenu des films."""
    
    def __init__(self):
        self.vectorizer = None
        self.knn_model = None
        self.tfidf_matrix = None
        self.movie_data = None
        self.is_trained = False
        
    def prepare_features(self, movies_df):
        """Prépare les caractéristiques textuelles des films."""
        
        # Combine genre, description et informations pour créer un profil textuel
        def create_content_profile(row):
            profile = []
            
            # Genre (poids important)
            if pd.notna(row.get('genre')):
                genre = str(row['genre']).replace('|', ' ')
                profile.append(f"{genre} {genre}")  # Double poids pour genre
            
            # Description/Synopsis
            if pd.notna(row.get('description')):
                profile.append(str(row['description']))
                
            # Réalisateur (triple poids - très important pour similarité)
            if pd.notna(row.get('director')):
                director = str(row['director'])
                profile.append(f"director_{director} director_{director} director_{director}")
            
            # Acteurs principaux (triple poids - très important pour similarité)
            if pd.notna(row.get('actors')):
                actors = str(row['actors'])
                profile.append(f"actors_{actors} actors_{actors} actors_{actors}")
            
            return ' '.join(profile)
        
        movies_df['content_profile'] = movies_df.apply(create_content_profile, axis=1)
        return movies_df
    
    def train_model(self):
        """Entraîne le modèle de recommandations."""
        
        print("🤖 Entraînement du modèle de recommandations...")
        
        # Récupère tous les films de la base
        movies = Movie.objects.all().values(
            'id', 'title', 'genre', 'description', 
            'release_date', 'rating', 'director', 'actors'
        )
        
        if not movies:
            print("❌ Aucun film trouvé en base de données")
            return False
            
        self.movie_data = pd.DataFrame(movies)
        print(f"📊 {len(self.movie_data)} films chargés")
        
        # Prépare les caractéristiques
        self.movie_data = self.prepare_features(self.movie_data)
        
        # Vectorisation TF-IDF
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8
        )
        
        content_profiles = self.movie_data['content_profile'].fillna('')
        self.tfidf_matrix = self.vectorizer.fit_transform(content_profiles)
        
        # Modèle KNN
        self.knn_model = NearestNeighbors(
            n_neighbors=20,
            metric='cosine',
            algorithm='brute'
        )
        self.knn_model.fit(self.tfidf_matrix)
        
        self.is_trained = True
        print("✅ Modèle entraîné avec succès !")
        return True
    
    def get_recommendations_by_movie_id(self, movie_id, n_recommendations=10):
        """Recommande des films similaires à partir d'un ID de film."""
        
        if not self.is_trained:
            if not self.train_model():
                return []
        
        try:
            # Trouve l'index du film
            movie_idx = self.movie_data[self.movie_data['id'] == movie_id].index
            if len(movie_idx) == 0:
                print(f"❌ Film avec ID {movie_id} non trouvé")
                return []
            
            movie_idx = movie_idx[0]
            
            # Trouve les films similaires
            distances, indices = self.knn_model.kneighbors(
                self.tfidf_matrix[movie_idx], 
                n_neighbors=n_recommendations + 1
            )
            
            # Exclut le film lui-même
            similar_indices = indices[0][1:]
            similar_distances = distances[0][1:]
            
            recommendations = []
            for idx, distance in zip(similar_indices, similar_distances):
                movie = self.movie_data.iloc[idx]
                similarity_score = 1 - distance  # Convertit distance en similarité
                
                recommendations.append({
                    'movie_id': int(movie['id']),
                    'title': movie['title'],
                    'genres': movie['genre'],  # Adapté au champ 'genre'
                    'vote_average': float(movie['rating']) if movie['rating'] else 0,
                    'release_date': movie['release_date'],
                    'similarity_score': float(similarity_score)
                })
            
            return recommendations
            
        except Exception as e:
            print(f"❌ Erreur lors des recommandations: {e}")
            return []
    
    def get_recommendations_by_query(self, query, n_recommendations=10):
        """Recommande des films basés sur une requête textuelle."""
        
        if not self.is_trained:
            if not self.train_model():
                return []
        
        try:
            # Normalise la requête pour améliorer les correspondances
            normalized_query = normalize_text(query)
            
            # Essaie d'abord une recherche directe dans les titres
            direct_matches = self.movie_data[
                self.movie_data['title'].str.contains(query, case=False, na=False) |
                self.movie_data['title'].apply(lambda x: normalized_query in normalize_text(x) if x else False)
            ]
            
            # Si on trouve des correspondances directes, les inclut
            recommendations = []
            if not direct_matches.empty:
                for _, movie in direct_matches.head(min(3, n_recommendations)).iterrows():
                    recommendations.append({
                        'movie_id': int(movie['id']),
                        'title': movie['title'],
                        'genres': movie['genre'],
                        'vote_average': float(movie['rating']) if movie['rating'] else 0,
                        'release_date': movie['release_date'],
                        'similarity_score': 0.95  # Score élevé pour correspondance directe
                    })
            
            # Complète avec recherche TF-IDF sémantique
            remaining_slots = n_recommendations - len(recommendations)
            if remaining_slots > 0:
                # Vectorise la requête normalisée
                search_text = f"{query} {normalized_query}"  # Combine original et normalisé
                query_vector = self.vectorizer.transform([search_text])
                
                # Trouve les films similaires
                distances, indices = self.knn_model.kneighbors(
                    query_vector, 
                    n_neighbors=remaining_slots + 5  # Cherche plus pour filtrer
                )
                
                similar_indices = indices[0]
                similar_distances = distances[0]
                
                # Ajoute les recommandations sémantiques (évite les doublons)
                existing_ids = {rec['movie_id'] for rec in recommendations}
                
                for idx, distance in zip(similar_indices, similar_distances):
                    if len(recommendations) >= n_recommendations:
                        break
                        
                    movie = self.movie_data.iloc[idx]
                    movie_id = int(movie['id'])
                    similarity_score = 1 - distance
                    
                    # Évite les doublons et filtre scores trop bas
                    if movie_id not in existing_ids and similarity_score > 0.1:
                        recommendations.append({
                            'movie_id': movie_id,
                            'title': movie['title'],
                            'genres': movie['genre'],
                            'vote_average': float(movie['rating']) if movie['rating'] else 0,
                            'release_date': movie['release_date'],
                            'similarity_score': float(similarity_score)
                        })
                        existing_ids.add(movie_id)
            
            # Trie par score de similarité décroissant
            recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)
            return recommendations[:n_recommendations]
            
        except Exception as e:
            print(f"❌ Erreur lors des recommandations par requête: {e}")
            return []
            
        except Exception as e:
            print(f"❌ Erreur lors des recommandations par requête: {e}")
            return []
    
    def get_trending_movies(self, n_movies=10):
        """Retourne les films tendance (mélange popularité + note)."""
        
        if not self.is_trained:
            if not self.train_model():
                return []
        
        try:
            # Score composite : 70% note + 30% popularité (basé sur rating)
            movies_copy = self.movie_data.copy()
            movies_copy['normalized_rating'] = movies_copy['rating'].fillna(0) / 10
            
            # Utilise la rating comme popularité approximative
            max_rating = movies_copy['rating'].max() if movies_copy['rating'].max() else 10
            movies_copy['normalized_popularity'] = (
                movies_copy['rating'].fillna(0) / max_rating
            )
            movies_copy['trending_score'] = (
                0.7 * movies_copy['normalized_rating'] + 
                0.3 * movies_copy['normalized_popularity']
            )
            
            # Filtre les films avec note minimum
            trending = movies_copy[movies_copy['rating'] >= 6.0]
            trending = trending.sort_values('trending_score', ascending=False)
            
            recommendations = []
            for _, movie in trending.head(n_movies).iterrows():
                recommendations.append({
                    'movie_id': int(movie['id']),
                    'title': movie['title'],
                    'genres': movie['genre'],  # Adapté au champ 'genre'
                    'vote_average': float(movie['rating']) if movie['rating'] else 0,
                    'release_date': movie['release_date'],
                    'trending_score': float(movie['trending_score'])
                })
            
            return recommendations
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des tendances: {e}")
            return []

# Instance globale du recommender
cinetopia_recommender = CinetopiaRecommender()

def get_movie_recommendations(movie_id=None, query=None, n_recommendations=10):
    """
    Interface principale pour obtenir des recommandations.
    
    Args:
        movie_id: ID d'un film pour recommandations similaires
        query: Requête textuelle pour recherche sémantique
        n_recommendations: Nombre de recommandations
    
    Returns:
        Liste de dictionnaires avec les films recommandés
    """
    
    if movie_id:
        return cinetopia_recommender.get_recommendations_by_movie_id(
            movie_id, n_recommendations
        )
    elif query:
        return cinetopia_recommender.get_recommendations_by_query(
            query, n_recommendations
        )
    else:
        return cinetopia_recommender.get_trending_movies(n_recommendations)

def force_retrain_model():
    """Force le réentraînement du modèle."""
    cinetopia_recommender.is_trained = False
    return cinetopia_recommender.train_model()