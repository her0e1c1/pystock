
# pystock

A commad line tool for stock

## install

> pip install stock

## heroku server

> heroku run --app APP_NAME python -m stock setup

Need to set `JUPYTER_NOTEBOOK_PASSWORD`

## Jupyter

```
jupyter notebook --ip 0.0.0.0
% magic, ?, ??
openssl req -x509 -nodes -days 365 -newkey rsa:1024 -keyout mykey.key -out mycert.pem
jupyter notebook --cert=mycert.pem --key=mykey.key --ip=0.0.0.0
# check token
docker logs jupyter
```

## Docker
> docker build . -t pystock
