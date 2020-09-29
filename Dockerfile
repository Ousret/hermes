# Download base image ubuntu 20.04
FROM ubuntu:20.04

# Use an official Python runtime as an image
FROM python:3.8

MAINTAINER Ahmed TAHRI "ahmed.tahri@cloudnursery.dev"

# Lets get latest list of packages
RUN apt-get update

# Disable Prompt During Packages Installation
ARG DEBIAN_FRONTEND=noninteractive

# Update  all packages to latest version before installing additional packages
RUN apt-get upgrade -y

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

RUN git clone https://github.com/Ousret/hermes.git .

COPY ./configuration.yml /app/configuration.yml

RUN pip install mysqlclient

RUN python setup.py install

WORKDIR /app/hermes_ui

RUN yarn install
RUN yarn build

WORKDIR /app

CMD python wsgi.py
