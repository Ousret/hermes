<h1 align="center">Les critères</h1>

Nous développons ici pour chaque type de critère :

  - Une courte description de ce qui est recherché
  - Ce qui est capturé (stockable dans une variable)

## Identifiant

La recherche d'identifiant correspond à tout ce qui ressemble à PREFIXE-NUMEROS.

```
Ticket D91827631 : Changement majeur de l'infra PBX-FR
```

**Exemple :** « On recherche un identifiant commençant par la lettre D dans le titre du message »

**Capture :** D91827631

Ici le préfixe est `D`. 

## Recherche d'expression

Rechercher une expression localisable

```
Bienvenue à Antoine GAUTIER au sein de la ville de Paris
```

**Exemple :** « Je recherche une expression comprise entre, ‘Bienvenue à’... et ...’au sein de la ville de Paris’ dans le corps du message »

**Capture :** `Antoine GAUTIER`

## Date

Trouver une date peu importe le format de représentation sachant le prefixe.
  - RFC 3339
  - RFC 2822
  - Y-m-d
  - d-m-Y

```
Bilan du 10/11/2020 pour le concours d'excellence
```

**Exemple :** « Je recherche une date juxtaposée à l’expression ‘Bilan du‘ dans le titre du message »

**Capture :** `10/11/2020`

## XPath (HTML)

Trouver un noeud dans un arbre XML soit le corps HTML de votre message.

```html
<html>
<body>
<div class="sujet">
Bonjour !
</div>
</body>
</html>
```

**Exemple :** « Je souhaite extraire le contenu de la première div ayant la classe .sujet »

**Capture :** `Bonjour !`

## Clé

**Brève explication :** Le programme Hermès arrive à trouver automatiquement certaine association explicite dans un texte.
Toute expression sous la forme de A -> B (A associé à B). Exemple : « Contact Externe : Ahmed TAHRI » 
Dans cet exemple, « Contact Externe » sera la clé auto-découverte.

```
Bonjour Michael,

Votre ticket de support numéro 761637 est maintenant ouvert.

Corresp. interne : Dep. RH
Contact Externe : Ahmed TAHRI

Merci de votre patience.
```

**Exemple :** « Je vérifie que le moteur a trouvé la clé ‘Contact Externe’ dans le message »

**Capture :** `Ahmed TAHRI`

## Expression exacte dans la clé

Permet de vérifier la présence d'un mot ou d'une suite de mot depuis la valeur associée à une clé auto-découverte par 
Hermès.

**Exemple :** « Je vérifie que la clé ‘Contact Externe’ contient bien »

**Capture :** `Ahmed TAHRI`