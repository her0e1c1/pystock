# coding: utf-8
import pandas as pd
import click
import requests

from .main import cli

from stock import models
from stock import util
from stock import constant as C


# 基本的にSTDOUTするので、共通部分は関数にしておくべき(interfaceを定義)

@cli.group()
def quandl():
    pass


@quandl.command(name="db", help="Store database code")
@click.option("-f", "--force", type=bool, default=False, is_flag=True)
@click.option("--url", default="https://www.quandl.com/api/v3/databases")
def database(force, url):
    click.secho("Try to store code from %s" % url, fg="blue")
    session = models.Session()
    if force:
        click.secho("Delete QuandlDatabase", fg="red")
        session.query(models.QuandlDatabase).delete()
        session.commit()
    dbs = session.query(models.QuandlDatabase).all()
    if not dbs:
        r1 = requests.get(url)
        if not r1.ok:
            msg = r1.json()['quandl_error']['message']
            click.secho("ERRRO: %s" % msg, fg="red")
            return
        dbs = [models.QuandlDatabase(code=j['database_code'])
               for j in r1.json()['databases']]
        session.add_all(dbs)
        session.commit()
    else:
        click.secho("Already stored", fg="blue")

    click.echo(", ".join(sorted([db.code for db in dbs])))


@quandl.command(name="code", help="Store and show quandl code")
@click.argument('database_code')
def code(database_code):
    session = models.Session()
    codes = session.query(models.QuandlCode).filter_by(database_code=database_code).all()
    if not codes:
        URL = "https://www.quandl.com/api/v3/databases/{}/codes.json".format(database_code)
        click.secho("GET %s" % URL, fg="blud")
        r = requests.get(URL)
        if not r.ok:
            return click.secho(r.content, fg="red")
        # row == [TSE/1111, "name"]
        session.add_all(util.read_csv_zip(
            lambda row: models.QuandlCode(code=row[0], database_code=database_code),
            content=r.content,
        ))
        session.commit()
    click.secho(", ".join(c.quandl_code for c in codes))


@quandl.command(name="line", help="Store price")
@click.argument('quandl_code', default="NIKKEI/INDEX")
def quandl_line(quandl_code):
    import quandl
    session = models.Session()
    data = session.query(models.Price).filter_by(quandl_code=quandl_code).first()
    if data:
        click.secho("Already imported")
        return
    mydata = quandl.get(quandl_code)
    mydata = mydata.rename(columns=C.MAP_PRICE_COLUMNS)
    mydata = mydata[pd.isnull(mydata.close) == False]  # NOQA
    mydata['quandl_code'] = quandl_code
    mydata.to_sql("price", models.engine, if_exists='append')
    click.secho("%s Imported" % quandl_code, fg="green")
