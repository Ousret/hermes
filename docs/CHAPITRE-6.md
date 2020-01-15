<h1 align="center">Éditer les actions d'un Automate</h1>

**Pré-requis:** Avoir mis en place au moins un détecteur et la description associée d'un automate.

## ✨ Éditeur d'un automate

Une fois la description de votre automate effectuée, nous vous invitons à revenir sur le menu "Éditeur d'Automate".

Nous vous invitons à choisir votre automate correspondant depuis la zone "Choisir Automate".

<p align="center">
<img width="1410" alt="Capture d’écran 2020-01-09 à 10 59 26" src="https://user-images.githubusercontent.com/9326700/72057722-20e94900-32cf-11ea-829d-712de0866909.png">
</p>

N'hésitez pas à regarder le volet des "variables" disponibles en appuyant sur le bouton en bas à droite.
Nous constatons que nos deux variables du détecteur sont disponibles. C'est bon signe.

## 👁️ Comprendre l'interface d'édition des Automates

Un assistant visuel vous permet de faire le tour de l'interface étape par étape. Nous vous invitons, 
au moins une fois à cliquer sur "Guide de l'interface".

<p align="center">
<img width="1227" alt="Capture d’écran 2020-01-09 à 11 07 57" src="https://user-images.githubusercontent.com/9326700/72058390-4fb3ef00-32d0-11ea-8b45-1c69f6bb778a.png">
</p>

## ✍️ Actions & Scénario 

Hermes remplace vos traitements répétitifs en vous permettant de créer une suite d'actions.

Cette suite d'actions s'organise en arbre binaire, chaque action possède deux issues, l'une en cas de **réussite**, l'autre en cas **d'échec**.

Vous pouvez modifier votre arbre d'actions avec les boutons suivants :

  - Nouvelle Action
  - Supprimer Action
  - Modifier Action
  - Remplacer Action

## Actions

Les actions disponibles sur étagère sont les suivantes :

| Type d'Action                                  | Description                                                                                                               |
|------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| RequeteSqlActionNoeud                          | Effectuer une requête de type SQL sur un serveur SGDB tel que Oracle, MySQL, PosgreSQL, Microsoft SQL Serveur et MariaDB. |
| RequeteSoapActionNoeud                         | Effectuer une requête de type SOAP Webservice.                                                                            |
| RequeteHttpActionNoeud                         | Effectuer une requête de type HTTP sur un serveur distant.                                                                |
| EnvoyerMessageSmtpActionNoeud                  | Ecrire un message électronique vers n- tiers via un serveur SMTP.                                                         |
| TransfertSmtpActionNoeud                       | Transférer le message électronique d'origine vers n-tiers via un serveur SMTP.                                            |
| ConstructionInteretActionNoeud                 | Construire une variable intermédiaire.                                                                                    |
| ConstructionChaineCaractereSurListeActionNoeud | Fabriquer une chaîne de caractère à partir d'une liste identifiable.                                                      |
| InvitationEvenementActionNoeud                 | Emettre ou mettre à jour une invitation à un évènement par message électronique.                                          |
| VerifierSiVariableVraiActionNoeud              | Vérifie si une variable est Vrai.                                                                                         |
| ComparaisonVariableActionNoeud                 | Effectue une comparaison entre deux variables de votre choix, nombres, dates, etc..                                       |
| DeplacerMailSourceActionNoeud                  | Déplacer le message électronique d'origine dans un autre dossier.                                                         |
| CopierMailSourceActionNoeud                    | Copier le message électronique d'origine dans un autre dossier.                                                           |
| SupprimerMailSourceActionNoeud                 | Supprimer le message électronique d'origine                                                                               |
| TransformationListeVersDictionnaireActionNoeud | Création d'une variable intermédiaire sachant une liste [{'cle_a': 'val_a', 'cle_b': 'val_b'}] vers {'val_a': 'val_b'}.   |
| ItopRequeteCoreGetActionNoeud                  | Effectuer une requête sur iTop avec l'opération core/get REST JSON                                                        |
| ItopRequeteCoreCreateActionNoeud               | Effectuer une requête sur iTop avec l'opération core/create REST JSON                                                     |
| ItopRequeteCoreUpdateActionNoeud               | Effectuer une requête sur iTop avec l'opération core/update REST JSON                                                     |
| ItopRequeteCoreApplyStimulusActionNoeud        | Effectuer une requête sur iTop avec l'opération core/apply_stimulus REST JSON                                             |
| ItopRequeteCoreDeleteActionNoeud               | Effectuer une requête sur iTop avec l'opération core/delete REST JSON                                                     |
| ExecutionAutomateActionNoeud                   | Exécute un autre Automate (routine ou plugin)                                                                             |

