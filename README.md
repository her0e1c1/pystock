
# pystock

A commad line tool for stock

## install

> pip install stock

## heroku server

> heroku run --app f1nance python -m stock init

## jupyter

```
openssl req -x509 -nodes -days 365 -newkey rsa:1024 -keyout mykey.key -out mycert.pem
jupyter notebook --cert=mycert.pem --key=mykey.key --ip=0.0.0.0
```
