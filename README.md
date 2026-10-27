# Simple Offline Captive Portal

Simple Offline Captive Portal description

## Quick Start

Run the application:

    make run

And open it in the browser at [http://127.0.0.1:5000/](http://127.0.0.1:5000/)


## Prerequisites

This is built to be used with Python 3. Update `Makefile` to switch to Python 2 if needed.

Some Flask dependencies are compiled during installation, so `gcc` and Python header files need to be present.
For example, on Ubuntu:

    apt install build-essential python3-dev


## Development environment and release process

 - create virtualenv with Flask and Simple Offline Captive Portal installed into it (latter is installed in
   [develop mode](http://setuptools.readthedocs.io/en/latest/setuptools.html#development-mode) which allows
   modifying source code directly without a need to re-install the app): `make venv`

 - run development server in debug mode: `make run`; Flask will restart if source code is modified

 - run tests: `make test` (see also: [Testing Flask Applications](http://flask.pocoo.org/docs/0.12/testing/))

 - create source distribution: `make sdist` (will run tests first)

 - to remove virtualenv and built distributions: `make clean`

 - to add more python dependencies: add to `install_requires` in `setup.py`

 - to modify configuration in development environment: edit file `settings.cfg`; this is a local configuration file
   and it is *ignored* by Git - make sure to put a proper configuration file to a production environment when
   deploying


## Deployment

If you are interested in an out-of-the-box deployment automation, check out accompanying
[`cookiecutter-flask-ansible`](https://github.com/candidtim/cookiecutter-flask-ansible).

Or, check out [Deploying with Fabric](http://flask.pocoo.org/docs/0.12/patterns/fabric/#fabric-deployment) on one of the
possible ways to automate the deployment.

In either case, generally the idea is to build a package (`make sdist`), deliver it to a server (`scp ...`),
install it (`pip install captiveportal.tar.gz`), ensure that configuration file exists and
`CAPTIVEPORTAL_SETTINGS` environment variable points to it, ensure that user has access to the
working directory to create and write log files in it, and finally run a
[WSGI container](http://flask.pocoo.org/docs/0.12/deploying/wsgi-standalone/) with the application.
And, most likely, it will also run behind a
[reverse proxy](http://flask.pocoo.org/docs/0.12/deploying/wsgi-standalone/#proxy-setups).

## Page language

The "Connected to ... Wifi" page is shown in the phone's language when the box has it (`captiveportal/translations.py`): the first language in the request's `Accept-Language` header that the box has content in (exact code, then the same base language: `es-MX` -> `es`, `zh-TW` -> `zh`), otherwise the box's default language from `languages.json`, otherwise English. Right-to-left languages are laid out right to left.

The text comes from the box's interface translation files (`TRANSLATIONS_DIR`, default `/usr/local/connectbox/translations/<code>.json`, shipped by connectbox-pi and managed by mmiLoader with the menu strings) under the `PORTAL_*` keys. Each entry records the English it was translated from; an entry whose English no longer matches `translations.ENGLISH` is not used, and a missing string is shown in English. `PORTAL_USE_AS_IS` must be Android's own wording of its "Use this network as is" menu item. The box's languages come from `LANGUAGES_JSON` (default `/var/www/enhanced/content/www/assets/content/languages.json`); when it cannot be read, every language with a translation file counts. Keep `ENGLISH` in step with the `PORTAL_*` strings in mmiLoader's `EXTRA_INTERFACE_STRINGS`.

The old-phone handling in `views.py` (iOS 9 / Android 4-5 era devices) is intentional; do not remove it.
