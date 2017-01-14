
# pystock

A commad line tool for stock

## install

	pip install stock

## server
setup heroku

    heroku run --app APP_NAME python -m stock setup

## how to set japanese companies data
1. access http://www.jpx.co.jp/markets/statistics-equities/misc/01.html
2. 市場第一部 （内国株） 's excel
3. read the excel file

       import pandas as pd
       xls = pd.ExcelFile("./first-d-j.xls")
       print(xls.sheet_names)  # check sheet name
       df = xls.parse("Sheet1")

## Jupyter

To launch the repl
    `Files -> New -> Python2`

you use Shift + Enter instead of Enter, which inputs a new line break

```
docker exec -it ps_jupyter_1 ipython
from stock.service.setup import *
```

## Docker
> docker build . -t pystock

## How to use
you can run click functions like this
> python -m pystock setup
