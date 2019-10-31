# Use an official Python runtime as an image
FROM python:3.8

MAINTAINER Ahmed TAHRI "ahmed.tahri@sii.fr"

RUN apt-get update
RUN apt-get -y install curl gnupg
RUN curl -sL https://deb.nodesource.com/setup_11.x  | bash -
RUN apt-get -y install nodejs
RUN npm install yarn -g

EXPOSE 5000

WORKDIR /

RUN python setup.py install --user

RUN yarn install
RUN yarn build

CMD python wsgi.py