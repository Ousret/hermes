# Use an official Python runtime as an image
FROM python:3.8

MAINTAINER Ahmed TAHRI "ahmed.tahri@cloudnursery.dev"

RUN apt-get update
RUN apt-get -y install curl gnupg wget git
RUN curl -sL https://deb.nodesource.com/setup_11.x  | bash -
RUN apt-get -y install nodejs
RUN npm install yarn -g

RUN pip install certifi pyopenssl

EXPOSE 5000

WORKDIR /app

RUN git clone https://github.com/Ousret/hermes.git .

COPY ./configuration.yml /app/configuration.yml

RUN python setup.py install

WORKDIR /app/hermes_ui

RUN yarn install
RUN yarn build

WORKDIR /app

CMD python wsgi.py
