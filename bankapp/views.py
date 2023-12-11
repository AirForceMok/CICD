from django.shortcuts import render, redirect
from django.http import HttpResponse
import mysql.connector
from .forms import ClientForm, CompteForm
import random, string
from django.db import connection
from . import models
from .models import Client, Compte
from django.template import loader
import asyncio
from nats.aio.client import Client
import nats
from nats.aio.errors import ErrConnectionClosed, ErrTimeout
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
import csv



def index(request):
    """
        Vue pour afficher la page d'accueil de l'application.

        Parameters:
        -----------
        request : HttpRequest
            Objet HttpRequest représentant la requête HTTP reçue.

        Returns:
        --------
        HttpResponse
            Réponse HTTP rendue pour afficher la page d'accueil.

        Notes:
        ------
        Récupère la liste de tous les clients et comptes depuis la base de données.
        Puis, renvoie la page d'accueil 'bankapp/index.html' avec les données des clients et des comptes.
    """
    clientelle = list(models.Client.objects.all())
    comptes = list(models.Compte.objects.all())
    context = {"clientelle": clientelle, "comptes": comptes}
    return render(request,"bankapp/index.html", context)

def nouveau_client(request):
    """
        Vue pour ajouter un nouveau client à la base de données.

        Parameters:
        -----------
        request : HttpRequest
            Objet HttpRequest représentant la requête HTTP reçue.

        Returns:
        --------
        HttpResponse
            Réponse HTTP pour afficher le formulaire d'ajout d'un nouveau client
            ou un message de confirmation après l'ajout.

        Notes:
        ------
        - Si la requête est de type 'POST', vérifie et traite les données du formulaire de création de client.
        - Si le formulaire est valide, enregistre le nouveau client dans la base de données et renvoie un message de succès.
        - Si la requête est de type 'GET', affiche le formulaire vide pour ajouter un nouveau client.
    """
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse("Le client a été ajouté avec succès.")
    else:
        form = ClientForm()

    context = {'form': form}
    return render(request, 'bankapp/index.html', context)


def ajout_compte(request):
    """
        Vue pour ajouter un nouveau compte à la base de données.

        Parameters:
        -----------
        request : HttpRequest
            Objet HttpRequest représentant la requête HTTP reçue.

        Returns:
        --------
        HttpResponse / HttpResponseRedirect
            Réponse HTTP pour afficher le formulaire d'ajout de compte
            ou rediriger vers la page d'accueil après l'ajout.

        Notes:
        ------
        - Si la requête est de type 'POST', vérifie et traite les données du formulaire de création de compte.
        - Si le formulaire est valide, crée un nouveau compte avec un IBAN généré et l'enregistre dans la base de données.
        - Si la requête est de type 'GET', affiche le formulaire vide pour ajouter un nouveau compte.
    """
    if request.method == 'POST':
        form = CompteForm(request.POST)
        if form.is_valid():
            compte = form.save(commit=False)
            compte.IBAN = generate_iban()
            compte.save()
            return redirect('index')
    else:
        form = CompteForm()

    context = {'form': form}
    return render(request, 'bankapp/index.html', context)

def generate_iban():
    """
        Génère un numéro IBAN aléatoire pour un compte bancaire.

        Returns:
        --------
        str
            Numéro IBAN généré au format FR68 XXXX XXXX XXXX XXXX XXXX XXXX.

        Notes:
        ------
        Génère un numéro IBAN au format FR68 suivi de 5 groupes de chiffres aléatoires.
    """
    IBAN = "FR68"
    random_part = ''.join(random.choices(string.digits, k=5))
    IBAN += f" {random_part}"
    random_part = ''.join(random.choices(string.digits, k=5))
    IBAN += f" {random_part}"
    random_part = ''.join(random.choices(string.digits, k=10))
    IBAN += f" {random_part}"
    return IBAN


#_________________________________________________________________________________________________________________________#



