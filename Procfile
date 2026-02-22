release: python manage.py collectstatic --noinput --clear
web: gunicorn qcorn.wsgi:application --bind 0.0.0.0:$PORT --workers=3
