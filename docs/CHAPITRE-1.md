<h1 align="center">Comprendre le fonctionnement des variables sous d'Hermes</h1>

## ✨ La génèse

Hermes dispose d'un moteur de variables (simplifié). 
La syntaxe d'appel des variables est similaire à celle du moteur de template Twig.

Faire appel à une variable de la manière suivante : `{{ ma_variable }}`.
Une variable commence systèmatiquement par `{{` et se termine par `}}`. 
Les espaces ne sont pas obligatoires.

##  Où ?

Vous êtes autorisé à utiliser les variables dans vos actions et dans la description de vos boîtes IMAP.
Il n'est pas possible d'utiliser les variables dans les paramètres des critères de détection.

Les variables disponibles sont accessible par un volet caché à droite.

![hermes-variables](https://user-images.githubusercontent.com/9326700/71878521-1d698c80-312c-11ea-9516-e828498c79b0.gif)

Le bouton en bas à droite vous permet de le faire apparaître et disparaître à votre guise.

Trois section sont visibles :

  - Les variables locales sont produite par un automate, ses actions ainsi que les critères de selection d'un message.
  - Les variables globales sont produite par vos entrés depuis le menu "Mes variables globales".
  - Les filtres permettent d'agir une variable, pour plus d'information, ci-dessous.

## Comment ?

Vous obtenez des variables de *TROIS* manières :

  - Le résultat d'un critère de recherche
  - Une variable accessible globalement, depuis le menu "Mes variables globales"
  - Le résultat d'une action

## Les filtres

Pouvoir stocker et réutiliser de l'information c'est bien, pouvoir la transformer c'est mieux.

| Filtre               | Description                                                                                                   | Avant              | Après        |
|----------------------|---------------------------------------------------------------------------------------------------------------|--------------------|--------------|
| escapeQuote          | Sécurise une chaîne de caractère pour une insertion dans un JSON. Traite par ex. les doubles chevrons.        | Je"suis"           | Je\\"suis\\"   |
| keys                 | Liste les clés d'un dictionnaire associatif                                                                   | {A: 0, B: 1, C: 2} | [A, B, C]    |
| int                  | Conserve UNIQUEMENT les chiffres d'une chaîne de caractère                                                    | ITOP-T-00541       | 541          |
| lower                | Chaque caractère se transforme en minuscule s'il y a lieu                                                     | ITOP-T-00541       | itop-t-00541 |
| upper                | Chaque caractère se transforme en majuscule s'il y a lieu                                                     | je suis            | JE SUIS      |
| strip                | Retire les espaces d'une chaîne de caractères                                                                 | je suis            | jesuis       |
| capitalize           | Première lettre en majuscule uniquement                                                                       | je Suis            | Je suis      |
| dateAjouterUnJour    | Prends une date US et y additionne une seule journée                                                          | 2020/01/01         | 2020/01/02   |
| dateAjouterUnMois    | Prends une date US et y additionne un mois                                                                    | 2020/01/01         | 2020/02/01   |
| dateAjouterUneAnnee  | Prends une date US et y additionne une année                                                                  | 2020/01/01         | 2021/01/01   |
| dateRetirerUnJour    | Prends une date US et y retire une journée                                                                    | 2020/01/01         | 2019/12/31   |
| dateRetirerUnMois    | Prends une date US et y retire un mois                                                                        | 2020/01/01         | 2019/12/01   |
| dateRetirerUneAnnee  | Prends une date US et y retire une année                                                                      | 2020/01/01         | 2019/01/01   |
| dateFormatFrance     | Prends une date et passe du format US à FR Y-m-d à d-m-Y                                                      | 2020/01/01         | 01/01/2020   |
| dateFormatUS         | Prends une date et passe du format FR à US d-m-Y à Y-m-d                                                      | 01/01/2020         | 2020/01/01   |
| dateProchainLundi    | Prends une date FR et remplace cette date par la date du prochain Lundi SI cette date n'est pas déjà un Lundi |                    |              |
| dateProchainMardi    | Prends une date FR et remplace cette date par la date du prochain Mardi SI cette date n'est pas déjà un Mardi |                    |              |
| dateProchainMercredi | //                                                                                                            |                    |              |
| dateProchainJeudi    | //                                                                                                            |                    |              |
| dateProchainVendredi | //                                                                                                            |                    |              |
| dateProchainSamedi   | //                                                                                                            |                    |              |
| dateProchainDimanche | //                                                                                                            |                    |              |
| slug                 | Transforme une chaîne de caractères en slug. URL-Safe String.                                                 | J'étais là         | j-etais-la   |
| alNum                | Conserve les caractères alphanumériques d'une chaîne                                                          | [##BONJOUR1]       | BONJOUR1     |
| alpha                | Conserve les caractères alpha d'une chaîne                                                                    | [##BONJOUR1]       | BONJOUR      |
| remplissage**Zero    | Rajoute des zéros en début de chaîne. Remplacer « *** » par « Un,Deux, Trois, Quatre, Cinq, etc.. »           |                    |              |

Imaginons que la variable `{{ ma_variable }}` contienne la valeur `ITOP-T-00541`. Pour en extraire la partie numérique j'applique 
le filtre `int` sur celle-ci.

```
{{ ma_variable|int }}
```

`{{ ma_variable }}` est remplacée par `ITOP-T-00541` tandis que `{{ ma_variable|int }}` est remplacée par `541`.

## Les différents types

Les variables sous Hermes ne sont qu'un *proxy* vers les variables nativements accessibles sous Python.

Ce qui signifie qu'une variable peut contenir un `int`, `str`, `float` mais aussi un `list` et `dict` !

`{{ ma_variable }}` peut contenir le `dict` suivant :

```json
{
    "nom_utilisateur": "john_doe",
    "mot_de_passe": "azerty"
}
```

Pour acceder à `nom_utilisateur` --> `{{ ma_variable.nom_utilisateur }}`.

Pour accéder à un niveau plus bas nous séparons les `étages` par un POINT.
Il est également possible d'accéder à `nom_utilisateur` de la manière suivante `{{ ma_variable.0 }}`. 

`{{ ma_variable }}` peut contenir le `list` suivant :

```json
[
  'A',
  'B',
  'C'
]
```

Pour acceder à la lettre `C`, on écrit `{{ ma_variable.2 }}`. Les index de liste commence à ZÉRO.

## Les variables imbriquées

Pour les plus aguéris, sachez que vous pouvez invoquer une variable dans une variable. Sans limite.

Imaginons que la variable `{{ ma_variable }}` contienne :

```json
{
  "tickets": {
    "561": {
      "A": 1,
      "B": 2
    }
  }
}
```

Nous souhaitons obtenir la valeur associé à `A`, soit `1`. Nous écrirons, naturellement, alors `{{ ma_variable.tickets.561.A }}`.
Néanmoins, partons du principe que nous sachons pas à l'avance que nous souhaitons passer par le niveau `561`.

Disons que si un de vos critères a réussi à capturer `561` dans la variable `mon_numero_de_ticket`.

Nous pouvons écrire : `{{ ma_variable.tickets.{{ mon_numero_de_ticket }}.A }}`, sachant qu'il sera traduit par `{{ ma_variable.tickets.561.A }}` puis `1`.
Génial, non ?

Maintenant si `{{ mon_numero_de_ticket }}` contient `Ticket 561` à la place de `561`, vous n'avez qu'à appliquer le filtre `|int` sur cette variable tel que :
`{{ ma_variable.tickets.{{ mon_numero_de_ticket|int }}.A }}`

## Pour aller plus loin

  - [ ] [Écrire et enregistrer vos variables partagées / globales](CHAPITRE-2.md)
