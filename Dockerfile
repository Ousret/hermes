# Use an official Python runtime as an image
FROM python:3.8

MAINTAINER Ahmed TAHRI "ahmed.tahri@sii.fr"

RUN apt-get update
RUN apt-get -y install curl gnupg wget git
RUN curl -sL https://deb.nodesource.com/setup_11.x  | bash -
RUN apt-get -y install nodejs
RUN npm install yarn -g

RUN pip install certifi pyopenssl

EXPOSE 5000

COPY ./setup.py /app/setup.py
COPY ./configuration.yml /app/configuration.yml
COPY ./upgrade.sh /app/upgrade.sh
COPY ./wsgi.py /app/wsgi.py

COPY ./hermes/ /app/hermes/
COPY ./hermes_ui/ /app/hermes_ui/
COPY ./msg_parser/ /app/msg_parser/

WORKDIR /app

RUN python setup.py install

WORKDIR /app/hermes_ui

RUN yarn install
RUN yarn build

WORKDIR /app

CMD python wsgi.py
