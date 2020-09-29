#!/usr/bin/bash
export FLASK_APP=app.py
git fetch --tags

latestTag=$(git describe --tags `git rev-list --tags --max-count=1`)
git checkout $latestTag

if type "python3" > /dev/null; then
  python3 setup.py install --user
else
  python setup.py install --user
fi

cd hermes_ui || exit
flask db upgrade
yarn build
