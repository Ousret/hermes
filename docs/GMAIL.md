<h1 align="center">GMail</h1>

Nous allons vous guidez dans la mise en oeuvre de la connexion à votre compte GMail.

## Authentification

Hôte IMAP : `imap.gmail.com`
Hôte SMTP : `smtp.gmail.com`
utilisateur : `mon_compte@gmail.com`

mot de passe : **Vous ne pouvez pas utiliser votre mot de passe habituel ! Vous devez en créer un spécialement pour hermes.**

D'abord recherchez "gmail generate app password" sur Google.

```
Create & use App Passwords
Go to your Google Account.
On the left navigation panel, choose Security.
On the "Signing in to Google" panel, choose App Passwords. ...
At the bottom, choose Select app and choose the app you're using.
Choose Select device and choose the device you're using.
Choose Generate.
```

[Générer son mot de passe d'Application](https://support.google.com/accounts/answer/185833?hl=fr)

## Configuration GMAIL nécessaire

Google dispose d'une implémentation IMAP4 modifiée et cela risque de poser un problème lors de la suppression des messages.
Cela vient de la manière dont les instructions `DELETE` et `EXPUNGE` sont interprétées.

Si vous souhaitez pallier à ce problème de message non supprimable depuis Hermès :

  - Connectez-vous sur votre compte gmail depuis votre navigateur internet.
  - Une fois sur votre boite de reception, choississez réglages, en haut à droite de la liste des messages. (Roue crantée puis réglages.)
  - Choisir l'onglet 'Boîte de réception' 
  - Cochez le bouton radio 'Laisser le client mail choisir pour la suppression'
  - À votre convenance, choisir comment sera interprété la suppression. (i) suppression immédiate (ii) déplacer dans corbeille.

<img width="1083" alt="Capture d’écran 2020-03-12 à 08 50 32" src="https://user-images.githubusercontent.com/9326700/76499214-97750500-643e-11ea-9c03-3f58b789ba21.png">
