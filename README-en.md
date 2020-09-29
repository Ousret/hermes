<h1 align="center">Programmable IMAP4 controllers for humans 👋 <a href="https://twitter.com/intent/tweet?text=Hermes%20&url=https://www.github.com/Ousret/hermes&hashtags=python,imap,automatons,developers"><img src="https://img.shields.io/twitter/url/http/shields.io.svg?style=social"/></a></h1>

<p align="center">
<a href="https://travis-ci.org/Ousret/hermes" target="_blank"><img src="https://travis-ci.org/Ousret/hermes.svg?branch=master" alt="Travis-CI Build Badge"></a>
<a href="https://www.codacy.com/manual/Ousret/hermes?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Ousret/hermes&amp;utm_campaign=Badge_Grade"><img alt="Codacy Badge" src="https://api.codacy.com/project/badge/Grade/858f5795316e4786a6f8c39d25535756"/></a>
<a href="https://github.com/ousret/hermes/blob/master/LICENSE">
   <img alt="License: NPOSL-3.0" src="https://img.shields.io/badge/license-NPOSL%203.0-purple.svg" target="_blank" />
</a>
<a href="https://codecov.io/gh/Ousret/hermes">
  <img src="https://codecov.io/gh/Ousret/hermes/branch/master/graph/badge.svg" />
</a>
</p> 

> Hermès is a pagan god in Greek mythology - messenger of the gods.

![hermes](https://user-images.githubusercontent.com/9326700/71805247-0eb8a200-3066-11ea-90a8-a58477ce5e8f.jpg)

<sub><sup>The names and logos of `iTop` and `Microsoft Exchange` are displayed only as samples.
Any IMAP provider or service works with Hermes, just as `iTop` is only one of the services you can use to send HTTP requests. Hermes is not affiliated with Combodo (iTop) or Microsoft (Exchange).</sup></sub>

## Contributions

Please ⭐ this project if you found it useful. Even better, contribute by : 
  - Reporting issues and problems
  - Submitting a fix with a pull request
  - Requesting features to benefit everyone

## 🍰 Why Hermes ?

This project was created with a specific use case in mind, which brought up the possibilities of a more open and generic use case.
A company may face this problem :

**How do we manage the interoperability of services with n-tiers, based only on electronic exchanges?**

A company was currently using the ITSM iTop program and the Incoming Mail (Mailbox Scanner) functionalities.
The official description of iTop is the following : `This extension runs in the background to scan the defined mail inbox(es) and either create or update tickets based on the content of the incoming emails.`

With the old solution (Incoming Mail):

1) Limited and restricted message identification
2) Forced to create IMAP files for *n* operations
3) Scanner actions are limited to basic operations

They found themselves extremely limited by Incoming Mail's functionalities.

Hermes offers a complete solution, building on what iTop cannot provide.

## ✨ Installation

Hermes is easily installed and executed in two ways. Requirements:

  - A usable IMAP / SMTP account
  - Your choice of a Linux / Unix / Windows environment

Whatever your preferred method, start by running :

```shell
cd $HOME
git clone https://github.com/Ousret/hermes.git
cd ./hermes
cp configuration.dist.yml configuration.yml
```

First, modify the configuration with your preferred text editor: `nano`, `vim`, etc..

```shell
nano configuration.yml
```

```yaml
PRODUCTION: &production
  <<: *common
  SECRET_KEY: PleaseChangeThisStringBeforeDeployment  # Replace with a long randomly generated string
  # *-* smtp configuration *-* used to send error reports
  EMAIL_HOST: 'smtp-host'
  EMAIL_PORT: 587
  EMAIL_TIMEOUT: 10
  EMAIL_USE_TLS: True
  EMAIL_HOST_USER: 'smtp-user@smtp-host'
  EMAIL_HOST_PASSWORD: 'secret_smtp'
  EMAIL_FROM: 'smtp-user@smtp-host'
  INCIDENT_NOTIFIABLE: 'destination@gmail.com' # Replace with the email to send error reports to
```

