from django.urls import path
from . import views
from .views import *



urlpatterns = [
        path('', views.index, name='index'),
    path('nouveau_client/', views.nouveau_client, name='nouveau_client'),
    path('ajout_compte/', views.ajout_compte, name='ajout_compte'),
    path('client/supprimer/<int:client_id>/', views.supprimer_client, name='supprimer_client'),
    path('execute-sql/', views.execute_sql, name='execute_sql'),
    path('depot/', views.depot, name='depot'),
    path('retrait/', views.retrait, name='retrait'),
    path('comptes/', compte_list, name='compte_list'),
    path('versement/', views.versement, name='versement'),
    path('rechercher_comptes/', rechercher_comptes, name='rechercher_comptes')
]

"""
Utilité:
--------
Liste des URLs de l'application 'bankapp'.

Cette liste définit les chemins d'accès aux différentes vues de l'application 'bankapp'.

URLs:
-----
'' : views.index
    Chemin d'accès à la page d'accueil de l'application.

'nouveau_client/' : views.nouveau_client
    Chemin d'accès pour créer un nouveau client.

'ajout_compte/' : views.ajout_compte
    Chemin d'accès pour ajouter un compte.

'client/supprimer/<int:client_id>/' : views.supprimer_client
    Chemin d'accès pour supprimer un client en utilisant son ID.

'execute-sql/' : views.execute_sql
    Chemin d'accès pour exécuter une requête SQL.

'depot/' : views.depot
    Chemin d'accès pour effectuer un dépôt.

'retrait/' : views.retrait
    Chemin d'accès pour effectuer un retrait.

'comptes/' : compte_list
    Chemin d'accès à la liste des comptes.

'versement/' : views.versement
    Chemin d'accès pour effectuer un versement.

'rechercher_comptes/' : rechercher_comptes
    Chemin d'accès pour rechercher des comptes.
"""