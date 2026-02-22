web: python manage.py migrate && python manage.py collectstatic --noinput --clear && gunicorn qcorn.wsgi:application --bind 0.0.0.0:$PORT --workers=3
