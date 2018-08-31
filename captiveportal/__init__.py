import os
from flask import Flask
from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__)
app.config.from_object('captiveportal.default_settings')
#app.config.from_envvar('CAPTIVEPORTAL_SETTINGS')

if not app.debug:
    import logging
    from logging.handlers import TimedRotatingFileHandler
    # https://docs.python.org/3.6/library/logging.handlers.html#timedrotatingfilehandler
    file_handler = TimedRotatingFileHandler(os.path.join(app.config['LOG_DIR'], 'captiveportal.log'), 'midnight')
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(logging.Formatter('<%(asctime)s> <%(levelname)s> %(message)s'))
    app.logger.addHandler(file_handler)

import captiveportal.views

@app.errorhandler(404)
def default_view(_):
    """Handle all URLs and send them to the captive portal welcome page"""
    return captiveportal.views.show_connected()

