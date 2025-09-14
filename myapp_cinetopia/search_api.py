"""
🔍 API de recherche Netflix-like pour Cinetopia
Suggestions de titres en temps réel avec autocomplete
"""

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from .models import Movie
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET"])
def search_autocomplete(request):
    """API pour suggestions de recherche en temps réel."""
    
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:  # Minimum 2 caractères pour déclencher la recherche
        return JsonResponse({
            'success': True,
            'suggestions': []
        })
    
    try:
        # Recherche UNIQUEMENT dans les titres pour une correspondance exacte
        movies = Movie.objects.filter(
            Q(title__icontains=query)
        ).values(
            'id', 'title', 'genre', 'director', 'image_url', 'rating', 'release_date'
        )[:10]  # Limite à 10 suggestions
        
        suggestions = []
        for movie in movies:
            suggestions.append({
                'id': movie['id'],
                'title': movie['title'],
                'year': movie['release_date'].year if movie['release_date'] else 'N/A',
                'genre': movie['genre'] or 'Non défini',
                'director': movie['director'] or 'Inconnu',
                'poster': movie['image_url'] or '',
                'rating': float(movie['rating']) if movie['rating'] else 0,
                'match_type': "titre"  # Toujours titre maintenant
            })
        
        return JsonResponse({
            'success': True,
            'suggestions': suggestions,
            'query': query,
            'total': len(suggestions)
        })
        
    except Exception as e:
        logger.error(f"Erreur recherche autocomplete: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Erreur lors de la recherche'
        })

@csrf_exempt 
@require_http_methods(["GET"])
def search_by_title(request):
    """Recherche précise par titre de film."""
    
    title = request.GET.get('title', '').strip()
    
    if not title:
        return JsonResponse({
            'success': False,
            'error': 'Titre manquant'
        })
    
    try:
        # Recherche exacte puis floue
        movie = Movie.objects.filter(title__iexact=title).first()
        
        if not movie:
            # Recherche floue si pas de match exact
            movie = Movie.objects.filter(title__icontains=title).first()
        
        if movie:
            movie_data = {
                'id': movie.id,
                'title': movie.title,
                'description': movie.description,
                'year': movie.release_date.year if movie.release_date else 'N/A',
                'genre': movie.genre or 'Non défini',
                'director': movie.director or 'Inconnu',
                'actors': movie.actors or 'Non défini',
                'poster': movie.image_url or '',
                'rating': float(movie.rating) if movie.rating else 0,
                'release_date': movie.release_date.isoformat() if movie.release_date else None
            }
            
            return JsonResponse({
                'success': True,
                'movie': movie_data
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'Film "{title}" non trouvé'
            })
            
    except Exception as e:
        logger.error(f"Erreur recherche par titre: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Erreur lors de la recherche'
        })

@csrf_exempt
@require_http_methods(["GET"])
def get_popular_searches(request):
    """Retourne les recherches populaires du moment."""
    
    try:
        # Films populaires basés sur la note
        popular_movies = Movie.objects.filter(
            rating__gte=7.0
        ).order_by('-rating').values(
            'title', 'genre', 'rating'
        )[:8]
        
        popular_searches = []
        for movie in popular_movies:
            popular_searches.append({
                'title': movie['title'],
                'genre': movie['genre'] or 'Film français',
                'rating': float(movie['rating']) if movie['rating'] else 0
            })
        
        return JsonResponse({
            'success': True,
            'popular_searches': popular_searches
        })
        
    except Exception as e:
        logger.error(f"Erreur recherches populaires: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Erreur lors de la récupération'
        })