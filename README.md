
# pystock

A commad line tool for stock

## install

> pip install stock

## heroku server

> heroku run --app APP_NAME python -m stock setup

Need to set `JUPYTER_NOTEBOOK_PASSWORD` or need to check stdout to get token

> heroku config:set JUPYTER_NOTEBOOK_PASSWORD=<your_passwd> -a f1nance
> heroku config:set JUPYTER_NOTEBOOK_PASSWORD_DISABLED=DangerZone! -a f1nance

## Jupyter

```
openssl req -x509 -nodes -days 365 -newkey rsa:1024 -keyout mykey.key -out mycert.pem
jupyter notebook --cert=mycert.pem --key=mykey.key --ip=0.0.0.0
```

## Docker

> docker build . -t pystock
