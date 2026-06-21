from planification.models import Memoire, Enseignant, Disponibilite, Salle, Soutenance, Jury
import datetime


def generer_planning(session_id, memoires_cibles=None):

    # 1- Recuperer les donnees de la session
    if memoires_cibles is None:
        memoires = Memoire.objects.filter(session_id=session_id)
    else:
        memoires = memoires_cibles

    enseignants = Enseignant.objects.all()
    dispo = Disponibilite.objects.filter(session_id=session_id)
    salles = Salle.objects.all()

    # 1.1 definir la rarete des specialites
    compteur = {}

    for enseignant in enseignants:
        compteur[enseignant.specialite] = compteur.get(enseignant.specialite, 0) + 1

    # Trier les memoires
    memoires_tries = sorted(
        memoires,
        key=lambda objet_memoire: compteur.get(objet_memoire.specialite, 0)
    )

    # 2- Trouver pour chaque memoire les profs possibles
    for memoire in memoires_tries:

        creneaux = {}
        membre_jury = []
        creneau_choisi = None

        candidat_juris = [
            enseignant
            for enseignant in enseignants
            if enseignant.specialite == memoire.specialite
        ]

        # 3- Chercher les profs disponibles et non occupes
        for disp in dispo:

            cle = (disp.jour, disp.heure_debut, disp.heure_fin)

            jour, heure_debut, heure_fin = cle

            soutenances_au_meme_creneau = Soutenance.objects.filter(
                jour=jour,
                heure_debut=heure_debut,
                heure_fin=heure_fin
            )

            profs_occupes = Jury.objects.filter(
                soutenance__in=soutenances_au_meme_creneau
            )

            liste_profs = [
                candidat
                for candidat in candidat_juris
                if (
                    disp.enseignant_id == candidat.id
                    and disp.enseignant_id not in profs_occupes.values_list('enseignant_id', flat=True)
                )
            ]

            if cle in creneaux:
                creneaux[cle].extend(liste_profs)
            else:
                creneaux[cle] = liste_profs

        # 4- Si au moins 3 profs de la specialite
        for cle, liste_juris_probable in creneaux.items():

            if len(liste_juris_probable) >= 3:

                membre_jury = liste_juris_probable[:3]
                creneau_choisi = cle
                break

        # Sinon completer avec d'autres profs
        if not creneau_choisi:

            for cle, liste_juris_probable in creneaux.items():

                if 1 <= len(liste_juris_probable) < 3:

                    membre_jury = liste_juris_probable
                    creneau_choisi = cle
                    break

            # Aucun creneau valide
            if not creneau_choisi:
                continue

            jour, heure_debut, heure_fin = creneau_choisi

            dispo_creneau = Disponibilite.objects.filter(
                jour=jour,
                heure_debut=heure_debut,
                heure_fin=heure_fin
            )

            soutenances_au_meme_creneau = Soutenance.objects.filter(
                jour=jour,
                heure_debut=heure_debut,
                heure_fin=heure_fin
            )

            profs_occupes = Jury.objects.filter(
                soutenance__in=soutenances_au_meme_creneau
            )

            complement = [
                disp.enseignant
                for disp in dispo_creneau
                if disp.enseignant_id not in profs_occupes.values_list('enseignant_id', flat=True)
            ]

            complement = [
                c for c in complement
                if c not in membre_jury
            ]

            nombre_manquant = 3 - len(membre_jury)

            membre_jury.extend(
                complement[:nombre_manquant]
            )

        # 5- Chercher une salle disponible
        jour, heure_debut, heure_fin = creneau_choisi

        salle_choisie = None

        for salle in salles:

            occupation = Soutenance.objects.filter(
                jour=jour,
                heure_debut=heure_debut,
                heure_fin=heure_fin,
                salle_id=salle.id
            )

            if not occupation.exists():

                salle_choisie = salle
                break

        # Pas de salle disponible
        if not salle_choisie:
            continue

        # 6- Programmer la soutenance
        if len(membre_jury) == 3 and salle_choisie:

            nouvelle_soutenance = Soutenance.objects.create(
                jour=jour,
                heure_debut=heure_debut,
                heure_fin=heure_fin,
                salle_id=salle_choisie.id,
                memoire_id=memoire.id,
                statut='planifiee'
            )

            # 7- Enregistrer le jury
            for prof in membre_jury:

                Jury.objects.create(
                    soutenance_id=nouvelle_soutenance.id,
                    enseignant_id=prof.id
                )


def replanifier(session_id):

    # Recuperer les soutenances rejetees
    soutenances_rejetees = Soutenance.objects.filter(
        statut='rejetee',
        memoire__session_id=session_id
    )

    # Recuperer les memoires associes
    memoires_a_replanifier = [
        soutenance.memoire
        for soutenance in soutenances_rejetees
    ]

    # Supprimer les jurys
    Jury.objects.filter(
        soutenance__in=soutenances_rejetees
    ).delete()

    # Supprimer les soutenances
    soutenances_rejetees.delete()

    # Relancer l'algo
    generer_planning(
        session_id,
        memoires_cibles=memoires_a_replanifier
    )