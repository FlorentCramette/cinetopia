
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
import logging

from .forms import LoginForm, SignUpForm, MovieRecommendationForm
from .services import movie_service, weather_service

logger = logging.getLogger(__name__)


@csrf_protect
def login_view(request):
    """Vue de connexion."""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, 'Connexion réussie!')
                return redirect('home')
            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})


@csrf_protect
def signup_view(request):
    """Vue d'inscription."""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Compte créé pour {username}!')
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    
    return render(request, 'signup.html', {'form': form})


@login_required
def home_view(request):
    """Vue de la page d'accueil."""
    weather_data = weather_service.get_weather_data()
    
    context = {
        'user': request.user,
        'weather_data': weather_data,
    }
    return render(request, 'home.html', context)


@login_required
def movie_view(request):
    """Vue pour la recherche de films."""
    if request.method == 'POST':
        form = MovieRecommendationForm(request.POST)
        if form.is_valid():
            movie_name = form.cleaned_data['movie_name']
            request.session['movie_name'] = movie_name
            return redirect('results')
    else:
        form = MovieRecommendationForm()
    
    return render(request, 'movie.html', {'form': form})


@login_required
def results_view(request):
    """Vue des résultats de recommandation."""
    movie_name = request.session.get('movie_name', '')
    
    if not movie_name:
        messages.error(request, 'Aucun film recherché.')
        return redirect('movie')
    
    try:
        recommended_movies, movie_info = movie_service.recommend_movies(movie_name)
        
        if recommended_movies is None:
            messages.error(request, movie_info)  # movie_info contient le message d'erreur
            return redirect('movie')
        
        context = {
            'recommended_movies': recommended_movies,
            'movie_info': movie_info,
            'movie_name': movie_name,
        }
        
        return render(request, 'results.html', context)
        
    except Exception as e:
        logger.error(f"Erreur lors de la recommandation pour '{movie_name}': {e}")
        messages.error(request, 'Une erreur est survenue lors de la recherche.')
        return redirect('movie')


@login_required
def recommend_view(request):
    """Vue de recommandation (alternative)."""
    if request.method == 'POST':
        form = MovieRecommendationForm(request.POST)
        if form.is_valid():
            movie_name = form.cleaned_data['movie_name']
            
            try:
                recommended_movies, movie_info = movie_service.recommend_movies(movie_name)
                
                if recommended_movies is None:
                    return JsonResponse({
                        'success': False,
                        'error': movie_info
                    })
                
                return JsonResponse({
                    'success': True,
                    'recommended_movies': recommended_movies,
                    'movie_info': movie_info
                })
                
            except Exception as e:
                logger.error(f"Erreur API recommandation: {e}")
                return JsonResponse({
                    'success': False,
                    'error': 'Erreur lors de la recherche.'
                })
    else:
        form = MovieRecommendationForm()
    
    return render(request, 'recommend.html', {'form': form})