from setuptools import setup

setup(
    name='hermes',
    version='1.0.15',
    author='Ahmed TAHRI',
    author_email='ahmed.tahri@cloudnursery.dev',
    description='Automates programmables à réaction aux échanges électroniques reçus depuis une boîte IMAP4',
    license='NPOSL-3.0',
    packages=['hermes', 'hermes_ui'],
    install_requires=[
        'Flask==1.1.*',
        'requests_html',
        'python-slugify',
        'requests>=2.23,<3.0',
        'prettytable',
        'imapclient>=2.1.0,<3.0',
        'zeep>=3.4,<4.0',
        'tqdm',
        'emails>=0.6.1,<1.0',
        'flask_security',
        'flask_admin',
        'flask_sqlalchemy==2.4.*',
        'flask_migrate',
        'pyyaml',
        'marshmallow>=3.5.2,<4.0',
        'flask_marshmallow>=0.12,<1.0',
        'marshmallow-sqlalchemy>=0.23,<1.0',
        'python-dateutil',
        'jinja2',
        'flask-emails',
        'ruamel.std.zipfile',
        'ics==0.5',
        'olefile>=0.46,<1.0',
        'html5lib',
        'pandas',
        'flask_babel==1.0.*',
        'records',
        'flask_babel',
        'unidecode',
        'pandas',
        'records',
        'marshmallow-oneofschema>=2.0.1,<2.1',
        'loguru',
        'Flask-Webpack>=0.1,<1.0',
        'mysql-connector-python',
        'werkzeug==1.0.*',
        'sqlalchemy==1.3.*',
        'flask_webpackext==1.0.*',
        'pyopenssl>=19.1.0',
        'msg_parser>=1.1.0',
        'wtforms',
        'dateparser',
        'kiss-headers>=2.0.4,<3.0',
        'email_validator>=1.1.0'
    ],
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
    message_extractors={
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
