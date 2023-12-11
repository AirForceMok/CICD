# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class Client(models.Model):
    """
        Modèle de données pour représenter un client.

        Attributes:
        -----------
        nom : str
            Nom du client (maximum 75 caractères).

        prenom : str
            Prénom du client (maximum 75 caractères).

        sexe : str
            Genre du client, choix entre 'Homme' ou 'Femme' (maximum 10 caractères).

        email : str
            Adresse email du client (maximum 100 caractères).

        nom_utilisateur : str
            Nom d'utilisateur du client (maximum 50 caractères).

        mdp : str
            Mot de passe du client (maximum 50 caractères).

        Meta:
        -----
        db_table : str
            Nom de la table de base de données associée à ce modèle (table 'client').
    """
    #id = models.IntegerField(primary_key=True)
    nom = models.CharField(max_length=75, null=True)
    prenom = models.CharField(max_length=75, null=True)
    SEXE_CHOICES = [
        ('Homme', 'Homme'),
        ('Femme', 'Femme'),
    ]
    sexe = models.CharField(max_length=10, choices=SEXE_CHOICES, null=True)
    email = models.CharField(max_length=100, null=True)
    nom_utilisateur = models.CharField(max_length=50, null=True)
    mdp = models.CharField(max_length=50, null=True)

    class Meta:
        db_table = 'client'


"""class Client(AbstractUser):
    nom_utilisateur = models.CharField(max_length=150, unique=True)
    mdp = models.CharField(max_length=128)

    USERNAME_FIELD = 'nom_utilisateur'
    REQUIRED_FIELDS = ['email']  # Ajoutez ici les champs requis pour la création d'un utilisateur

    def __str__(self):
        return self.nom_utilisateur"""


class Compte(models.Model):
    """
        Modèle de données pour représenter un compte.

        Attributes:
        -----------
        IBAN : str
            Numéro IBAN du compte (maximum 50 caractères), unique dans la base de données.

        client : Client
            Référence au client associé à ce compte (clé étrangère vers le modèle Client).

        solde : Decimal
            Solde du compte (maximum 10 chiffres avant la virgule et 2 chiffres après la virgule).
            La valeur par défaut est 0.00.

        date : datetime
            Date de création du compte (remplie automatiquement lors de la création).

        Meta:
        -----
        db_table : str
            Nom de la table de base de données associée à ce modèle (table 'compte').

        Methods:
        --------
        __str__():
            Renvoie l'IBAN du compte sous forme de chaîne.
    """
    #id = models.IntegerField(primary_key=True)
    IBAN = models.CharField(max_length=50, unique=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True)
    solde = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0.00)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'compte'

    def __str__(self):
        return self.iban


class Personnel(models.Model):
    """
        Modèle de données pour représenter le personnel.

        Attributes:
        -----------
        nom : str
            Nom du personnel (maximum 75 caractères).

        prenom : str
            Prénom du personnel (maximum 75 caractères).

        email : str
            Adresse email du personnel (maximum 100 caractères).

        date_arrive : datetime
            Date d'arrivée du personnel (peut être vide).

        nom_utilisateur : str
            Nom d'utilisateur du personnel (maximum 50 caractères).

        mdp : str
            Mot de passe du personnel (maximum 50 caractères).

        Meta:
        -----
        db_table : str
            Nom de la table de base de données associée à ce modèle (table 'personnel').
    """
    #id = models.IntegerField(primary_key=True)
    nom = models.CharField(max_length=75, blank=True, null=True)
    prenom = models.CharField(max_length=75, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    date_arrive = models.DateTimeField(blank=True, null=True)
    nom_utilisateur = models.CharField(max_length=50, blank=True, null=True)
    mdp = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'personnel'


class Transaction(models.Model):
    """
        Modèle de données pour représenter une transaction entre deux comptes.

        Attributes:
        -----------
        compte_source : Compte
            Compte source de la transaction (clé étrangère vers le modèle Compte).

        compte_cible : Compte
            Compte cible de la transaction (clé étrangère vers le modèle Compte).

        montant : Decimal
            Montant de la transaction (maximum 10 chiffres avant la virgule et 2 chiffres après la virgule).

        type : str
            Type de transaction (maximum 25 caractères).

        Meta:
        -----
        db_table : str
            Nom de la table de base de données associée à ce modèle (table 'transaction').
    """
    #id = models.IntegerField(primary_key=True)
    compte_source = models.ForeignKey(Compte, on_delete=models.DO_NOTHING, db_column='compte_source', blank=True, null=True, related_name='transactions_source')
    compte_cible = models.ForeignKey(Compte, on_delete=models.DO_NOTHING, db_column='compte_cible', blank=True, null=True, related_name='transactions_cible')
    montant = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    type = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        db_table = 'transaction'
