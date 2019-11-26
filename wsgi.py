#!/usr/bin/env python3
from hermes_ui.app import app

if __name__ == '__main__':

    app.run(
        host='0.0.0.0',
        port=5000,
        threaded=True,
        ssl_context=(app.config.get('HERMES_CERTIFICAT_TLS'), app.config.get('HERMES_CLE_PRIVEE_TLS')) if app.config.get('HERMES_CERTIFICAT_TLS') and app.config.get('HERMES_CLE_PRIVEE_TLS') else None
    )
