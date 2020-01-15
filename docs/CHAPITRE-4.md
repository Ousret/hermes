<h1 align="center">La détection d'un message électronique</h1>

## ✨ Un détecteur et ses critères de recherche et d'extraction

Tout d'abord, la première tâche consiste à donner la capacité à Hermes de pouvoir 
identifier un message électronique et de lui assigner une étiquette.

**Un détecteur :** C'est un sac avec une libellé unique contenant un emsemble de critères vérifiant la nature d'un message.

**Un critère ou une règle :** C'est la capacité de vérifier la présence de qqch (unitaire) dans un message et d'en conserver la valeur dans une variable si nécessaire.

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
Dirigeons-nous sur le menu "Critères de recherche" puis "Expression exacte". Ensuite appuyons sur le bouton "Créer".

<p align="center">
<img width="606" alt="Capture d’écran 2020-01-09 à 09 23 42" src="https://user-images.githubusercontent.com/9326700/72050576-c39acb00-32c1-11ea-8316-6c070e0f5632.png">
</p>

⚠️ Un critère peut ne pas être obligatoire, néanmoins soyez sûr qu'il existe au moins un critère obligatoire. Sans quoi le détecteur ne sera pas exploitable.

### Tester la détection

Il est possible de vérifier que le détecteur fonctionne bien en amont. Pour cela il existe une zone de test en bas à droite de votre écran.
Cette boîte semi-cachée se nomme "Simulation de détection" et vous propose trois méthodes de simulation :

Soit :

  - Avec du texte brute contre l'ensemble des détecteurs
  - Avec du texte brute contre un seul détecteur de votre choix
  - Avec un message électronique *.eml ou *.msg de votre choix contre l'ensemble des détecteurs

❓ Vous pouvez effectuer un "Drag & Drop" de votre message électronique depuis votre client de messagerie favoris jusque dans la zone 
"Simulation de détection" délimitée en pointillé.

<p align="center">
<img width="483" alt="Capture d’écran 2020-01-09 à 09 36 12" src="https://user-images.githubusercontent.com/9326700/72051396-7fa8c580-32c3-11ea-9753-fa1bddf9a6bc.png">
</p>

❓ Pour le client internet Gmail il est possible de télécharger un fichier *.eml depuis "Plus" > "Afficher l'original" > "Télécharger"

Une fois que notre *facture icloud* a été déposée sur l'espace "Drag & Drop" nous pouvons observer :

<p align="center">
<img width="667" alt="Capture d’écran 2020-01-09 à 09 38 38" src="https://user-images.githubusercontent.com/9326700/72051584-dd3d1200-32c3-11ea-9885-01e044331ae1.png">
</p>

Dans le cas contraire, si le message ne correspond pas à votre détecteur, nous allons observer :

<p align="center">
<img width="666" alt="Capture d’écran 2020-01-09 à 09 41 46" src="https://user-images.githubusercontent.com/9326700/72051832-44f35d00-32c4-11ea-88d6-5d0957887f41.png">
</p>

#### 2/ Vérifier que le sujet contient bien

Nous allons créer un critère *Expression exacte* une seconde fois pour cette fois ci vérifier que le sujet contient bien : 
"Votre facture Apple". Parce que verifier l'expéditeur n'est pas suffisant.

<p align="center">
<img width="611" alt="Capture d’écran 2020-01-09 à 09 53 46" src="https://user-images.githubusercontent.com/9326700/72052790-18404500-32c6-11ea-857d-cff6d8b3e9b3.png">
</p>


#### 3/ Récupérer la capacité de stockage iCloud

Maintenant nous allons essayer de récupérer la quantité de stockage iCloud de ce message. 
Pour ce faire, nous allons utiliser un critère *Recherche d'expression*.

Nous savons que notre cible se situe entre `Forfait de stockage iCloud :` et `Go`.

Cette fois-ci nous allons conserver le résultat du critère dans une variable nommée `quantite_stockage_icloud`.

<p align="center">
<img width="608" alt="Capture d’écran 2020-01-09 à 09 58 45" src="https://user-images.githubusercontent.com/9326700/72053145-c0eea480-32c6-11ea-83dd-e9a10bdcd59d.png">
</p>

#### 🎉 Vérification du détecteur

À nouveau, nous vous conseillons toujours de re-vérifier le bon fonctionnement de la détection. Cette fois-ci nous devriions avoir :

<p align="center">
<img width="773" alt="Capture d’écran 2020-01-09 à 10 00 28" src="https://user-images.githubusercontent.com/9326700/72053232-e2e82700-32c6-11ea-9cca-630048806da3.png">
</p>

Magnifique, non ?

### Concept avancé

Vous êtes suceptible de vouloir capturer beaucoup plus de données sans pour autant savoir 
comment ? 

Par ex. nous pouvons être interessé par le montant total de la facture iCloud.

#### L'auto-détection, la pré-lecture du moteur Hermes

Hermes est capable de resortir sans effort des données qui semble être importante. Plus simplement, tout ce qui à A associe B est capturé.
Le message d'Apple est organisé avec un tableau et la dernière ligne nous interesse.

Recommençons l'opération "Drag & Drop" et cette fois-ci arrêtons nous à "Ce que le moteur perçoit".

<p align="center">
<img width="1198" alt="Capture d’écran 2020-01-09 à 10 11 40" src="https://user-images.githubusercontent.com/9326700/72054170-c220d100-32c8-11ea-957e-5c96426cd5a1.png">
</p>

Le moteur créer ce que l'on va appeler des **clés**, ici soulignées en **rouges**. Elles sont auto-découvertes et permettent de simplifier votre 
création de détecteur.

#### L'auto-détection, comment en profiter ?

Nous constatons que le moteur découvre une information `total`. Nous allons créer un critère de type *Clé*.

<p align="center">
<img width="612" alt="Capture d’écran 2020-01-09 à 10 22 25" src="https://user-images.githubusercontent.com/9326700/72054813-ff399300-32c9-11ea-9e6f-020b488ab5e2.png">
</p>

Nous allons stocker le résultat du critère dans la variable `montant_facture_icloud`.

Et maintenant, vous pouvez re-vérifier le fonctionnement de votre détecteur.

<p align="center">
<img width="798" alt="Capture d’écran 2020-01-09 à 10 22 45" src="https://user-images.githubusercontent.com/9326700/72054948-3b6cf380-32ca-11ea-863b-6fa68e20cc34.png">
</p>

Et voilà ! 

⚠️ Petite note pour l'exploitation de la variable `{{ montant_facture_icloud }}`, elle sortira comme `0,99 €` et non pas comme `0.99`. N'oubliez pas d'y appliquer le filtre 
`|float`.

## Pour aller plus loin

  - [ ] [Créer un automate en réaction à une détection de message électronique](CHAPITRE-5.md)

