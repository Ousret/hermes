<h1 align="center">Boîtes de messagerie électronique (IMAP)</h1>

## ✨ Configuration

Tout le principe d'Hermes est de réagir à une certaine typologie de message électronoqie.
Nous avons alors besoin d'une source de données dans laquelle lire les messages en entrés.

Le programme permet, clé en main de configurer l'accès à une boite IMAP4 en sachant :

  - Hôte distante (IP ou DNS)
  - Nom d'utilisateur pour s'authentifier
  - Mot de passe associé à l'utilisateur
  - Dossier dans lequel se placer pour lire et analyser les messages, par défaut **INBOX**.

Pour cela, nous vous invitons à vous rendre dans le menu "Sources de données" puis "Boite aux lettres (IMAP)".
Une fois sur la liste des boîtes, nous vous invitons à cliquer sur "Créer".

🔒 Nous vous conseillons de laisser coché "TLS" et "Vérification Certificat" pour plus de sécurité.
❓ La case **Activation** permet d'autoriser Hermès à inclure cet automate lors de la surveillance de(s) boite(s) IMAP. Inversement pour test(s) uniquement(s).
⚠️ L'option "Legacy TLS" permet d'essayer de négocier une connexion sur un serveur ayant des protocols déchus. Cette option est déconseillée et risque de ne pas fonctionner selon vos installations locales. (openssl)

## Utilisation de variable

Les champs **Hôte distante**, **Nom d'utilisateur**, **Mot de passe** peuvent contenir des variables au format `{{ ma_variable }}`.

## Fournisseurs compatibles

N'importe quel fournisseur de messagerie est compatible, mais sachez que certain fournisseur exige un niveau 
d'authentification plus important que le couple *utilisateur, mot de passe*.

Pour que GMail soit compatible, il faut d'abord activer l'accès moins sécurisée. (cf. google)

## Pour aller plus loin

  - [ ] [Détecter un message électronique](CHAPITRE-4.md)
