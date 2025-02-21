# EpicEvents CRM CLI

**EpicEvents** est une application **CRM (Customer Relationship Management)** en **ligne de commande (CLI)** conçue pour les équipes commerciales, support et gestion.
Elle permet de **gérer les clients, contrats et événements** efficacement.

---

## Fonctionnalités

- **Gestion des clients** (ajout, mise à jour, liste)
- **Gestion des contrats** (création, signature, suivi des paiements)
- **Gestion des événements** (planification, affectation des supports)
- **Authentification sécurisée** avec JWT
- **Gestion des rôles** (commercial, support, gestion)
- **Journalisation** avec **Sentry**
- **Déploiement facile avec Docker**

---

## Installation & Exécution

### 1. **Prérequis**
- **Docker** & **Docker Compose** installés ([instructions](https://docs.docker.com/get-docker/)) (pour version avec Docker)
ou
- **Python 3.10**,**Poetry** & **MySQL** installés ([instructions](https://python-poetry.org/docs/)) (pour version sans Docker)

---

### 2. **Exécution avec Docker**

> **⚠️ Remarque :** Pense à configurer Sentry (optionnel) pour la journalisation.

#### ➤ **Clone le projet**
```sh
git clone https://github.com/LuuNa-JD/EpicEvents_CRM.git
cd epicevents-crm
```

#### ➤ **Configuration des variables d’environnement**
copie le fichier récupéré dans la partie [Configuration](#configuration) et renomme-le en `.env.docker` à la racine du projet.

#### ➤ **Démarrer l'application**
```sh
SENTRY_DSN="https://votre_dsn_sentry" docker-compose up --build
```
Si tu n’utilises pas **Sentry**, lance simplement :
```sh
docker-compose up --build
```

#### ➤ **Se connecter à la CLI**
Une fois lancé, ouvre un **nouveau terminal** et connecte-toi au conteneur CRM :
```sh
docker attach crm_epicevents
```


#### ➤ **Arrêter l'application**
```sh
docker-compose down
```

---

### 3. **Exécution en local (Sans Docker)**
1. **Clone le projet** :
   ```sh
   git clone https://github.com/LuuNa-JD/EpicEvents_CRM.git
   cd epicevents-crm
   ```
2. **Configuration des variables d’environnement** :
- copie le fichier récupéré dans la partie [Configuration](#configuration) et renomme-le en `.env` à la racine du projet.
3. **Installe les dépendances avec Poetry** :
   ```sh
   poetry install
   poetry shell
   ```
4. **Créé la Base de données** :
    ```sql
    CREATE DATABASE crm_epicevents;
    CREATE USER 'crm_admin'@'localhost' IDENTIFIED BY 'Qwerty123*';
    GRANT ALL PRIVILEGES ON crm_epicevents.* TO 'crm_admin'@'localhost';
    FLUSH PRIVILEGES;
    ```
5. **Initialise la base de données** :
   ```sh
   poetry run python init_db.py
   poetry run python seed_data.py
   ```
6. **Lance la CLI** :
   ```sh
   poetry run python main.py
   ```

---

## Utilisation

### ➤ **Authentification**
Pour utiliser l’application, tu dois d'abord **te connecter** (exemple):
```sh
epic_events> auth login
Votre login: admin
Votre mot de passe: admin123
```
si tu veux tester d'autres rôles, utilise les identifiants suivants :
- **Gestionnaire** : `admin` / `admin123`
- **Commercial** : `celine` / `password123`
- **Support** : `robinson` / `support123`

---

### ➤ **Commandes disponibles**
L’application suit une **gestion des rôles** :
- **Gestionnaire** : Gestion complète des collaborateurs, contrats et événements.
- **Commercial** : Gère uniquement ses clients et contrats.
- **Support** : Gère uniquement les événements qui lui sont attribués.

| **Commande**                     | **Description** | **Roles concernés** |
|-----------------------------------|--------------------------------------|---------------------|
| `auth login`                      | Se connecter | Tous |
| `auth logout`                     | Se déconnecter | Tous |
| `auth status`                     | Voir les informations de l'utilisateur connecté | Tous |
| `clients list`                     | Lister les clients | Tous |
| `clients show <id>`                | Afficher les détails d'un client | Tous |
| `clients create`                   | Ajouter un nouveau client | Commercial |
| `clients update`               | Modifier un client | Commercial |
| `contrats list`                     | Voir les contrats (avec filtres) | Tous |
| `contrats create`                   | Créer un contrat | Gestion |
| `contrats update`              | Modifier un contrat | Gestion |
| `contrats update-mine`         | Modifier un contrat | Commercial |
| `evenements list`                   | Voir les événements (avec filtres) | Tous |
| `evenements create`                 | Créer un événement | Commercial |
| `evenements assign_support`    | Assigner un support à un événement | Gestion |
| `evenements update`            | Modifier un événement | Support |
| `collaborateurs create`             | Ajouter un collaborateur  | Gestion |
| `collaborateurs list`               | Lister les collaborateurs | Tous |
| `collaborateurs update`        | Modifier un collaborateur  | Gestion |
| `collaborateurs delete`        | Supprimer un collaborateur | Gestion |
| `help`                             | Afficher l’aide complète | Tous |
| `clear`                             | Effacer l’écran | Tous |
| `exit`                             | Quitter l’application | Tous |

➤ **Afficher l’aide complète** :
```sh
epic_events> help
```

---

## Configuration

### ➤ **Variables d’environnement**
L’application (par docker) utilise **un fichier `.env.docker`** pour la configuration Docker ou **un fichier `.env`** pour l’exécution locale.
Tu peux retrouver ces deux fichiers sur mon cloud personnel : https://cloud.nodehub.cloud/index.php/s/zRwmWGxcCxAjxZC. N'oublie pas de les ajouter à la racine du projet et de rajouter un "." devant le nom du fichier.
> **Si tu utilises Docker**, **ajoute ton DSN Sentry manuellement** lors du lancement :
```sh
SENTRY_DSN="https://votre_dsn_sentry" docker-compose up --build
```

---

## Licence
Ce projet est sous licence **MIT**.

---