def supprimer_client(request, client_id):
    """
        Vue pour supprimer un client de la base de données.

        Parameters:
        -----------
        request : HttpRequest
            Objet HttpRequest représentant la requête HTTP reçue.

        client_id : int
            Identifiant du client à supprimer.

        Returns:
        --------
        HttpResponseRedirect
            Redirection vers la page d'accueil après la suppression du client.

        Notes:
        ------
        - Recherche le client à l'aide de son identifiant dans la base de données.
        - Supprime le client trouvé.
        - Redirige ensuite vers la page d'accueil de l'application.
    """
    client = Client.objects.get(id=client_id)
    client.delete()
    return redirect('index')

def execute_sql(request):
    """
        Vue pour exécuter une commande SQL personnalisée pour supprimer un client.

        Parameters:
        -----------
        request : HttpRequest
            Objet HttpRequest représentant la requête HTTP reçue.

        Returns:
        --------
        HttpResponseRedirect / HttpResponse
            Redirection vers la page d'accueil après l'exécution de la commande SQL,
            ou affichage du formulaire HTML pour saisir la commande SQL.

        Notes:
        ------
        - Si la requête est de type 'POST', récupère l'identifiant du client à supprimer et exécute la commande SQL DELETE correspondante.
        - Redirige ensuite vers la page d'accueil de l'application.
        - Si la requête est de type 'GET', affiche le formulaire HTML pour saisir la commande SQL.
    """
    if request.method == 'POST':
        id = request.POST.get('id')

        # Votre commande SQL à exécuter
        sql = f"DELETE FROM client WHERE id={id};"

        with connection.cursor() as cursor:
            cursor.execute(sql)

        # Rediriger vers la page principale (index)
        return redirect('index')

        # Gérer le cas où le formulaire n'a pas été soumis
    return render(request, 'template.html')


#_________________________________________________________________________________________________________________________#

"""async def publish_deposit_message():
    nc = NATS()
    await nc.connect(servers=["10.128.200.7:4222"])

    message = "test"

    await nc.publish("deposit", message.encode())

    await nc.close()

async def publish_verification_message(montant):
    if montant > 10000:
        await publish_deposit_message()"""




def depot(request):
    """
        Vue pour effectuer un dépôt sur un compte bancaire en utilisant une connexion directe à une base de données MySQL.

        Parameters:
        -----------
        request : HttpRequest
            Objet HttpRequest représentant la requête HTTP reçue.

        Returns:
        --------
        HttpResponse
            Réponse HTTP pour indiquer le succès de la mise à jour du solde du compte.

        Notes:
        ------
        - Si la requête est de type 'POST', récupère l'IBAN et le montant à déposer depuis les données POST.
        - Établit une connexion à la base de données MySQL avec les informations de connexion fournies.
        - Utilise des fonctions internes pour retrouver le solde du compte associé à l'IBAN, mettre à jour le solde du compte avec le montant déposé, et envoie un message de vérification asynchrone si le montant est supérieur à 10000 euros.
    """

    if request.method == 'POST':
        iban = request.POST.get('iban')  # Récupérer l'IBAN à partir des données POST
        montant = float(request.POST.get('montant'))  # Récupérer le montant à partir des données POST

        cnx = mysql.connector.connect(
            host="localhost",
            user="root",
            password="toto",
            database="bankapp",
            port="3307",
        )

        # Création d'un curseur pour exécuter des requêtes SQL
        cursor = cnx.cursor()

        # Fonction pour trouver le solde d'un compte en fonction de son IBAN
        def trouver_solde_par_iban(iban):

            query = "SELECT solde FROM compte WHERE IBAN = %s"
            cursor.execute(query, (iban,))
            result = cursor.fetchone()
            if result:
                solde = result[0]
                return solde
            else:
                print(f"Aucun compte trouvé avec l'IBAN {iban}.")
                return None

        # Fonction pour mettre à jour le solde d'un compte
        def mettre_a_jour_solde(iban, montant):
            """
                Met à jour le solde d'un compte bancaire en fonction de l'IBAN et du montant à déposer.

                Parameters:
                -----------
                iban : str
                    Numéro IBAN du compte bancaire.

                montant : float
                    Montant à déposer sur le compte.

                Notes:
                ------
                Cette fonction récupère le solde actuel du compte à partir de l'IBAN spécifié,
                ajoute le montant fourni au solde actuel, puis met à jour le solde dans la base de données.
                Elle exécute une requête SQL UPDATE pour modifier le solde du compte correspondant à l'IBAN.
            """
            solde = trouver_solde_par_iban(iban)
            if solde is not None:
                solde = float(solde)
                nouveau_solde = solde + montant
                query = "UPDATE compte SET solde = %s WHERE IBAN = %s"
                cursor.execute(query, (nouveau_solde, iban))
                cnx.commit()
                print(f"Le solde du compte {iban} a été mis à jour : {nouveau_solde} euros.")

                """if montant > 10000:
                    asyncio.run(publish_verification_message(montant))"""

        # Exemple d'utilisation : ajout du montant donné au solde d'un compte avec un IBAN spécifique
        mettre_a_jour_solde(iban, montant)

        """asyncio.run(publish_verification_message(montant))"""

        # Fermeture du curseur et de la connexion à la base de données
        cursor.close()
        cnx.close()

        return HttpResponse("Le solde a été mis à jour avec succès.")
    else:
        return HttpResponse("Erreur : méthode non autorisée.")

