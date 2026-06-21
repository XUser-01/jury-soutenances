from django.contrib import admin
from .models import Session, Enseignant, Etudiant, Salle, Memoire, Disponibilite, Soutenance, Jury

from django.contrib.admin import AdminSite

# Personnalisation de l'admin
admin.site.site_header = "Gestion des Jurys de Soutenances - ESI"
admin.site.site_title = "Administration ESI"
admin.site.index_title = "Tableau de bord"

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'date_debut', 'date_fin', 'statut')
    list_filter = ('statut',)

@admin.register(Enseignant)
class EnseignantAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'specialite', 'grade', 'email')
    search_fields = ('nom', 'prenom', 'specialite')

@admin.register(Etudiant)
class EtudiantAdmin(admin.ModelAdmin):
    list_display = ('matricule', 'nom', 'prenom', 'filiere', 'niveau')
    search_fields = ('nom', 'prenom', 'matricule')

@admin.register(Salle)
class SalleAdmin(admin.ModelAdmin):
    list_display = ('nom', 'capacite', 'batiment')

@admin.register(Memoire)
class MemoireAdmin(admin.ModelAdmin):
    list_display = ('titre', 'etudiant', 'specialite', 'type', 'statut', 'session')
    list_filter = ('specialite', 'statut', 'session')
    search_fields = ('titre',)

@admin.register(Disponibilite)
class DisponibiliteAdmin(admin.ModelAdmin):
    list_display = ('enseignant', 'jour', 'heure_debut', 'heure_fin', 'session')
    list_filter = ('enseignant', 'session')

@admin.register(Soutenance)
class SoutenanceAdmin(admin.ModelAdmin):
    list_display = ('memoire', 'jour', 'heure_debut', 'salle', 'statut', 'note', 'decision')
    list_filter = ('statut', 'jour')

@admin.register(Jury)
class JuryAdmin(admin.ModelAdmin):
    list_display = ('soutenance', 'enseignant', 'present')
    list_filter = ('present',)