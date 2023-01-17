.. mailinglist documentation master file, created by
   sphinx-quickstart on Sun Jan 15 15:15:26 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to mailinglist's documentation!
=======================================
Project LAUNCH
==================

* pwd
* python -m venv venv
* venv/Scripts/activate
* pip install --no-cache-dir -r requirements.txt
* python manage.py runserver
* celery -A mailinglist worker -l info --pool=solo
* celery -A mailinglist beat -l INFO

########################
Acomplished EXTRA Tasks:
########################

* 1.Code Testing
* 2.GitLab CI
* 3.Docker-Compose
* 5.Swagger UI
* 6.Admin Web UI
* 7.Oauth2 autorization
* 8.Send statistics to email
* 11.Time interval for mailinglist


.. toctree::
   :maxdepth: 2

   modules/mail_api.rst
   modules/mail_api.tests.rst
   modules/mailinglist.rst
   modules/manage.rst
   modules/modules.rst
