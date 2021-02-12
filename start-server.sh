#!/usr/bin/env bash
# start-server.sh
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
    (cd converter_web_app; python manage.py createsuperuser --no-input)
fi
(cd converter_web_app; gunicorn converter_web_app.wsgi --user www-data --bind 0.0.0.0:8010 --workers=1 --threads=2 --worker-class=gthread --timeout 150 --log-level debug) &
nginx -g "daemon off;"