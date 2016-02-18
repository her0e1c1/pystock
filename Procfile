web: gunicorn stock.server.main:app --log-file -

# you need to set cron ready
# heroku ps:scale clock=1
clock: python clock.py