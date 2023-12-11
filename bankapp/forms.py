from django import forms
from .models import Client, Compte

class ClientForm(forms.ModelForm):
    """
        Formulaire Client:
        ------------------

        Formulaire de création/modification d'un client.

        Ce formulaire est basé sur le modèle Django 'Client' et inclut les champs suivants :
        - nom
        - prénom
        - sexe
        - email
        - nom_utilisateur
        - mdp

        Attributes:
        -----------
        forms.ModelForm: Classe parente pour créer un formulaire basé sur un modèle Django.

        Meta:
        ------
        model: Client
            Le modèle de base pour ce formulaire.
        fields: List[str]
            Liste des champs inclus dans le formulaire.
    """
    class Meta:
        model = Client
        fields = ['nom', 'prenom', 'sexe', 'email', 'nom_utilisateur', 'mdp']


class CompteForm(forms.ModelForm):
    """
        Formulaire Compte:
        ------------------

        Formulaire de création/modification d'un compte.

        Ce formulaire est basé sur le modèle Django 'Compte' et inclut le champ 'client'.

        Attributes:
        -----------
        forms.ModelForm: Classe parente pour créer un formulaire basé sur un modèle Django.

        Methods:
        --------
        __init__(self, *args, **kwargs):
            Initialise le formulaire avec des données optionnelles.

            Parameters:
            -----------
            *args: List
                Arguments positionnels pour initialiser le formulaire.
            **kwargs: Dict
                Arguments clés-valeurs pour initialiser le formulaire.

            Note:
            -----
            Modifie l'étiquette vide du champ 'client' pour afficher 'Sélectionner un client'.
    """
    class Meta:
        model = Compte
        fields = ['client']

    def __init__(self, *args, **kwargs):
        """
            Initialise le formulaire avec des données optionnelles.

            Parameters:
            -----------
            *args: List
                Arguments positionnels pour initialiser le formulaire.
            **kwargs: Dict
                Arguments clés-valeurs pour initialiser le formulaire.

            Note:
            -----
            Modifie l'étiquette vide du champ 'client' pour afficher 'Sélectionner un client'.
        """
        super().__init__(*args, **kwargs)
        self.fields['client'].empty_label = 'Sélectionner un client'
