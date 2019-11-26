#!/usr/bin/env python3
from hermes_ui.app import app
from ssl import SSLContext, PROTOCOL_TLS, CERT_REQUIRED

if __name__ == '__main__':

    context = None

    if app.config.get('HERMES_CERTIFICAT_TLS') and app.config.get('HERMES_CLE_PRIVEE_TLS'):
        context = SSLContext(PROTOCOL_TLS)

        context.verify_mode = CERT_REQUIRED
        context.load_cert_chain(app.config.get('HERMES_CERTIFICAT_TLS'), app.config.get('HERMES_CLE_PRIVEE_TLS'))

        if app.config.get('HERMES_CERTIFICAT_CA'):
            context.load_verify_locations(app.config.get('HERMES_CERTIFICAT_CA'))

    if context:
        context.set_ciphers("ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384")

    app.run(
        host='0.0.0.0',
        port=5000,
        threaded=True,
        ssl_context=context
    )
