import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

# -------------------------------------------------------------------------
# Flask application factory.
# ProxyFix is required because the app runs behind nginx which terminates
# TLS and forwards requests.  Without it, request.remote_addr would always
# be 127.0.0.1 (the nginx upstream address) and per-client session tracking
# in views.py would not work correctly.
# -------------------------------------------------------------------------
app = Flask(__name__)
app.config.from_object('captiveportal.default_settings')
app.wsgi_app = ProxyFix(app.wsgi_app)

import captiveportal.views

@app.errorhandler(404)
def default_view(_):
    """Catch-all 404 handler — redirects every unknown URL to the welcome page.

    The captive portal relies on this behaviour: when a device probes an
    arbitrary URL (e.g. http://example.com/test) and gets the ConnectBox
    welcome page instead of a 404, it knows it is behind a captive portal
    and raises the sign-in sheet.
    """
    return captiveportal.views.show_connected()

