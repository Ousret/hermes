from setuptools import setup

setup(
    name='hermes',
    version='2.1.0',
    author='Ahmed TAHRI',
    author_email='ahmed.tahri@cloudnursery.dev',
    description='Permet la mise en oeuvre d\'une interopérabilité entre vos différents services ou fournisseurs',
    license='MIT',
    packages=['hermes', 'hermes_ui'],
    install_requires=['Flask>=1.0', 'peewee', 'requests_html', 'python-slugify', 'chardet', 'jsonpickle', 'requests',
                      'prettytable', 'imapclient', 'zeep', 'tqdm', 'emails', 'mysqlclient',
                      'flask_security', 'flask_admin', 'flask_sqlalchemy', 'flask_migrate', 'pyyaml',
                      'marshmallow>=2.1', 'flask_marshmallow', 'marshmallow-sqlalchemy', 'python-dateutil', 'jinja2',
                      'flask-emails', 'ruamel.std.zipfile', 'ics>=0.5', 'olefile', 'html5lib', 'pandas', 'flask_babel',
                      'records', 'flask_babel', 'unidecode', 'pandas', 'records', 'marshmallow-oneofschema', 'loguru',
                      'Flask-Webpack', 'mysql-connector', 'werkzeug', 'sqlalchemy', 'flask_webpackext',
                      'pyopenssl', 'msg_parser'],
    tests_require=[],
    keywords=[],
    dependency_links=[
        'git+https://github.com/Ousret/msg_parser.git#egg=msg_parser'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'Environment :: MacOS X',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
