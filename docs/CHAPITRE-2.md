<h1 align="center">Création des variables globales</h1>

## ✨ C'est quoi ?

Juste avant, nous avons parlé des variables *simplifiées* sous Hermes. Pour mémo, les variables peuvent être issus de :

  - Le résultat d'un critère de recherche
  - **Une variable accessible globalement**, depuis le menu "Mes variables globales"
  - Le résultat d'une action

Il est parfois très utile de disposer d'une variable partagée peut-importe l'automate, comme par exemple vos identifiants SMTP pour envoyer un message.

## Où ?

La création de vos variables globales est possible depuis le menu "Mes variables globales".

<p align="center">
<img width="1619" alt="Capture d’écran 2020-01-08 à 13 23 15" src="https://user-images.githubusercontent.com/9326700/71977838-26d12280-321a-11ea-8595-9e93d0626ede.png">

<img width="1140" alt="Capture d’écran 2020-01-08 à 13 23 26" src="https://user-images.githubusercontent.com/9326700/71977824-1a4cca00-321a-11ea-80e7-7939b8f2613d.png">
</p>

## Choix de format

### Classique

La désignation représente le nom de votre future variable. 

Imaginons que vous souhaiteriez conserver le nom d'utilisateur et le mot de passe SMTP.

Vous allez créer deux variables, l'une `identifiant_smtp` et l'autre `mot_de_passe_smtp`.
Qui seront par la suite accessible par la syntaxe `{{ identifiant_smtp }}`.

Vous remplirez comme suit :

<p align="center">
<img width="860" alt="Capture d’écran 2020-01-08 à 13 28 21" src="https://user-images.githubusercontent.com/9326700/71978070-c1c9fc80-321a-11ea-94d1-cc7518ffc8a9.png">
</p>

### Avancé

Si vous le souhaitez, vous pouvez exploiter une valeur plus complexe. Vous pouvez insérer dans *Valeur* :

  - Une chaîne JSON
  - Une chaîne YAML

Reprenons notre cas ci-dessus. Au lieu de créer deux variables `identifiant_smtp` et l'autre `mot_de_passe_smtp`, 
créons une seule variable `mon_compte_smtp`.

Pour ce faire nous constituons une chaîne **JSON** tel que :

```json 
{
    "mon_compte_smtp": {
        "identifiant": "abcdef@mon-provider.com",
        "mot_de_passe": "azerty"
    }
}
```

Et donc en remplissant le formulaire de cette manière :

<p align="center">
<img width="1175" alt="Capture d’écran 2020-01-08 à 13 34 03" src="https://user-images.githubusercontent.com/9326700/71978407-8da30b80-321b-11ea-82bb-58b469cccb37.png">
</p>

Vous allez pouvoir invoquer `{{ mon_compte_smtp.identifiant }}` et `{{ mon_compte_smtp.mot_de_passe }}`.

⚠️ Vous remarquerez que le nom de votre variable n'est plus la **désignation** mais le nom de la clé/index racine. Ceci s'applique dans le cas où le format sélectionné est `JSON` ou `YAML`.

## Pour aller plus loin

  - [ ] [Mise en place de votre/vos boîte(s) IMAP](CHAPITRE-3.md)
