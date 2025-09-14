import os
from pathlib import Path
from django.conf import settings
from cinetopia.config import WEATHER_API_KEY, WEATHER_API_HOST
import requests
import logging

# Imports optionnels pour ML
try:
    import pandas as pd
    import re
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.neighbors import NearestNeighbors
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    pd = None

logger = logging.getLogger(__name__)


class MovieRecommendationService:
    """Service de recommandation de films."""
    
    def __init__(self):
        self.data = None
        self.knn = None
        self.vectorizer = None
        self.data_vectorized = None
        self.ml_available = ML_AVAILABLE
        
        if self.ml_available:
            try:
                self._load_data()
            except Exception as e:
                logger.error(f"Erreur lors du chargement des données ML: {e}")
                self.ml_available = False
        else:
            logger.warning("Packages ML non disponibles - recommandations désactivées")
    
    def _load_data(self):
        """Charge et prépare les données de films."""
        if not self.ml_available:
            return
            
        try:
            data_path = Path(settings.BASE_DIR) / 'myapp_cinetopia' / 'data' / 'french_movies_with_keywords.csv'
            df = pd.read_csv(data_path)
            
            # Renommer les colonnes problématiques
            df = df.rename(columns={'Lien de l\'affiche': 'Lien_de_l_affiche'})
            df.columns = [col.replace(' ', '_') for col in df.columns]
            
            self.data = df.copy()
            self._preprocess_data()
            self._train_model()
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données: {e}")
            self.ml_available = False
            raise
    
    def _preprocess_data(self):
        """Préprocesse les données."""
        # Nettoyage des mots-clés
        self.data['keywords'] = self.data['keywords'].apply(self._clean_text)
        self.data = self.data.fillna('')
        
        # Combinaison des caractéristiques
        self.data['combined_features'] = self.data.apply(self._combine_features, axis=1)
    
    def _clean_text(self, text):
        """Nettoie le texte."""
        if isinstance(text, str):
            text = re.sub(r'\bid\b|\bname\b|\d+', '', text)
        return text
    
    def _combine_features(self, row):
        """Combine les caractéristiques d'un film."""
        genres = row.get('Genre', '') * 2
        acteurs = row.get('Noms_de_tous_les_acteurs', '')
        director = row.get('Nom_du_réalisateur', '') * 2
        synopsis = row.get('Synopsis', '') * 2
        note = str(row.get('Note', ''))
        date = str(row.get('Date_de_sortie', '')) * 2
        keywords = row.get('keywords', '')
        
        return f'{acteurs} {director} {genres} {synopsis} {note} {date} {keywords}'
    
    def _train_model(self):
        """Entraîne le modèle de recommandation."""
        self.vectorizer = TfidfVectorizer()
        self.data_vectorized = self.vectorizer.fit_transform(self.data['combined_features'])
        
        self.knn = NearestNeighbors(metric='cosine', algorithm='brute')
        self.knn.fit(self.data_vectorized)
    
    def recommend_movies(self, movie_name, n_neighbors=10):
        """Recommande des films similaires."""
        if not self.ml_available:
            return None, "Les recommandations ML ne sont pas disponibles. Veuillez installer pandas et scikit-learn."
        
        movie_name_lower = movie_name.lower()
        self.data['Nom_lower'] = self.data['Nom'].str.lower()
        
        if movie_name_lower not in self.data['Nom_lower'].values:
            return None, f"Le film '{movie_name}' n'est pas présent dans la base de données."
        
        try:
            movie_index = self.data[self.data['Nom_lower'] == movie_name_lower].index[0]
            distances, indices = self.knn.kneighbors(
                self.data_vectorized[movie_index], 
                n_neighbors=n_neighbors
            )
            
            # Créer le DataFrame des recommandations
            recommended_movies = pd.DataFrame({
                'Nom': self.data['Nom'].iloc[indices[0]], 
                'Distance': distances[0]
            })
            
            # Ajouter les informations supplémentaires
            columns_to_add = [
                'Lien_de_l_affiche', 'Nom_du_réalisateur', 
                'Noms_de_tous_les_acteurs', 'Synopsis'
            ]
            
            for col in columns_to_add:
                if col in self.data.columns:
                    if col == 'Noms_de_tous_les_acteurs':
                        recommended_movies[col] = self.data[col].iloc[indices[0]].apply(
                            lambda x: ' '.join(str(x).split()[:10])
                        )
                    else:
                        recommended_movies[col] = self.data[col].iloc[indices[0]]
            
            # Supprimer les doublons et le film original
            recommended_movies.drop_duplicates(subset='Nom', keep='first', inplace=True)
            recommended_movies = recommended_movies[
                recommended_movies['Nom'] != self.data['Nom'].iloc[movie_index]
            ]
            recommended_movies.sort_values(by='Distance', inplace=True)
            
            # Informations du film recherché
            movie_info = self.data.loc[movie_index, [
                'Nom', 'Lien_de_l_affiche', 'Nom_du_réalisateur', 
                'Noms_de_tous_les_acteurs', 'Synopsis'
            ]].copy()
            
            if 'Noms_de_tous_les_acteurs' in movie_info:
                movie_info['Noms_de_tous_les_acteurs'] = ' '.join(
                    str(movie_info['Noms_de_tous_les_acteurs']).split()[:10]
                )
            
            # Convertir en dictionnaires
            recommended_movies_dict = recommended_movies[[
                'Nom', 'Lien_de_l_affiche', 'Nom_du_réalisateur', 
                'Noms_de_tous_les_acteurs', 'Synopsis'
            ]].to_dict('records')
            
            movie_info_dict = movie_info.to_dict()
            
            return recommended_movies_dict, movie_info_dict
            
        except Exception as e:
            logger.error(f"Erreur lors de la recommandation: {e}")
            return None, f"Erreur lors de la recommandation: {str(e)}"


class WeatherService:
    """Service pour récupérer les données météo."""
    
    def __init__(self):
        self.api_key = WEATHER_API_KEY
        self.api_host = WEATHER_API_HOST
        self.base_url = "https://weatherapi-com.p.rapidapi.com/forecast.json"
    
    def get_weather_data(self, city="Limoges", days=3, lang="fr"):
        """Récupère les données météo pour une ville."""
        if not self.api_key:
            logger.warning("Clé API météo non configurée")
            return None
        
        try:
            headers = {
                "X-RapidAPI-Key": self.api_key,
                "X-RapidAPI-Host": self.api_host
            }
            
            params = {
                "q": city,
                "days": days,
                "lang": lang
            }
            
            response = requests.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération des données météo: {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur inattendue: {e}")
            return None


# Instances globales pour éviter de recharger les données
try:
    movie_service = MovieRecommendationService()
    weather_service = WeatherService()
except Exception as e:
    logger.error(f"Erreur lors de l'initialisation des services: {e}")
    # Créer des services de fallback
    movie_service = None
    weather_service = WeatherService()