### Method 1 : WITH Docker

If you've already installed `docker` and `docker-compose` on your machine, you can simply run :

```shell
docker-compose up
```

### Method 2 : WITHOUT Docker

Requirements : `python3`, `pip`, `nodejs`, `npm`. Optional : `mariadb-server` and `mariadb-client`.

These commands may require superuser privileges. (Installing the `yarn` utility)
```bash
npm install yarn -g
```

```shell
pip install certifi pyopenssl --user

python setup.py install --user
cd ./hermes_ui
yarn install
yarn build
cd ..
```

The second method requires a database implementation. If you're using `mariadb`, connect and create a `hermes` database.

```sql
CREATE DATABASE hermes;
```

If you don't have `mariadb` installed, you can opt for a lightweight `sqlite` implementation.  

In the `configuration.yml` file, change the following parameter :

```yaml
PRODUCTION: &production
  <<: *common
  SQLALCHEMY_DATABASE_URI: 'mysql://user:mdp@127.0.0.1/hermes'
```

If you don't want to use `mariadb`, replace it with :

```yaml
PRODUCTION: &production
  <<: *common
  SQLALCHEMY_DATABASE_URI: 'sqlite:///hermes.sqlite'
```

Finally, launch `wsgi.py`.

```shell
python wsgi.py
```

### AFTER Method 1 or 2

Navigate to the following address : [http://127.0.0.1:5000](http://127.0.0.1:5000)
The default user is `hermes@localhost` and the password is `admin`. 
It's a good idea to change these after the first connection.

<p align="center">
<img width="900" alt="Capture d’écran 2020-01-10 à 15 59 14" src="https://user-images.githubusercontent.com/9326700/72162392-325f4d80-33c2-11ea-9d10-8d4a5ec19bb1.png">
</p>

## ⚡ How does it work ?

![hermes-principes](https://user-images.githubusercontent.com/9326700/71805268-2001ae80-3066-11ea-9e8e-386044ddd621.gif)

Essentially, 

An electronic **message** is received -> we use a **series of criteria** from a **detector** to find the nature of the message while preserving evaluation results -> **A series of actions** defined by the designer will be linked in a binary tree -> each action results in a **success** or a **failure** and takes the appropriate following action.

## 👤 Documentation

This section is a guide to getting started with Hermes quickly.

  - [ ] [Understanding simplified variables with Hermes](docs/CHAPITRE-1.md)
  - [ ] [Write / save global variables](docs/CHAPITRE-2.md)
  - [ ] [Configure your IMAP box(es)](docs/CHAPITRE-3.md)
  - [ ] [Detecting an email message](docs/CHAPITRE-4.md)
  - [ ] [Creating a controller in response to a message detection](docs/CHAPITRE-5.md)
  - [ ] [Implement an action sequence](docs/CHAPITRE-6.md)
  - [ ] [Test and debug the controller](docs/CHAPITRE-7.md)

Going further :

  - [ ] [Detection criteria](docs/CRITERES.md)
  - [ ] [The actions](docs/ACTIONS.md) 
  - [ ] [Gmail](docs/GMAIL.md)  

## 🚧 Maintenance

This program is still in its development stages. 
Hermes is stable and available for production and deployment. This project can be improved - ideas for significant refactors are being considered.

A GitHub Project is open with all the tasks to be carried out to make Hermes even more incredible!

For now, I'm focusing on bugs and security maintenance, and I re-read and approve all contributions.

## ⬆️ Upgrade

Hermes may require updates. To do so, run the `upgrade.sh` script.

```shell
./upgrade.sh
```

## 📝 License

**Commercial exploitation is strictly prohibited, however, internal use is authorized.**

Released under "Non-Profit Open Software License 3.0 (NPOSL-3.0)"

## Contributor(s) :

  - Ahmed TAHRI @Ousret, Developer and maintainer
  - Didier JEAN ROBERT @SadarSSI, Initial conception and feature brainstormer
  - Denis GUILLOTEAU @Dsniss, Initial conception, tester, validator.