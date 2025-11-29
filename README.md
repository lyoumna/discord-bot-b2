Bot Discord – Projet B2 

Ce projet consiste à faire un bot Discord développé en Python. Il combine plusieurs fonctionnalités : historique des commandes, arbre de conversation, rappels, mini-jeu, filtre de langage, et persistance des données. 

Fonctionnalités 

Arbre de conversation 

Commande !helpme : lance une discussion guidée. 

Réponses sans préfixe : l’utilisateur avance dans l’arbre. 

Commande !reset : recommence la conversation. 

Commande !speak_about <sujet> : vérifie si un sujet existe dans l’arbre. 

Historique 

!h_last : affiche la dernière commande de l’utilisateur. 

!h_all : affiche toutes ses commandes. 

!h_clear : vide son historique personnel. 

Rappels 

!remind <durée> <message> : envoie un rappel après un délai (ex. !remind 10s boire de l’eau). 

Mini-jeu 

!guess start : le bot choisit un nombre entre 1 et 10. 

!guess try <nombre> : l’utilisateur devine. 

!guess stop : arrête la partie. 

Filtre de langage 

Détecte les mots interdits (con, idiot, merde). 

Envoie un avertissement à l’utilisateur. 

!warnings : affiche le nombre d’avertissements. 

Persistance 

Sauvegarde automatique toutes les 60 secondes. 

Sauvegarde à l’arrêt du bot. 

Données stockées dans data.json. 

Installation 

Prérequis 

Python 3.11+ 

Un bot Discord avec le Message Content Intent activé 

Dépendances 

bash 

pip install discord.py python-dotenv 
 

Fichier .env 

Crée un fichier .env à la racine avec : 

Code 

DISCORD_TOKEN=ton_token_ici 
PREFIX=! 
 

Lancement 

bash 

python bot.py 
 

Structure du projet 

Code 

discord-bot-b2/ 
│ 
├── bot.py                 # Fichier principal 
├── .env                   # Token et préfixe 
├── data.json              # Sauvegarde des données 
│ 
└── structures/ 
   ├── linked_list.py     # Historique des commandes 
   ├── tree.py            # Arbre de conversation 
   └── persistence.py     # Sauvegarde / chargement JSON 
 

Auteur 

Youmna Larabi 

Projet réalisé pour le rattrapage en Python 
