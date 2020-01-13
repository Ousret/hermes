<h1 align="center">Automates programmables IMAP4 pour les humains 👋 <a href="https://twitter.com/intent/tweet?text=Hermes%20&url=https://www.github.com/Ousret/hermes&hashtags=python,imap,automatons,developers"><img src="https://img.shields.io/twitter/url/http/shields.io.svg?style=social"/></a></h1>

<p align="center">
<a href="https://travis-ci.org/Ousret/hermes" target="_blank"><img src="https://travis-ci.org/Ousret/hermes.svg?branch=master" alt="Travis-CI Build Badge"></a>
<a href="https://www.codacy.com/manual/Ousret/hermes?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Ousret/hermes&amp;utm_campaign=Badge_Grade"><img alt="Codacy Badge" src="https://api.codacy.com/project/badge/Grade/858f5795316e4786a6f8c39d25535756"/></a>
<a href="https://github.com/ousret/hermes/blob/master/LICENSE">
   <img alt="License: NPOSL-3.0" src="https://img.shields.io/badge/license-NPOSL-purple.svg" target="_blank" />
</a>
</p> 

> Hermès est une divinité issue de la mythologie grecque. Messager des dieux.

![hermes](https://user-images.githubusercontent.com/9326700/71805247-0eb8a200-3066-11ea-90a8-a58477ce5e8f.jpg)

<sub><sup>Les noms et logos `iTop` et `Microsoft Exchange` sont affichés à titre d'exemple uniquement. 
N'importe quel service IMAP fonctionne avec Hermes. De même qu'iTop est UN des services sur lequel vous pouvez émettre des requêtes. Hermes n'est pas affilié à Combodo (iTop) ni à Microsoft (Exchange).</sup></sub>

## Contributions

Merci d'offrir une ⭐ à ce projet s'il vous a été utile. Encore mieux, participez en : 
  - Signalant un problème
  - Proposant un correctif via le système de pull request
  - Proposant des fonctionnalités/idées utiles à tous

## 🍰 Quel besoin ?

Ce projet est né d'un besoin spécifique qui a laissé entrevoir la possibilité d'un cas bien plus ouvert et générique.
Une entreprise peut-être confrontée à cette problématique : 

**Comment gérer une interopérabilité des services avec n-tiers en se basant uniquement sur les échanges électroniques ?**

L'origine est qu'une entreprise utilisant le programme ITSM iTop et l'Incoming Mail (Scanner de boîte mail).
La description officielle du module iTop est la suivante : `This extension runs in the background to scan the defined mail inbox(es) and either create or update tickets based on the content of the incoming emails.`

Avec l'ancienne solution (non exhaustif) :

1) Impossible d'identifier clairement et automatiquement un message
2) Obligation de créer des dossiers IMAP pour n opération(s)
3) Les actions du scanner sont limitées à des simples opérations

Ils se sont retrouvés extrêment limitée par l'Incoming Mail.

Hermes offre une solution complète à ce qu'iTop ne peux pas fournir.

## ✨ Installation

Le projet Hermes s'installe et s'execute très facilement de deux manières. À condition d'avoir :

  - Un compte IMAP et SMTP utilisable
  - Environnement Linux, Unix ou Windows au choix

Quelque soit votre méthode préférée, commencez par :

```shell script
cd $HOME
git clone https://github.com/Ousret/hermes.git
cd ./hermes
cp configuration.dist.yml configuration.yml
```

Modifions d'abord la configuration à l'aide de votre éditeur préféré, `nano`, `vim`, etc..

```shell script
nano configuration.yml
```

```yaml
PRODUCTION: &production
  <<: *common
  SECRET_KEY: MerciDeMeChangerImmediatementAvantPremierLancement  # Remplacer par une longue chaîne de caractère aléatoire 
  # *-* configuration smtp *-* à utiliser pour envoyer les rapports d'erreurs
  EMAIL_HOST: 'hote-smtp'
  EMAIL_PORT: 587
  EMAIL_TIMEOUT: 10
  EMAIL_USE_TLS: True
  EMAIL_HOST_USER: 'smtp-utilisateur@hote-smtp'
  EMAIL_HOST_PASSWORD: 'secret_smtp'
  EMAIL_FROM: 'smtp-utilisateur@hote-smtp'
  INCIDENT_NOTIFIABLE: 'destinataire@gmail.com' # Remplacer par l'adresse email à laquelle transmettre un rapport d'erreur
```

