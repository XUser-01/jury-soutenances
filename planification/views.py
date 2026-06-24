import csv

from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Memoire, Enseignant, Salle, Soutenance, Jury, Session
from .algo import generer_planning, replanifier


@login_required
def index(request):
    sessions = Session.objects.annotate(
        total_memoires=Count('memoire', distinct=True),
        total_soutenances=Count('memoire__soutenance', distinct=True),
        terminees=Count(
            'memoire__soutenance',
            filter=Q(memoire__soutenance__statut='terminee'),
            distinct=True,
        ),
        validees=Count(
            'memoire__soutenance',
            filter=Q(memoire__soutenance__statut='validee'),
            distinct=True,
        ),
    ).order_by('-date_debut')

    stats = {
        'sessions': sessions.count(),
        'memoires': Memoire.objects.count(),
        'enseignants': Enseignant.objects.count(),
        'salles': Salle.objects.count(),
        'soutenances': Soutenance.objects.count(),
        'terminees': Soutenance.objects.filter(statut='terminee').count(),
    }

    return render(request, 'planification/index.html', {
        'sessions': sessions,
        'stats': stats,
        'is_admin': request.user.is_staff,
    })


@login_required
@require_POST
def lancer_planning(request, session_id):
    if not request.user.is_staff:
        return redirect('index')

    deja_planifie = Soutenance.objects.filter(
        memoire__session_id=session_id
    ).exists()

    if not deja_planifie:
        generer_planning(session_id)
        request.session['message'] = "Planning genere avec succes."
    else:
        request.session['message'] = "Cette session possede deja un planning."

    return redirect('planning', session_id=session_id)


@login_required
def afficher_planning(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    statut = request.GET.get('statut', '').strip()
    q = request.GET.get('q', '').strip()

    if request.user.is_staff:
        soutenances = Soutenance.objects.filter(memoire__session_id=session_id)
    else:
        try:
            enseignant = Enseignant.objects.get(user=request.user)
            soutenances = Soutenance.objects.filter(
                memoire__session_id=session_id,
                jury__enseignant=enseignant,
            )
        except Enseignant.DoesNotExist:
            soutenances = Soutenance.objects.none()

    if statut:
        soutenances = soutenances.filter(statut=statut)

    if q:
        soutenances = soutenances.filter(
            Q(memoire__titre__icontains=q)
            | Q(memoire__etudiant__nom__icontains=q)
            | Q(memoire__etudiant__prenom__icontains=q)
            | Q(memoire__specialite__icontains=q)
            | Q(salle__nom__icontains=q)
        )

    soutenances = soutenances.select_related(
        'memoire',
        'salle',
        'memoire__etudiant',
    ).prefetch_related('jury_set__enseignant').order_by('jour', 'heure_debut', 'salle__nom')

    stats = {
        'total': soutenances.count(),
        'planifiees': soutenances.filter(statut='planifiee').count(),
        'validees': soutenances.filter(statut='validee').count(),
        'terminees': soutenances.filter(statut='terminee').count(),
    }

    planning = []
    for soutenance in soutenances:
        planning.append({
            'soutenance': soutenance,
            'jurys': soutenance.jury_set.all(),
        })

    message = request.session.pop('message', None)

    return render(request, 'planification/planning.html', {
        'planning': planning,
        'session': session,
        'session_id': session_id,
        'is_admin': request.user.is_staff,
        'message': message,
        'stats': stats,
        'selected_statut': statut,
        'search_query': q,
        'statut_choices': Soutenance.STATUT_CHOICES,
    })


@login_required
@require_POST
def valider_soutenance(request, soutenance_id):
    if not request.user.is_staff:
        return redirect('index')

    soutenance = get_object_or_404(Soutenance, id=soutenance_id)
    soutenance.statut = 'validee'
    soutenance.save(update_fields=['statut'])
    request.session['message'] = "Soutenance validee."
    return redirect('planning', session_id=soutenance.memoire.session_id)


@login_required
@require_POST
def rejeter_soutenance(request, soutenance_id):
    if not request.user.is_staff:
        return redirect('index')

    soutenance = get_object_or_404(Soutenance, id=soutenance_id)
    session_id = soutenance.memoire.session_id
    memoire_titre = soutenance.memoire.titre
    soutenance.statut = 'rejetee'
    soutenance.save(update_fields=['statut'])
    replanifier(session_id)

    nouvelle = Soutenance.objects.filter(
        memoire__titre=memoire_titre,
        statut='planifiee',
    ).exists()

    if nouvelle:
        message = f"'{memoire_titre}' a ete replanifie avec succes."
    else:
        message = f"'{memoire_titre}' n'a pas pu etre replanifie : aucun creneau disponible."

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
            jury.save(update_fields=['present'])

        request.session['message'] = "Resultats enregistres."
        return redirect('planning', session_id=soutenance.memoire.session_id)

    return render(request, 'planification/resultats.html', {
        'soutenance': soutenance,
        'jurys': jurys,
    })


@login_required
def exporter_planning(request, session_id):
    if not request.user.is_staff:
        return redirect('index')

    session = get_object_or_404(Session, id=session_id)
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="planning_session_{session_id}.csv"'
    response.write('\ufeff')

    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'Session', 'Date', 'Debut', 'Fin', 'Salle', 'Etudiant',
        'Memoire', 'Specialite', 'Jury', 'Statut', 'Note', 'Decision',
    ])

    soutenances = Soutenance.objects.filter(
        memoire__session=session,
    ).select_related(
        'memoire', 'memoire__etudiant', 'salle',
    ).prefetch_related('jury_set__enseignant').order_by('jour', 'heure_debut')

    for soutenance in soutenances:
        jurys = ', '.join(str(jury.enseignant) for jury in soutenance.jury_set.all())
        writer.writerow([
            session.libelle,
            soutenance.jour.strftime('%d/%m/%Y'),
            soutenance.heure_debut.strftime('%H:%M'),
            soutenance.heure_fin.strftime('%H:%M'),
            soutenance.salle.nom,
            str(soutenance.memoire.etudiant),
            soutenance.memoire.titre,
            soutenance.memoire.specialite,
            jurys,
            soutenance.get_statut_display(),
            soutenance.note if soutenance.note is not None else '',
            soutenance.get_decision_display() if soutenance.decision else '',
        ])

    return response
