#!/usr/bin/bash
export FLASK_APP=app.py
git pull
cd hermes_ui || exit
flask db upgrade
yarn build