### Méthode 1 : AVEC Docker

En ayant déjà installé `docker` et `docker-compose` sur votre machine, vous n'avez plus qu'à lancer :

```shell script
docker-compose up
```

### Méthode 2 : SANS Docker

Les pré-requis sont les suivants : `python3`, `pip`, `nodejs`, `npm`. Optionnellement `mariadb-server` et `mariadb-client`.

```shell script
pip install certifi pyopenssl --user
npm install yarn -g

python setup.py install --user
cd ./hermes_ui
yarn install
yarn build
cd ..
```

La seconde méthode nécessite de mettre en oeuvre une base de données. Si vous êtes sous `mariadb`, connectez-vous et créez une base de données `hermes`.

```mysql
CREATE DATABASE hermes;
```

Si vous n'avez pas `mariadb`, vous pouvez opter pour un système léger `sqlite` qui ne nécessite rien de plus.

Dans le fichier `configuration.yml`, modifiez le paramètre suivant :

```yaml
PRODUCTION: &production
  <<: *common
  SQLALCHEMY_DATABASE_URI: 'mysql://utilisateur:mdp@127.0.0.1/hermes'
```

Si vous ne souhaitez pas mettre en place `mariadb`, remplacez par :

```yaml
PRODUCTION: &production
  <<: *common
  SQLALCHEMY_DATABASE_URI: 'sqlite:///hermes.sqlite'
```

### APRÈS Méthode 1 OU 2

Ouvrir le navigateur à l'adresse suivante : [http://127.0.0.1:5000](http://127.0.0.1:5000)
L'utilisateur par défaut est `hermes@localhost` et le mot de passe associé est `admin`. 
Il est bien entendu sage de le modifier rapidement après la 1ere connexion.

<p align="center">
<img width="900" alt="Capture d’écran 2020-01-10 à 15 59 14" src="https://user-images.githubusercontent.com/9326700/72162392-325f4d80-33c2-11ea-9d10-8d4a5ec19bb1.png">
</p>

## ⚡ Comment ça marche ?

![hermes-principes](https://user-images.githubusercontent.com/9326700/71805268-2001ae80-3066-11ea-9e8e-386044ddd621.gif)

En bref, 

Un message électronique est reçu, nous arrivons, grâce à une suite de critères à définir la nature du message tout en conservant les résultats de l'évaluation 
des critères.  Ensuite une suite d'actions déterminées par le concepteur s'enchainera en arbre binaire, chaque action se solde par une réussite ou un échec et prend la branche correspondante 
pour exécuter l'action suivante.

## 👤 Documentations

Cette section vous propose de prendre en main rapidement Hermes.

  - [ ] [Comprendre le mécanisme des variables simplifiées sous Hermes](docs/CHAPITRE-1.md)
  - [ ] [Écrire et enregistrer vos variables partagées / globales](docs/CHAPITRE-2.md)
  - [ ] [Configurer votre/vos boîte(s) IMAP](docs/CHAPITRE-3.md)
  - [ ] [Détecter un message électronique](docs/CHAPITRE-4.md)
  - [ ] [Créer un automate en réaction à une détection de message électronique](docs/CHAPITRE-5.md)
  - [ ] [Mettre en oeuvre une suite d'action à appliquer après la détection](docs/CHAPITRE-6.md)
  - [ ] [Test et debug d'un automate](docs/CHAPITRE-7.md)

Pour aller encore plus loin :

  - [ ] [Les critères de détection](docs/CRITERES.md)
  - [ ] [Les actions](docs/ACTIONS.md)  

## 🚧 Maintenance

Ce programme n'est qu'à ses balbutiements. 
Hermès est stable et disponible pour la production. Ce projet peut être amélioré, des idées d'évolutions significatives sont à l'étude.

Un projet Github est ouvert avec l'ensemble des idées / tâches à réaliser pour rendre ce projet incroyable.

Pour le moment, j'adresse la maintenance concernant les bugs et la sécurité et je relis et j'approuve les contributions soumises.

## 📝 Droits

**L'exploitation commerciale est strictement interdite tandis que l'usage interne professionnel est autorisée.**

Publication sous "Non-Profit Open Software License 3.0 (NPOSL-3.0)"

## Contributeur(s) :

  - Ahmed TAHRI @Ousret, Développeur et mainteneur
  - Didier JEAN ROBERT @SadarSSI, Conception / expression de besoins