#_________________________________________________________________________________________________________________________#

"""async def publish_verification_message(montant):
    nc = await nats.connect("ws://10.128.200.7:4222")

    async def error_cb(e):
        print("Error:", e)

    async def closed_cb():
        print("Connection closed.")

    try:
        await nc.connect(servers=["ws://10.128.200.7:4222"], error_cb=error_cb, closed_cb=closed_cb)

        montant = "10001"
        #if montant > 10000:
        await nc.publish("deposit", float(montant).encode())

        await nc.flush()
        await nc.close()

    except (ErrConnectionClosed, ErrTimeout) as e:
        print("Error:", e)"""



def retrait(request):
    """
        Vue pour effectuer un retrait sur un compte bancaire en utilisant une connexion directe à une base de données MySQL.

        Parameters:
        -----------
        request : HttpRequest
            Objet HttpRequest représentant la requête HTTP reçue.

        Returns:
        --------
        HttpResponse
            Réponse HTTP pour indiquer le succès de la mise à jour du solde du compte.

        Notes:
        ------
        - Si la requête est de type 'POST', récupère l'IBAN et le montant à retirer depuis les données POST.
        - Établit une connexion à la base de données MySQL avec les informations de connexion fournies.
        - Utilise des fonctions internes pour retrouver le solde du compte associé à l'IBAN, mettre à jour le solde du compte avec le montant retiré, et envoie un message de vérification asynchrone si le montant est supérieur à 10000 euros.
    """
    if request.method == 'POST':
        iban = request.POST.get('iban')  # Récupérer l'IBAN à partir des données POST
        montant = float(request.POST.get('montant'))  # Récupérer le montant à partir des données POST

        cnx = mysql.connector.connect(
            host="localhost",
            user="root",
            password="toto",
            database="bankapp",
            port="3307",
        )

        # Création d'un curseur pour exécuter des requêtes SQL
        cursor = cnx.cursor()

        # Fonction pour trouver le solde d'un compte en fonction de son IBAN
        def trouver_solde_par_iban(iban):
            query = "SELECT solde FROM compte WHERE IBAN = %s"
            cursor.execute(query, (iban,))
            result = cursor.fetchone()
            if result:
                solde = result[0]
                return solde
            else:
                print(f"Aucun compte trouvé avec l'IBAN {iban}.")
                return None

        # Fonction pour mettre à jour le solde d'un compte
        def mettre_a_jour_solde(iban, montant):
            solde = trouver_solde_par_iban(iban)
            if solde is not None:
                solde = float(solde)
                nouveau_solde = solde - montant
                query = "UPDATE compte SET solde = %s WHERE IBAN = %s"
                cursor.execute(query, (nouveau_solde, iban))
                cnx.commit()
                print(f"Le solde du compte {iban} a été mis à jour : {nouveau_solde} euros.")

                """if montant > 10000:
                    asyncio.run(publish_verification_message(montant))"""

        # Exemple d'utilisation : ajout du montant donné au solde d'un compte avec un IBAN spécifique
        mettre_a_jour_solde(iban, montant)

        # Fermeture du curseur et de la connexion à la base de données
        cursor.close()
        cnx.close()

        return HttpResponse("Le solde a été mis à jour avec succès.")
    else:
        return HttpResponse("Erreur : méthode non autorisée.")

