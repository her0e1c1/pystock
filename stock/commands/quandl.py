# coding: utf-8
import click
import requests

from .main import cli

from stock import models 
from stock import util


@cli.group()
def quandl():
    pass


@quandl.command(name="db")
@click.option("-f", "--force", type=bool)
@click.option("--url", default="https://www.quandl.com/api/v3/databases")
def database(force, url):
    session = models.Session()
    dbs = session.query(models.QuandlDatabase).all()
    if not dbs:
        r1 = requests.get(url)
        if not r1.ok:
            print(r1.json()['quandl_error']['message'])
            return
        dbs = [models.QuandlDatabase(code=j['database_code'])
               for j in r1.json()['databases']]
        session.add_all(dbs)
        session.commit()
    for db in dbs:
        click.echo(db)


@quandl.command()
@click.argument('database_code', default="")
@click.argument('quandl_code', default="")
@click.option("--no-cache", type=bool)
@click.option("-U", "--update", type=bool)
def code(database_code, quandl_code, no_cache, update):
    session = models.Session()
    if not database_code:
        database.callback(*database.params)
    else:
        if quandl_code:
            quandl_code = "{database_code}/{quandl_code}".format(**locals())
            from stock.service.table import s
            ret = s(quandl_code=quandl_code)
            print(ret)
            return
        db = session.query(models.QuandlDatabase).filter_by(code=database_code).one()
        codes = session.query(models.QuandlCode).filter_by(database_id=db.id).all()
        if not codes:
            URL = "https://www.quandl.com/api/v3/databases/{}/codes.json".format(database_code)
            r = requests.get(URL)
            # row == [TSE/1111, "name"]
            session.add_all(util.read_csv_zip(
                f=lambda row: models.QuandlCode(code=row[0], database=db),
                content=r.content,
            ))
            session.commit()
        for c in codes:
            print(c.quandl_code)


@quandl.command(name="line")
@click.argument('quandl_code', default="")
def quandl_line(quandl_code):
    from stock.service.table import get_from_quandl
    df = get_from_quandl(quandl_code)
