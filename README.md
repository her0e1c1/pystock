
# pystock

A commad line tool for stock

## install
> pip install stock

## server
> heroku run --app APP_NAME python -m stock setup

## how to set japanese companies data
1. access http://www.jpx.co.jp/markets/statistics-equities/misc/01.html
2. 市場第一部 （内国株） 's excel
3. read the excel file

       import pandas as pd
       xls = pd.ExcelFile("./first-d-j.xls")
       print(xls.sheet_names)  # check sheet name
       df = xls.parse("Sheet1")

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
