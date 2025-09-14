from django.db import models
from django.urls import reverse


class Movie(models.Model):
    """Modèle représentant un film."""
    
    title = models.CharField(
        max_length=255, 
        verbose_name="Titre",
        help_text="Titre du film"
    )
    description = models.TextField(
        verbose_name="Description",
        help_text="Synopsis du film"
    )
    image_url = models.URLField(
        verbose_name="URL de l'affiche",
        help_text="Lien vers l'affiche du film"
    )
    release_date = models.DateField(
        verbose_name="Date de sortie",
        help_text="Date de sortie du film"
    )
    director = models.CharField(
        max_length=255,
        verbose_name="Réalisateur",
        blank=True,
        null=True
    )
    actors = models.TextField(
        verbose_name="Acteurs",
        blank=True,
        null=True,
        help_text="Liste des acteurs principaux"
    )
    genre = models.CharField(
        max_length=255,
        verbose_name="Genre",
        blank=True,
        null=True
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        verbose_name="Note",
        blank=True,
        null=True,
        help_text="Note du film (ex: 7.5)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Film"
        verbose_name_plural = "Films"
        ordering = ['-release_date']

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('movie_detail', kwargs={'pk': self.pk})