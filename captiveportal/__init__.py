import os
from flask import Flask
from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__)
app.config.from_object('captiveportal.default_settings')
app.wsgi_app = ProxyFix(app.wsgi_app)

import captiveportal.views

@app.errorhandler(404)
def default_view(_):
    """Handle all URLs and send them to the captive portal welcome page"""
    return captiveportal.views.show_connected()

