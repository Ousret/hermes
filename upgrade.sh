#!/usr/bin/bash
export FLASK_APP=app.py
git fetch --tags

latestTag=$(git describe --tags `git rev-list --tags --max-count=1`)
git checkout $latestTag

cd hermes_ui || exit
flask db upgrade
yarn build
