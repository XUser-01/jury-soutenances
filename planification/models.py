from django.db import models

from django.contrib.auth.models import User

class Enseignant(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    grade = models.CharField(max_length=50)
    specialite = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.prenom} {self.nom}"
class Session(models.Model):

    STATUT_CHOICES = [
        ('ouverte', 'Ouverte'),
        ('fermee', 'Fermée'),
    ]

    libelle = models.CharField(max_length=100)
    date_debut = models.DateField()
    date_fin = models.DateField()

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='ouverte'
    )

    def __str__(self):
        return self.libelle




class Etudiant(models.Model):

    matricule = models.CharField(max_length=20, unique=True)

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)

    filiere = models.CharField(max_length=80)

    niveau = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.prenom} {self.nom}"


class Salle(models.Model):

    nom = models.CharField(max_length=50)

    capacite = models.IntegerField()

    batiment = models.CharField(max_length=80)

    def __str__(self):
        return self.nom


class Memoire(models.Model):

    STATUT_CHOICES = [
        ('soumis', 'Soumis'),
        ('valide', 'Validé'),
        ('rejete', 'Rejeté'),
    ]

    etudiant = models.ForeignKey(
        Etudiant,
        on_delete=models.CASCADE
    )

    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE
    )

    titre = models.CharField(max_length=255)

    type = models.CharField(max_length=50)

    specialite = models.CharField(max_length=100)

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='soumis'
    )

    def __str__(self):
        return self.titre


class Disponibilite(models.Model):

    enseignant = models.ForeignKey(
        Enseignant,
        on_delete=models.CASCADE
    )

    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE
    )

    jour = models.DateField()

    heure_debut = models.TimeField()

    heure_fin = models.TimeField()

    def __str__(self):
        return f"{self.enseignant} - {self.jour} {self.heure_debut}"


class Soutenance(models.Model):

    STATUT_CHOICES = [
        ('planifiee', 'Planifiée'),
        ('validee', 'Validée'),
        ('rejetee', 'Rejetée'),
        ('terminee', 'Terminée'),
    ]

    DECISION_CHOICES = [
        ('admis', 'Admis'),
        ('corrections', 'Admis avec corrections'),
        ('ajourne', 'Ajourné'),
    ]

    memoire = models.ForeignKey(
        Memoire,
        on_delete=models.CASCADE
    )

    salle = models.ForeignKey(
        Salle,
        on_delete=models.CASCADE
    )

    jour = models.DateField()

    heure_debut = models.TimeField()

    heure_fin = models.TimeField()

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='planifiee'
    )

    note = models.FloatField(
        null=True,
        blank=True
    )

    decision = models.CharField(
        max_length=50,
        choices=DECISION_CHOICES,
        null=True,
        blank=True
    )

    observations = models.TextField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Soutenance de {self.memoire}"


class Jury(models.Model):

    soutenance = models.ForeignKey(
        Soutenance,
        on_delete=models.CASCADE
    )

    enseignant = models.ForeignKey(
        Enseignant,
        on_delete=models.CASCADE
    )

    present = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.enseignant} - {self.soutenance}"