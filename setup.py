from setuptools import setup

setup(
    name='hermes',
    version='1.0.12',
    author='Ahmed TAHRI',
    author_email='ahmed.tahri@cloudnursery.dev',
    description='Automates programmables à réaction aux échanges électroniques reçus depuis une boîte IMAP4',
    license='NPOSL-3.0',
    packages=['hermes', 'hermes_ui'],
    install_requires=['Flask>=1.0', 'requests_html', 'python-slugify', 'requests',
                      'prettytable', 'imapclient', 'zeep', 'tqdm', 'emails>=0.6.1',
                      'flask_security', 'flask_admin', 'flask_sqlalchemy', 'flask_migrate', 'pyyaml',
                      'marshmallow>=2.1', 'flask_marshmallow', 'marshmallow-sqlalchemy', 'python-dateutil', 'jinja2',
                      'flask-emails', 'ruamel.std.zipfile', 'ics==0.5', 'olefile', 'html5lib', 'pandas', 'flask_babel',
                      'records', 'flask_babel', 'unidecode', 'pandas', 'records', 'marshmallow-oneofschema', 'loguru',
                      'Flask-Webpack', 'mysql-connector-python', 'werkzeug', 'sqlalchemy', 'flask_webpackext',
                      'pyopenssl', 'msg_parser>=1.1.0', 'wtforms', 'dateparser', 'kiss-headers>=2.0.4'],
    tests_require=[],
    keywords=[],
    dependency_links=[
        'git+https://github.com/Ousret/python-emails.git#egg=emails'
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
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    message_extractors = {
        'hermes': [
            ('**.py', 'python', None),
            ('templates/**.html', 'jinja2', None),
            ('assets/**', 'ignore', None),
            ('static/**', 'ignore', None)
        ],
        'hermes_ui': [
            ('**.py', 'python', None),
            ('templates/**.html', 'jinja2', None),
            ('assets/**', 'ignore', None),
            ('static/**', 'ignore', None)
        ],
    },

)
