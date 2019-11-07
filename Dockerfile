# Use an official Python runtime as an image
FROM python:3.8

MAINTAINER Ahmed TAHRI "ahmed.tahri@sii.fr"

RUN apt-get update
RUN apt-get -y install curl gnupg
RUN curl -sL https://deb.nodesource.com/setup_11.x  | bash -
RUN apt-get -y install nodejs
RUN npm install yarn -g

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

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /app/wait
RUN chmod +x /app/wait

CMD wait

CMD python wsgi.py