#_________________________________________________________________________________________________________________________#

def get_comptes_by_client_id(client_id):
    """
        Récupère les comptes associés à un client spécifique depuis la base de données.

        Parameters:
        -----------
        client_id : int
            Identifiant du client pour lequel récupérer les comptes.

        Returns:
        --------
        list
            Liste des comptes associés au client spécifié.

        Notes:
        ------
        Établit une connexion à la base de données MySQL avec les informations de connexion fournies.
        Exécute une requête SQL SELECT pour récupérer tous les comptes liés à un client par son identifiant.
        Ferme le curseur et la connexion à la base de données après avoir récupéré les comptes.
    """
    cnx = mysql.connector.connect(
        host="localhost",
        user="root",
        password="toto",
        database="bank",
        port="3307",
    )
    cursor = cnx.cursor()
    query = "SELECT * FROM compte WHERE client_id = %s"
    cursor.execute(query, (client_id,))
    comptes = cursor.fetchall()
    cursor.close()
    cnx.close()
    return comptes

# Vue pour la page avec le formulaire et les résultats des comptes
def compte_list(request):
    """
        Affiche une liste de comptes associés à un client spécifique.

        Parameters:
        -----------
        request : HttpRequest
            Objet HttpRequest représentant la requête HTTP reçue.

        Returns:
        --------
        HttpResponse
            Réponse HTTP avec la liste des comptes associés au client spécifié.

        Notes:
        ------
        Si la méthode de la requête est 'POST', récupère l'identifiant du client à partir des données POST.
        Appelle la fonction 'get_comptes_by_client_id' pour obtenir la liste des comptes associés à ce client.
        Si aucun compte n'est trouvé pour l'identifiant du client, un message spécifique est affiché.
        Renvoie un rendu HTML avec la liste des comptes et le message, à afficher sur la page 'compte_list.html'.
    """
    comptes = []
    message = ""

    if request.method == 'POST':
        client_id = request.POST.get('client_id')
        comptes = get_comptes_by_client_id(client_id)
        if not comptes:
            message = f"Aucun compte trouvé pour l'ID du client {client_id}."

    context = {'comptes': comptes, 'message': message}
    return render(request, 'bankapp/compte_list.html', context)


#_________________________________________________________________________________________________________________________#

from django.shortcuts import render
import mysql.connector

# Connexion à la base de données
cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="toto",
    database="bankapp",
    port="3307"
)

# Création d'un curseur pour exécuter des requêtes SQL
cursor = cnx.cursor()

def get_solde_by_iban(iban):
    """
        Récupère le solde d'un compte bancaire en fonction de son IBAN dans la base de données.

        Parameters:
        -----------
        iban : str
            Numéro d'identification bancaire (IBAN) du compte.

        Returns:
        --------
        float or None
            Solde du compte associé à l'IBAN spécifié. Renvoie None si aucun compte n'est trouvé.

        Notes:
        ------
        Exécute une requête SQL SELECT pour récupérer le solde du compte associé à l'IBAN fourni.
        Si un compte est trouvé pour l'IBAN, renvoie le solde du compte. Sinon, affiche un message d'erreur
        indiquant qu'aucun compte n'a été trouvé avec l'IBAN spécifié.
    """
    query = "SELECT solde FROM compte WHERE IBAN = %s"
    cursor.execute(query, (iban,))
    result = cursor.fetchone()
    if result:
        solde = result[0]
        return solde
    else:
        print(f"Aucun compte trouvé avec l'IBAN {iban}.")
        return None