Chaque action nécessite de remplir n argument(s).
Les arguments communs sont les suivants :

  - designation (Courte description de votre action)
  - friendly_name (Précise dans quel nom de variable le résultat doit être stocké)

### Scénario fictif

Pour traiter nos factures iCloud, nous allons employer le scénario suivant :

  - Si le montant de la facture est inférieur à 1.00 EUR on supprime le message immédiatement
  - Sinon on effectue une requête http sur un serveur distant pour l'informer de la facture
  - Dans le cas ou facture >= 1.00 EUR on la conserve dans le dossier IMAP iCloud

Pour cela nous allons utiliser les actions de la manière suivante :

  - ComparaisonVariableActionNoeud
    - RequeteHttpActionNoeud
      - DeplacerMailSourceActionNoeud
  - SupprimerMailSourceActionNoeud

### Création d'une action

Pour créer une nouvelle action, nous vous invitons à cliquer sur "Nouvelle Action".

1) Choisir le type d'action.
2) (Optionnel) choisir l'action parente et la branche fils, échec ou réussite.
3) Renseigner les arguments de l'assistant.

Captures, dans l'ordre.

<p align="center">
<img width="864" alt="Capture d’écran 2020-01-09 à 11 14 53" src="https://user-images.githubusercontent.com/9326700/72060018-7162a580-32d3-11ea-8f73-e34f50f21b18.png">
<img width="583" alt="Capture d’écran 2020-01-09 à 11 17 29" src="https://user-images.githubusercontent.com/9326700/72060045-850e0c00-32d3-11ea-84c4-8ba6d1c7762b.png">
<img width="478" alt="Capture d’écran 2020-01-09 à 11 17 35" src="https://user-images.githubusercontent.com/9326700/72060047-86d7cf80-32d3-11ea-9ff5-3d34351db115.png">
</p>

⚠️ Les deux dernières captures n'apparaissent que lorsque la première action a déjà été créée. L'action racine n'a pas de parent et elle s'exécute obligatoirement.

### Arguments d'une action

Chaque action nécessite n argument(s) obligatoire(s) et n optionnel(s). Chaque argument peut contenir des variables.

<p align="center">
<img width="482" alt="Capture d’écran 2020-01-09 à 11 15 46" src="https://user-images.githubusercontent.com/9326700/72060031-7aec0d80-32d3-11ea-8804-086afd515c03.png">
</p>

Un support de completion automatique est disponible dans la mesure du raisonable.

⚠️ Aucun support de marche arrière n'est disponible. Ceci est une limitation de la bibliothèque sweetalert2.
L'assistant de création des actions ne permet pas de revenir à une étape antérieur.

### L'arbre des actions

<p align="center">
<img width="1027" alt="Capture d’écran 2020-01-09 à 11 21 41" src="https://user-images.githubusercontent.com/9326700/72060066-8dfedd80-32d3-11ea-90d0-217ee608a121.png">
</p>

Une fois vos actions mises en place. L'éditeur vous proposera une représentation visuelle de votre arbre d'action.

### Modifier l'arbre

Vous pouvez insérer dans l'arbre, supprimer et remplacer. 
Sachez qu'Hermes tentera de rééquilibrer l'arbre en priviligiant toujours la branche de **réussite**.

## Pour aller plus loin

  - [ ] [Test et debug d'un automate](CHAPITRE-7.md)
