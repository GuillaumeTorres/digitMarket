# digiMarket

digiMarket est une API REST de boutique en ligne réalisée avec Flask. Elle permet de gérer des utilisateurs, un catalogue de produits et des commandes.

## Fonctionnalités

- Inscription et connexion avec un token JWT.
- Consultation et recherche de produits par nom ou catégorie.
- Création, modification et suppression de produits réservées aux administrateurs.
- Création et consultation des commandes.
- Mise à jour du statut d'une commande et du stock lorsque la commande est validée ou annulée.
- Documentation interactive de l'API avec Swagger.

## Prérequis

- Python installé.
- `pip`, pour installer les dépendances Python.

Les commandes ci-dessous sont à exécuter depuis la racine du projet.

## Installation

Créer puis activer un environnement virtuel :

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Installer les dépendances :

```bash
python -m pip install -r requirements.txt
```

Créer un fichier `.env` à la racine du projet et y définir une clé secrète pour les tokens JWT :

```env
JWT_SECRET_KEY=remplacer-par-une-cle-secrete-personnelle
```
Le fichier `.env` est ignoré par Git.

## Base de données et données de démonstration

La base SQLite est enregistrée dans `instance/digimarket.db`. Après l’installation des dépendances et la création du fichier `.env`, lancer le script :

```bash
python generate_data.py
```

Le script crée les tables si nécessaire et ajoute un compte admin, deux comptes clients, trois produits et trois commandes. Jean a deux commandes, Marie en a une et l’admin peut consulter les trois. La base locale n’est pas envoyée sur GitHub ; le script permet de la recréer avec ces données.

Comptes de démonstration :

| Rôle | Email | Mot de passe |
|---|---|---|
| Admin | `admin@digimarket.test` | `admin_password` |
| Client Jean | `jean@digimarket.test` | `client_password` |
| Client Marie | `marie@digimarket.test` | `client2_password` |

Ces identifiants sont uniquement destinés à la démonstration. Si la base contient déjà des utilisateurs ou des produits, le script n’ajoute rien.

## Lancer l’application

Avec l’environnement virtuel activé :

```bash
flask run --debug
```

L’API est alors accessible à l’adresse `http://127.0.0.1:5000`.

## Documentation de l’API

Quand le serveur est lancé, ouvrir la documentation interactive à l’adresse :

```text
http://127.0.0.1:5000/apidocs/
```

Pour les routes protégées, envoyer le token retourné par la connexion dans l’en-tête HTTP :

```text
Authorization: Bearer <token>
```

## Routes principales

| Méthode | URL | Accès | Description |
|---|---|---|---|
| `POST` | `/api/auth/register` | Public | Créer un compte client |
| `POST` | `/api/auth/login` | Public | Se connecter et obtenir un token |
| `GET` | `/api/produits` | Public | Lister les produits, avec filtres facultatifs `nom` et `categorie` |
| `GET` | `/api/produits/{id}` | Public | Consulter un produit |
| `POST` | `/api/produits` | Admin | Créer un produit |
| `PATCH` | `/api/produits/{id}` | Admin | Modifier un produit |
| `DELETE` | `/api/produits/{id}` | Admin | Supprimer un produit |
| `POST` | `/api/commandes` | Utilisateur connecté | Créer une commande avec ses produits et quantités |
| `GET` | `/api/commandes` | Utilisateur connecté | Lister ses commandes ; un admin voit toutes les commandes |
| `GET` | `/api/commandes/{id}` | Admin | Consulter une commande |
| `GET` | `/api/commandes/{id}/lignes` | Admin | Consulter les produits d’une commande |
| `PATCH` | `/api/commandes/{id}` | Admin | Modifier le statut d’une commande |

Les paramètres attendus et les réponses sont détaillés dans Swagger.

### Exemple : créer une commande

Après connexion, envoyer le token dans l’en-tête `Authorization` et un corps JSON de cette forme :

```json
{
  "adresse_livraison": "12 rue des Exemples, Paris",
  "produits": [
    {"produit_id": 1, "quantite": 2},
    {"produit_id": 2, "quantite": 1}
  ]
}
```

La commande est créée avec le statut `en_attente`. Le stock est vérifié et mis à jour lorsque l’administrateur valide la commande.

## Tests

Tester les différentes routes de l'API :

```bash
python -m pytest
```

Les tests utilisent une base SQLite temporaire séparée de la base de l’application.

## Structure du projet après installation

```text
digiMarket/
├── .gitignore               # Fichiers ignorés par Git
├── .env                     # Configuration locale
├── .venv/                   # Environnement virtuel
├── README.md                # Présentation et instructions du projet
├── app.py                   # Création et configuration de l’application Flask
├── generate_data.py         # Création des données de démonstration
├── requirements.txt         # Dépendances Python nécessaires
├── utils.py                 # Fonctions partagées
├── instance/
│   └── digimarket.db        # Base SQLite créée par le script
├── models/                  # Modèles SQLAlchemy
├── routes/                  # Routes organisées en Blueprints
└── tests/                   # Tests unitaires et fonctionnels
```
