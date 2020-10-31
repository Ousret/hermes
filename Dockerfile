# Use Ubuntu 20.04 as the base image
FROM ubuntu:20.04
# Use an official Python runtime as an image
FROM python:3.8

#Disable Prompt During Packages Installation
ARG DEBIAN_FRONTEND=noninteractive

LABEL MAINTAINER Ahmed TAHRI "ahmed.tahri@cloudnursery.dev"
LABEL version ="0.1"
LABEL description="This is a customer docker build for Hermes - https://github.com/Ousret/hermes"

# Update Current available packages
RUN apt-get update
# Upgrade all installed packages so most recent files are used.
RUN apt-get upgrade -y

# Lets install some mandatory requirements to grad the rest of the files needed
RUN apt-get -y install curl gnupg wget git
RUN curl -sL https://deb.nodesource.com/setup_14.x  | bash -
RUN apt-get -y install nodejs
RUN npm install yarn -g

RUN pip install certifi pyopenssl

EXPOSE 5000

RUN mkdir /python-emails

WORKDIR /python-emails

RUN git clone https://github.com/Ousret/python-emails.git .

RUN python setup.py install

WORKDIR /app

COPY ./hermes ./hermes
COPY ./hermes_ui ./hermes_ui
COPY setup.py ./setup.py
COPY setup.cfg ./setup.cfg
COPY wsgi.py ./wsgi.py

RUN mkdir invitations

COPY ./configuration.yml /app/configuration.yml

RUN pip install mysqlclient

RUN python setup.py install

WORKDIR /app/hermes_ui

RUN yarn install
RUN yarn build

WORKDIR /app

CMD python wsgi.py

# This will clean up any un-used apps and any other mess we might have made.
RUN rm -rf /var/lib/apt/lists/* && apt clean
