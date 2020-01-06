<h1 align="center">Automates programmables IMAP4 pour les humains 👋 <a href="https://twitter.com/intent/tweet?text=Hermes%20&url=https://www.github.com/Ousret/hermes&hashtags=python,imap,automatons,developers"><img src="https://img.shields.io/twitter/url/http/shields.io.svg?style=social"/></a></h1>

> Ce projet permet à un utilisateur d'identifier des messages électroniques et d'y réagir en y effectuant une suite d'action.

![hermes](https://user-images.githubusercontent.com/9326700/71805247-0eb8a200-3066-11ea-90a8-a58477ce5e8f.jpg)

## Contributions

Merci d'offrir une ⭐ à ce projet s'il vous a été utile. Encore mieux, participez en : 
  - Signalant un problème
  - Proposant un correctif via le système de pull request
  - Proposant des fonctionnalités utiles à tous

## ✨ Installation

Le projet Hermes s'installe et s'execute très facilement de deux manières.

### Méthode 1 : AVEC Docker

En ayant déjà installé `docker` et `docker-compose` sur votre machine, vous n'avez plus qu'à lancer :

```sh
docker-compose up
```

Ouvrir le navigateur à l'adresse suivante : [http://127.0.0.1:5000](http://127.0.0.1:5000)
L'utilisateur par défaut est `hermes@localhost` et le mot de passe associé est `admin`. 
Il est bien entendu sage de le modifier rapidement après la 1ere connexion.

### Méthode 2 : SANS Docker

Les pré-requis sont les suivants : `python3`, `pip`, `nodejs` et `npm`

```sh
pip install certifi pyopenssl --user
npm install yarn -g

cd $HOME
git clone https://github.com/Ousret/hermes.git
cd ./hermes
python setup.py install --user
cd ./hermes_ui
yarn install
yarn build
cd ..
python wsgi.py
```

## ⚡ Comment ça marche ?

![hermes-principes](https://user-images.githubusercontent.com/9326700/71805268-2001ae80-3066-11ea-9e8e-386044ddd621.gif)

## 🍰 Quel besoin ?

Ce projet est né d'un besoin spécifique qui a laissé entrevoir la possibilité d'un cas bien plus ouvert et générique.
Une entreprise peut-être confrontée à cette problématique : 

**Comment gérer une interopérabilité des services avec n-tiers en se basant uniquement sur les échanges électroniques ?**

## 👤 Documentations

## 📝 Droits

