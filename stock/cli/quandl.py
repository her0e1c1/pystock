# coding: utf-8
import pandas as pd
import quandl
import click
import requests

from .main import cli, AliasedGroup

from stock import models
from stock import util
from stock import config as C


quandl.ApiConfig.api_key = C.QUANDL_CODE_API_KEY


@cli.group(cls=AliasedGroup, name="quandl")
@click.option("-k", "--key")
def c(key):
    if key:
        quandl.ApiConfig.api_key = key


@c.command(name="db", help="Store database codes")
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
    session.close()
    db_codes = ", ".join(sorted([db.code for db in dbs]))
    click.echo(db_codes)
    return db_codes


@c.command(name="code", help="Store and show quandl codes of [database_code]")
@click.argument('database_code')
def quandl_codes(database_code):
    session = models.Session()
    codes = session.query(models.QuandlCode).filter_by(database_code=database_code).all()
    if not codes:
        URL = "https://www.quandl.com/api/v3/databases/{}/codes.json".format(database_code)
        click.secho("GET %s" % URL, fg="blue")
        r = requests.get(URL)
        if not r.ok:
            return click.secho(r.content, fg="red")
        # db = models.QuandlDatabase(code=database_code)
        # session.add(db)
        # row == [TSE/1111, "name"]
        session.add_all(util.read_csv_zip(
            lambda row: models.QuandlCode(code=row[0], database_code=database_code),
            content=r.content,
        ))
        session.commit()
    session.close()
    quandl_codes = [c.quandl_code for c in codes]
    click.secho(", ".join(quandl_codes))
    return quandl_codes


@c.command(name="get", help="Store prices by calling quandl API")
@click.argument('quandl_code', default="NIKKEI/INDEX")
@click.option("-l", "--limit", type=int, default=None, help="For heroku db limitation")
def get_by_code(quandl_code, limit):
    session = models.Session()
    data = session.query(models.Price).filter_by(quandl_code=quandl_code).first()
    if data:
        click.secho("Already imported: %s" % quandl_code)
        session.close()
        return
    mydata = quandl.get(quandl_code)
    mydata = mydata.rename(columns=C.MAP_PRICE_COLUMNS)
    mydata = mydata.reindex(mydata.index.rename("date"))  # "TSE/TOPIX" returns "Year" somehow
    mydata = mydata[pd.isnull(mydata.close) == False]  # NOQA
    mydata['quandl_code'] = quandl_code
    if limit:
        mydata = mydata.reindex(reversed(mydata.index))[:limit]
    mydata.to_sql("price", models.engine, if_exists='append')
    click.secho("Imported: %s" % quandl_code)
    session.close()


@c.command(name="import_codes", help="import")
@click.argument('database_code')
@click.option("-l", "--limit", type=int, default=10)
def import_codes(database_code, limit):
    database_code = database_code.upper()

    session = models.Session()
    codes = session.query(models.Price.quandl_code).distinct().all()
    allcodes = session.query(models.QuandlCode).filter_by(database_code=database_code).filter(
        models.QuandlCode.code.notin_([c[0] for c in codes])
    ).all()
    session.close()
    codes = [c.code for c in allcodes][:limit]
    click.secho(",".join(codes))
    for c in codes:
        get_by_code.callback(c)

    return codes
