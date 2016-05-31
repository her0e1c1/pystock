
# pystock

A commad line tool for stock

## install

    git clone ssh://git@github.com/her0e1c1/s
    pyvenv venv34
	source venv34/bin/activate
	pip install -r requirements.txt

setup heroku

    heroku run --app APP_NAME python -m stock setup

serve

    gunicorn stock.server.main:app

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

### autoreload
```
%load_ext autoreload
%autoreload 2
%matplotlib inline
from stock.service.table import *
```

### Esc mode
j
k
Enter
d
