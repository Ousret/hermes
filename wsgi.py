#!/usr/bin/env python3
from hermes_ui.app import app
from ssl import SSLContext, PROTOCOL_TLSv1_2, CERT_REQUIRED

if __name__ == '__main__':

    context = None

    if app.config.get('HERMES_CERTIFICAT_TLS') and app.config.get('HERMES_CLE_PRIVEE_TLS') and app.config.get('HERMES_CERTIFICAT_CA'):
        context = SSLContext(PROTOCOL_TLSv1_2)

        context.verify_mode = CERT_REQUIRED
        context.load_cert_chain(app.config.get('HERMES_CERTIFICAT_TLS'), app.config.get('HERMES_CLE_PRIVEE_TLS'))
        context.load_verify_locations(app.config.get('HERMES_CERTIFICAT_CA'))

    elif app.config.get('HERMES_CERTIFICAT_CA') and app.config.get('HERMES_CLE_PRIVEE_TLS'):
        context = SSLContext(PROTOCOL_TLSv1_2)

        context.verify_mode = CERT_REQUIRED
        context.load_cert_chain(app.config.get('HERMES_CERTIFICAT_CA'), app.config.get('HERMES_CLE_PRIVEE_TLS'))

    app.run(
        host='0.0.0.0',
        port=5000,
        threaded=True,
        ssl_context=context
    )
