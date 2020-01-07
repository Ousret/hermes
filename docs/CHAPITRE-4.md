<h1 align="center">La détection d'un message électronique</h1>

## ✨ Un détecteur et ses critères de recherche et d'extraction

Tout d'abord, la première tâche consiste à donner la capacité à Hermes de pouvoir 
identifier un message électronique et de lui assigner une étiquette.

**Un détecteur :** C'est un sac avec une désignation particulière contenant un emsemble de critères vérifiant la nature d'un message.

**Un critère :** C'est la capacité de vérifier la présence de qqch (unitaire) dans un message et d'en conserver la valeur dans une variable si nécessaire.

## Détecteur

Un type de message associe à un détecteur. Partons du principe que vous recevez mensuellement une facture d'iCloud par messagerie.
Nous allons créer un détecteur vide sous le nom de "Ma facture iCloud". Le menu "Détecteur" puis "Créer".

Chaque boite de dialogue d'assistance à la création est suffisament fournise en aide pour prendre en main chaque champs.

<img width="1347" src="https://user-images.githubusercontent.com/9326700/71885975-af2cc600-313b-11ea-80a6-5310dde9c7b0.png">

### Critères

Une fois le détecteur mis en place, il est temps de créer l'ensemble des critères qui identifient "Ma facture iCloud".

<img width="1285" alt="Capture d’écran 2020-01-07 à 11 04 30" src="https://user-images.githubusercontent.com/9326700/71887113-b9e85a80-313d-11ea-856b-a988f60122d5.png">

À première vue on observe dans ce message :

  - L'expéditeur est no_reply@email.apple.com
  - Le titre contient exactement "Votre facture Apple"
  - Précise la date de renouvellement à GAUCHE DE "Rnvl. le"
  - Précise l'abonnement "Forfait de stockage iCloud : XX Go"

Nous avons sur étagère une panoplie de critères prédéfinis.

<p align="center">
<img width="221" alt="Capture d’écran 2020-01-07 à 10 49 37" src="https://user-images.githubusercontent.com/9326700/71886305-41cd6500-313c-11ea-9339-0b5ff96a7dbf.png">
</p>

#### Comprendre les types de critère

| Type                          | Description                                                                                                                                                           |
|-------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Identifiant                   | Critère simplifié permettant de trouver un identifiant.                                                                                                               |
| Recherche d'expression        | Critère simplifié permettant de trouver une expression localisable avec l’expression immédiatement à droite et / ou immédiatement à gauche.                           |
| Date                          | Critère simplifié permettant de trouver une date peu importe le format de représentation.                                                                             |
| XPath (HTML)                  | Critère simplifié permettant de trouver un noeud dans un arbre XML soit le corps HTML de votre message                                                                |
| Expression exacte             | Critère simplifié permettant de trouver exactement une expression à l’identique.                                                                                      |
| Clé                           | Critère simplifié permettant de vérifier l’existence d’une « clé » auto-découverte par le moteur.                                                                     |
| Expression exacte dans la clé | Critère simplifié permettant de vérifier l’existence d’une « clé » auto-découverte par le moteur et de trouver exactement une expression à l’identique dans celle-ci. |
| Expression régulière          | Critère complexe permettant de vérifier l’existence de qqch sachant une expression régulière.                                                                         |
| Information balisée           | Critère simplifié permettant de trouver une chaîne contenue entre balise [ ainsi que ] ou commençant par le symbole dièse #.                                          |
| Opération sur critère(s)      | Critère compilant une suite de critères simplifiés ou complexes en appliquant une opération sur ceux-ci. (AND, NOT, XOR, OR)                                             |

Par défaut, un critère s'exécute sur l'intégralité d'un message électronique. Il est possible de limiter la recherche à :

  - Titre
  - Corps
  - Champ expéditeur
  - Champ destinataire
  - Liste des URLs auto-découvertes
  - Liste des noms de PJ
  - Liste des types de PJ

#### 1/ Vérifier l'expéditeur

Nous allons créer un critère *Expression exacte* pour trouver exactement *no_reply@email.apple.com* dans le champ *expéditeur*.

