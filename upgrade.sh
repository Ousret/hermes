#!/usr/bin/env bash
export FLASK_APP=app.py
cd ./gie_interoperabilite_ui/
flask db upgrade
