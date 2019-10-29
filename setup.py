from setuptools import setup

setup(
    name='hermes',
    version='2.0.0',
    author='GIE SESAM-VITALE',
    author_email='at.sii.TAHRI@sesam-vitale.fr',
    description='Permet la mise en oeuvre d\'une interopérabilité entre vos différents services ou fournisseurs',
    license='MIT',
    packages=['hermes', 'hermes_ui', 'msg_parser'],
    install_requires=['Flask', 'peewee', 'requests_html', 'python-slugify', 'chardet', 'jsonpickle', 'requests',
                      'prettytable', 'imapclient', 'zeep', 'tqdm', 'emails',
                      'flask_security', 'flask_admin', 'flask_sqlalchemy', 'flask_migrate', 'pyyaml',
                      'marshmallow', 'flask_marshmallow', 'marshmallow-sqlalchemy', 'python-dateutil', 'jinja2',
                      'flask-emails', 'ruamel.std.zipfile', 'ics', 'olefile', 'html5lib', 'pandas', 'flask_babel',
                      'records', 'flask_babel', 'unidecode', 'pandas', 'records', 'marshmallow-oneofschema', 'loguru',
                      'Flask-Webpack', 'mysql-connector', 'werkzeug', 'sqlalchemy'],
    dependency_links=[
        'git+https://github.com/C4ptainCrunch/ics.py.git@ebe80a0e77d93dd30d6182137d813e3176a2490c#egg=ics'
    ],
    tests_require=[''],
    keywords=[],
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
    ],
)
