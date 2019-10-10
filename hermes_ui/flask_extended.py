import os
import yaml

from flask import Flask as BaseFlask, Config as BaseConfig


class Config(BaseConfig):
    """Flask config enhanced with a `from_yaml` method."""

    def from_yaml(self, config_file):
        env = os.environ.get('FLASK_ENV', 'DEVELOPMENT')
        self['ENVIRONMENT'] = env.lower()

        with open(config_file) as f:
            c = yaml.load(f, Loader=yaml.FullLoader)

        c = c.get(env, c)

        for key in c.keys():
            if key.isupper():
                self[key] = c[key]


class Flask(BaseFlask):
    """Extended version of `Flask` that implements custom config class"""

    def make_config(self, instance_relative=False):
        root_path = self.root_path
        if instance_relative:
            root_path = self.instance_path
        return Config(root_path, self.default_config)
