from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('session/<int:session_id>/lancer/', views.lancer_planning, name='lancer_planning'),
    path('session/<int:session_id>/planning/', views.afficher_planning, name='planning'),
    path('soutenance/<int:soutenance_id>/valider/', views.valider_soutenance, name='valider_soutenance'),
    path('soutenance/<int:soutenance_id>/rejeter/', views.rejeter_soutenance, name='rejeter_soutenance'),
    path('soutenance/<int:soutenance_id>/resultats/', views.saisir_resultats, name='saisir_resultats'),
]