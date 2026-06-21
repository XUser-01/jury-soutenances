from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Memoire, Enseignant, Disponibilite, Salle, Soutenance, Jury, Session
from .algo import generer_planning, replanifier

@login_required
def index(request):
    if request.user.is_staff:
        sessions = Session.objects.all()
        return render(request, 'planification/index.html', {
            'sessions': sessions,
            'is_admin': True
        })
    sessions = Session.objects.all()
    return render(request, 'planification/index.html', {
        'sessions': sessions,
        'is_admin': False
    })

@login_required
def lancer_planning(request, session_id):
    if not request.user.is_staff:
        return redirect('index')
    deja_planifie = Soutenance.objects.filter(
        memoire__session_id=session_id
    ).exists()
    if not deja_planifie:
        generer_planning(session_id)
    return redirect('planning', session_id=session_id)

@login_required
def afficher_planning(request, session_id):
    if request.user.is_staff:
        soutenances = Soutenance.objects.filter(
            memoire__session_id=session_id
        ).select_related('memoire', 'salle', 'memoire__etudiant').order_by('jour', 'heure_debut')
    else:
        try:
            enseignant = Enseignant.objects.get(user=request.user)
            soutenances = Soutenance.objects.filter(
                memoire__session_id=session_id,
                jury__enseignant=enseignant
            ).select_related('memoire', 'salle', 'memoire__etudiant').order_by('jour', 'heure_debut')
        except Enseignant.DoesNotExist:
            soutenances = []

    planning = []
    for s in soutenances:
        jurys = Jury.objects.filter(soutenance=s).select_related('enseignant')
        planning.append({
            'soutenance': s,
            'jurys': jurys
        })

    message = request.session.pop('message', None)

    return render(request, 'planification/planning.html', {
        'planning': planning,
        'session_id': session_id,
        'is_admin': request.user.is_staff,
        'message': message
    })

@login_required
def valider_soutenance(request, soutenance_id):
    soutenance = get_object_or_404(Soutenance, id=soutenance_id)
    soutenance.statut = 'validee'
    soutenance.save()
    return redirect('planning', session_id=soutenance.memoire.session_id)

@login_required
def rejeter_soutenance(request, soutenance_id):
    soutenance = get_object_or_404(Soutenance, id=soutenance_id)
    session_id = soutenance.memoire.session_id
    memoire_titre = soutenance.memoire.titre
    soutenance.statut = 'rejetee'
    soutenance.save()
    replanifier(session_id)

    nouvelle = Soutenance.objects.filter(
        memoire__titre=memoire_titre,
        statut='planifiee'
    ).exists()

    if nouvelle:
        message = f"✅ '{memoire_titre}' a été replanifié avec succès."
    else:
        message = f"⚠️ '{memoire_titre}' n'a pas pu être replanifié — aucun créneau disponible."

    request.session['message'] = message
    return redirect('planning', session_id=session_id)

@login_required
def saisir_resultats(request, soutenance_id):
    if not request.user.is_staff:
        return redirect('index')

    soutenance = get_object_or_404(Soutenance, id=soutenance_id)
    jurys = Jury.objects.filter(soutenance=soutenance).select_related('enseignant')

    if request.method == 'POST':
        soutenance.note = request.POST.get('note')
        soutenance.decision = request.POST.get('decision')
        soutenance.observations = request.POST.get('observations')
        soutenance.statut = 'terminee'
        soutenance.save()

        for jury in jurys:
            present = request.POST.get(f'present_{jury.id}')
            jury.present = present == 'on'
            jury.save()

        return redirect('planning', session_id=soutenance.memoire.session_id)

    return render(request, 'planification/resultats.html', {
        'soutenance': soutenance,
        'jurys': jurys
    })