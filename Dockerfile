# Use an official Python runtime as an image
FROM python:3.8

MAINTAINER Ahmed TAHRI "ahmed.tahri@sii.fr"

RUN apt-get update

RUN apt-get remove -y openssl
RUN apt-get install -y build-essential cmake zlib1g-dev libcppunit-dev git subversion wget

RUN wget https://www.openssl.org/source/openssl-1.0.2g.tar.gz -O - | tar -xz
WORKDIR /openssl-1.0.2g
RUN ./config --prefix=/usr/local/openssl --openssldir=/usr/local/openssl && make && make install

RUN apt-get -y install curl gnupg wget
RUN curl -sL https://deb.nodesource.com/setup_11.x  | bash -
RUN apt-get -y install nodejs npm
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

RUN pip install certifi pyopenssl

RUN python setup.py install

WORKDIR /app/hermes_ui

RUN yarn install
RUN yarn build

WORKDIR /app

CMD python wsgi.py
