from django.core.management.base import BaseCommand
from planification.models import (
    Enseignant, Etudiant, Memoire, Disponibilite, 
    Salle, Session, Soutenance, Jury
)
import datetime, random

class Command(BaseCommand):
    help = 'Remplit la BDD avec des données de démonstration'

    def handle(self, *args, **kwargs):

        # Nettoyage
        Jury.objects.all().delete()
        Soutenance.objects.all().delete()
        Disponibilite.objects.all().delete()
        Memoire.objects.all().delete()
        Etudiant.objects.all().delete()
        Enseignant.objects.all().delete()
        Salle.objects.all().delete()
        Session.objects.all().delete()

        # Session
        session = Session.objects.create(
            libelle='Session Juin 2026',
            date_debut=datetime.date(2026, 6, 20),
            date_fin=datetime.date(2026, 6, 30),
            statut='ouverte'
        )

        # Salles
        Salle.objects.create(nom='Salle A', capacite=30, batiment='Bloc Info')
        Salle.objects.create(nom='Salle B', capacite=25, batiment='Bloc Info')
        Salle.objects.create(nom='Salle C', capacite=20, batiment='Bloc Sciences')
        Salle.objects.create(nom='Amphi 200', capacite=200, batiment='Bat Principal')

        # Enseignants
        enseignants = []
        for nom, prenom, email, grade, specialite in [
            ('Ouedraogo', 'Moussa',  'moussa.ouedraogo@univ.bf',  'Professeur',       'Informatique'),
            ('Kabore',    'Issouf',  'issouf.kabore@univ.bf',     'Maitre de conf.',  'Informatique'),
            ('Sawadogo',  'Dramane', 'dramane.sawadogo@univ.bf',  'Maitre Assistant', 'Informatique'),
            ('Zongo',     'Seydou',  'seydou.zongo@univ.bf',      'Maitre Assistant', 'Informatique'),
            ('Traore',    'Aminata', 'aminata.traore@univ.bf',    'Professeur',       'Reseaux'),
            ('Compaore',  'Ibrahim', 'ibrahim.compaore@univ.bf',  'Maitre de conf.',  'Reseaux'),
            ('Kindo',     'Fatima',  'fatima.kindo@univ.bf',      'Maitre Assistant', 'Reseaux'),
            ('Tall',      'Oumar',   'oumar.tall@univ.bf',        'Professeur',       'Genie Logiciel'),
            ('Diallo',    'Mariam',  'mariam.diallo@univ.bf',     'Maitre de conf.',  'Genie Logiciel'),
            ('Barro',     'Adama',   'adama.barro@univ.bf',       'Maitre Assistant', 'Genie Logiciel'),
            ('Some',      'Pascal',  'pascal.some@univ.bf',       'Professeur',       'Algorithmique'),
            ('Toe',       'Rasmane', 'rasmane.toe@univ.bf',       'Maitre de conf.',  'Algorithmique'),
        ]:
            e = Enseignant.objects.create(
                nom=nom, prenom=prenom, email=email,
                grade=grade, specialite=specialite
            )
            enseignants.append(e)

        # Disponibilités
        creneaux = [
            (datetime.date(2026, 6, 20), datetime.time(8, 0),  datetime.time(10, 0)),
            (datetime.date(2026, 6, 20), datetime.time(14, 0), datetime.time(16, 0)),
            (datetime.date(2026, 6, 21), datetime.time(8, 0),  datetime.time(10, 0)),
            (datetime.date(2026, 6, 21), datetime.time(14, 0), datetime.time(16, 0)),
        ]
        random.seed(42)
        for enseignant in enseignants:
            for jour, heure_debut, heure_fin in random.sample(creneaux, k=random.randint(2, 4)):
                Disponibilite.objects.create(
                    enseignant_id=enseignant.id,
                    session_id=session.id,
                    jour=jour, heure_debut=heure_debut, heure_fin=heure_fin
                )

        # Étudiants + Mémoires
        for matricule, nom, prenom, filiere, niveau, titre, specialite in [
            ('INF001', 'Sawadogo', 'Jean',    'Informatique',  'Master 2', 'Systemes de recommandation',          'Informatique'),
            ('INF002', 'Zongo',    'Fatima',  'Informatique',  'Master 2', 'Securite des applications web',       'Informatique'),
            ('INF003', 'Kabore',   'Adama',   'Informatique',  'Master 2', 'Cloud computing et virtualisation',   'Informatique'),
            ('INF004', 'Traore',   'Mariam',  'Informatique',  'Master 2', 'Intelligence artificielle appliquee', 'Informatique'),
            ('RES001', 'Compaore', 'Ibrahim', 'Reseaux',       'Master 2', 'Protocoles de routage avances',       'Reseaux'),
            ('RES002', 'Diallo',   'Oumar',   'Reseaux',       'Master 2', 'Reseaux sans fil et IoT',             'Reseaux'),
            ('RES003', 'Barro',    'Aminata', 'Reseaux',       'Master 2', 'Securite des reseaux',                'Reseaux'),
            ('GL001',  'Some',     'Pascal',  'Genie Logiciel','Master 2', 'Methodes agiles en entreprise',       'Genie Logiciel'),
            ('GL002',  'Toe',      'Rasmane', 'Genie Logiciel','Master 2', 'Architecture microservices',          'Genie Logiciel'),
            ('GL003',  'Kindo',    'Seydou',  'Genie Logiciel','Master 2', 'Tests et qualite logicielle',         'Genie Logiciel'),
            ('AL001',  'Ouedraogo','Dramane', 'Algorithmique', 'Master 2', 'Algorithmes de tri avances',          'Algorithmique'),
            ('AL002',  'Tall',     'Moussa',  'Algorithmique', 'Master 2', 'Complexite et optimisation',          'Algorithmique'),
        ]:
            etudiant = Etudiant.objects.create(
                matricule=matricule, nom=nom, prenom=prenom,
                filiere=filiere, niveau=niveau
            )
            Memoire.objects.create(
                etudiant_id=etudiant.id, session_id=session.id,
                titre=titre, type='Memoire',
                specialite=specialite, statut='soumis'
            )

        self.stdout.write(self.style.SUCCESS(
            f'✅ BDD remplie ! {Enseignant.objects.count()} profs, '
            f'{Memoire.objects.count()} mémoires, '
            f'{Disponibilite.objects.count()} dispos.'
        ))