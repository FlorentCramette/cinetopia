
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
import logging

from .forms import LoginForm, SignUpForm, MovieRecommendationForm
from .recommender_engine import get_movie_recommendations
from .models import Movie

logger = logging.getLogger(__name__)


@csrf_protect
def login_view(request):
    """Vue d'accueil unifiée avec authentification."""
    # Gestion de la déconnexion
    if request.GET.get('logout') == '1':
        logout(request)
        messages.success(request, 'Vous avez été déconnecté avec succès.')
        return redirect('login')
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'login':
            form = LoginForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                user = authenticate(request, username=username, password=password)
                
                if user is not None:
                    login(request, user)
                    messages.success(request, f'Bienvenue {user.username}! Connexion réussie.')
                    return redirect('home')
                else:
                    messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
        
        elif form_type == 'signup':
            # Traiter l'inscription directement ici
            username = request.POST.get('username')
            email = request.POST.get('email')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            # Validation basique
            if password1 != password2:
                messages.error(request, 'Les mots de passe ne correspondent pas.')
            elif len(password1) < 6:
                messages.error(request, 'Le mot de passe doit contenir au moins 6 caractères.')
            elif User.objects.filter(username=username).exists():
                messages.error(request, 'Ce nom d\'utilisateur existe déjà.')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Cette adresse email est déjà utilisée.')
            else:
                # Créer l'utilisateur
                try:
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password1
                    )
                    messages.success(request, f'Compte créé avec succès! Bienvenue {username}.')
                    # Connecter automatiquement l'utilisateur
                    login(request, user)
                    return redirect('login')  # Reste sur la page unifiée après inscription
                except Exception as e:
                    messages.error(request, f'Erreur lors de la création du compte: {str(e)}')
    
    return render(request, 'unified_home.html')


@csrf_protect
def signup_view(request):
    """Vue d'inscription - redirige vers la page principale."""
    return redirect('login')


@login_required
def home_view(request):
    """Vue de la page d'accueil (maintenant unified_home.html)."""
    context = {
        'user': request.user,
    }
    return render(request, 'unified_home.html', context)


@login_required  
def movie_view(request):
    """Vue pour la recherche de films."""
    if request.method == 'POST':
        query = request.POST.get('query', '')
        if query:
            return redirect(f'/results/?q={query}')
    
    return render(request, 'movie.html')


@login_required
def results_view(request):
    """Vue des résultats de recommandation ML."""
    query = request.GET.get('q', '')
    movie_id = request.GET.get('movie_id')
    
    if not query and not movie_id:
        messages.error(request, 'Aucune recherche spécifiée.')
        return redirect('login')
    
    try:
        # Obtenir les recommandations via notre moteur ML
        if movie_id:
            recommendations = get_movie_recommendations(movie_id=int(movie_id), n_recommendations=6)
            movie = get_object_or_404(Movie, id=movie_id)
            context_title = f"Films similaires à {movie.title}"
        else:
            recommendations = get_movie_recommendations(query=query, n_recommendations=6)
            context_title = f"Recommandations pour '{query}'"
        
        # Enrichir les données et éliminer les doublons
        enriched_recommendations = []
        seen_titles = set()
        seen_ids = set()
        
        for rec in recommendations:
            try:
                movie_db = Movie.objects.get(id=rec['movie_id'])
                normalized_title = rec['title'].lower().strip()
                
                # Éviter les doublons et limiter à 3 résultats
                if (rec['movie_id'] not in seen_ids and 
                    normalized_title not in seen_titles and 
                    len(enriched_recommendations) < 3):
                    
                    # Enrichir avec les données de la DB
                    rec['genres_list'] = rec['genres'].split('|') if rec['genres'] else []
                    rec['poster_url'] = movie_db.image_url
                    rec['overview'] = movie_db.description
                    rec['vote_average'] = movie_db.rating
                    rec['release_date'] = movie_db.release_date
                    rec['director'] = movie_db.director
                    rec['actors'] = movie_db.actors
                    
                    # Assurer que le similarity_score est présent (converti en pourcentage)
                    if 'similarity_score' in rec:
                        rec['similarity_score'] = int(rec['similarity_score'] * 100)
                    else:
                        rec['similarity_score'] = 0
                    
                    enriched_recommendations.append(rec)
                    seen_ids.add(rec['movie_id'])
                    seen_titles.add(normalized_title)
                    
            except Movie.DoesNotExist:
                continue
        
        context = {
            'recommendations': enriched_recommendations,
            'query': query,
            'movie_title': context_title,
            'total_found': len(enriched_recommendations)
        }
        
        print(f"DEBUG: Context clés: {list(context.keys())}")
        print(f"DEBUG: Longueur context['recommendations']: {len(context['recommendations'])}")
        if context['recommendations']:
            print(f"DEBUG: Premier film: {context['recommendations'][0]['title']}")
            print(f"DEBUG: Premier film poster_url: {context['recommendations'][0].get('poster_url', 'MANQUANT')}")
        
        return render(request, 'results.html', context)
        
    except Exception as e:
        logger.error(f"Erreur lors des recommandations: {e}")
        messages.error(request, 'Une erreur est survenue lors de la recherche.')
        return redirect('login')


@login_required
def recommend_view(request):
    """API pour recommandations ML."""
    if request.method == 'POST':
        query = request.POST.get('query', '')
        movie_id = request.POST.get('movie_id')
        
        try:
            if movie_id:
                recommendations = get_movie_recommendations(movie_id=movie_id, n_recommendations=10)
            elif query:
                recommendations = get_movie_recommendations(query=query, n_recommendations=10)
            else:
                recommendations = get_movie_recommendations(n_recommendations=10)  # Tendances
            
            return JsonResponse({
                'success': True,
                'recommendations': recommendations
            })
            
        except Exception as e:
            logger.error(f"Erreur API recommandation: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Erreur lors de la recherche.'
            })
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

def test_background(request):
    """Page de test pour vérifier le background."""
    return render(request, 'test_background.html')