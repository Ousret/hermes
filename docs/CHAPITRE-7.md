<h1 align="center">Tester & Débugger un Automate</h1>

**Pré-requis:** Avoir mis en place au moins un détecteur, la description d'un automate associée ainsi que des actions prêtes.

## ✨ Phase finale de conception

Lors de la création d'un **détecteur** nous avions vu qu'il est possible de le tester au fur et à mesure de la conception.
Il en va de même pour la création des actions d'un automate.

### Mode de test et de prodution

Dans la zone "Choisir Automate" et aussi dans la boîte de dialogue création "Description d'un Automate", 
il y a une option "Production".

Cette checkbox, décochée, permet d'empêcher le moteur de surveillance continue de votre boîte IMAP d'exécuter votre automate.

Pendant la phase de conception il est recommandé de laisser votre automate en mode test. Donc checkbox décochée.

### Lancer l'automate seul

Depuis la page "Éditeur d'Automate", selectionnez votre automate depuis la zone "Choisir Automate". 
Puis une fois dans cet état.

<p align="center">
<img width="1027" alt="Capture d’écran 2020-01-09 à 11 21 41" src="https://user-images.githubusercontent.com/9326700/72060066-8dfedd80-32d3-11ea-90d0-217ee608a121.png">
</p>

Cliquez sur "Tester Automate", puis confirmer le démarrage.

⚠️ Une limitation empêche de pouvoir conduire un test autrement que depuis votre boîte IMAP.
Ce qui signifie que vous devez vous assurer que :

  - Votre message type est disponible dans le dossier dans lequel Hermes ira lire les messages
  - La boucle de surveillance des messages est suspendue
  - Votre automate est en mode test

Une fois les critères réunis, vous observerez le résultat en temps réel depuis la zone console.

<p align="center">
<img width="1382" alt="Capture d’écran 2020-01-09 à 15 18 04" src="https://user-images.githubusercontent.com/9326700/72075096-5b64dd00-32f3-11ea-8652-7baf9b03bc37.png">
</p>

### Résultat d'un automate

Un automate termine par une réussite si la dernière action de l'arbre se termine correctement.

## 📊 Historique des lancements

Hermes permet de consulter les 50 derniers lancements que ce soit en mode production ou de test depuis la zone 
"Historique des exécutions".

### 😞 Les erreurs critiques

Une erreur critique est qqch qui ne se rattrape pas et qui empêche l'automate d'aboutir. Par ex. une variable non résolue.

⚠️ Les automates qui se solde par une erreur critique n'apparaissent pas dans l'historique. Néanmoins un message électronique est 
envoyé à :

  - Adresse de messagerie `INCIDENT_NOTIFIABLE` parametrée dans **configuration.yml**
  - Dernier éditeur de l'automate
  - Créateur de l'automate

Ce rapport contient autant d'information que possible pour assister à la résolution.

### Debug

Pour chaque rapport d'execution existe une ligne dans le tableau "Historique des exécutions". 
Ce tableau s'actualise lui aussi avec une latence de plus ou moins cinq secondes.

Chaque ligne offre un récapitulatif succint de l'exécution. 

![hermes_logs](https://user-images.githubusercontent.com/9326700/72078007-8f8ecc80-32f8-11ea-82b5-a803cd2e706e.jpg)

Pour consulter les détails de chaque exécution, il est possible de cliquer sur le bouton de la colonne "Info".

Vous observerez ansi un assistant similaire à celui de la création d'une action.

**Revoir comment s'est déroulé la détection**
![hermes_logs_2](https://user-images.githubusercontent.com/9326700/72078006-8f8ecc80-32f8-11ea-9238-17f700b6e4c8.jpg)
**Voir comment s'est exécutée une action et en connaître la réponse**
![hermes_logs_3](https://user-images.githubusercontent.com/9326700/72078015-90bff980-32f8-11ea-9d84-e5ce4417ba4a.jpg)

⚠️ Les caches sur les images ne représentent pas la réalité, et sont ici pour protéger la confidentialité de mon environnement de production.