def mettre_a_jour_solde(iban, montant):
    """
        Met à jour le solde d'un compte bancaire en fonction de son IBAN en ajoutant un montant.

        Parameters:
        -----------
        iban : str
            Numéro d'identification bancaire (IBAN) du compte à mettre à jour.
        montant : float
            Montant à ajouter au solde du compte.

        Notes:
        ------
        Récupère le solde du compte associé à l'IBAN en utilisant la fonction 'get_solde_by_iban'.
        Si un compte est trouvé, le montant spécifié est ajouté au solde du compte.
        Exécute une requête SQL UPDATE pour mettre à jour le solde du compte dans la base de données.
        Affiche un message indiquant que le solde du compte a été mis à jour avec succès.
    """
    solde = get_solde_by_iban(iban)
    if solde is not None:
        solde = float(solde)
        nouveau_solde = solde + montant
        query = "UPDATE compte SET solde = %s WHERE IBAN = %s"
        cursor.execute(query, (nouveau_solde, iban))
        cnx.commit()
        print(f"Le solde du compte {iban} a été mis à jour : {nouveau_solde} euros.")

def versement(request):
    """
        Traite une opération de versement entre deux comptes bancaires.

        Parameters:
        -----------
        request : HttpRequest
            Objet HttpRequest représentant la requête HTTP reçue.

        Returns:
        --------
        HttpResponse
            Rendu HTML de la page 'index.html'.

        Notes:
        ------
        Si la méthode de la requête est 'POST', récupère les IBAN et le montant depuis les données POST.
        Utilise la fonction 'mettre_a_jour_solde' pour débiter le montant de l'IBAN source et créditer
        le montant à l'IBAN cible.
        Renvoie le rendu HTML de la page 'index.html'.
    """
    if request.method == 'POST':
        iban_source = request.POST.get('iban_source')
        iban_cible = request.POST.get('iban_cible')
        montant = float(request.POST.get('montant'))

        mettre_a_jour_solde(iban_source, -montant)
        mettre_a_jour_solde(iban_cible, montant)

        return render(request, 'bankapp/index.html')
    else:
        return render(request, 'bankapp/index.html')


# _________________________________________________________________________________________________________________________#


"""def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('accueil')  # Rediriger vers la page d'accueil après la connexion
        else:
            error_message = "Identifiants invalides. Veuillez réessayer."
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')"""


# _________________________________________________________________________________________________________________________#

def rechercher_comptes(request):
    """
        Recherche et génère un fichier CSV contenant les informations des comptes associés à un client.

        Parameters:
        -----------
        request : HttpRequest
            Objet HttpRequest représentant la requête HTTP reçue.

        Returns:
        --------
        HttpResponse
            Réponse HTTP avec un fichier CSV contenant les informations des comptes du client en téléchargement.

        Notes:
        ------
        Si la méthode de la requête est 'POST', récupère l'ID du client depuis les données POST.
        Utilise la fonction 'filter' pour obtenir tous les comptes associés à ce client.
        Génère un fichier CSV contenant les IBAN et les soldes de chaque compte du client.
        Renvoie une réponse HTTP avec le fichier CSV en téléchargement ou rend la page 'index.html'.
    """
    if request.method == 'POST':
        client_id = request.POST.get('client_id')
        comptes = Compte.objects.filter(client_id=client_id)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="comptes_client_{}.csv"'.format(client_id)

        writer = csv.writer(response, delimiter=' ')  # Utilisation du délimiteur d'espace
        writer.writerow(['IBAN', 'Solde'])

        for compte in comptes:
            writer.writerow([compte.IBAN, compte.solde])

        return response

    return render(request, 'bankapp/index.html')

