# coding: utf-8
import click
import requests

from .main import cli

from stock import models
from stock import util
from stock import constant as C


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


@quandl.command(help="TODO")
@click.argument('database_code', default="")  # avoid key missing error if default=None
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


@quandl.command(name="line", help="Store price")
@click.argument('quandl_code', default="NIKKEI/INDEX")
def quandl_line(quandl_code):
    session = models.Session()
    data = session.query(models.Price).filter_by(quandl_code=quandl_code).first()
    if data:
        click.secho("Already imported")
        return
    mydata = quandl.get(quandl_code)
    mydata = mydata.rename(columns=C.MAP_PRICE_COLUMNS)
    # series = getattr(df, price_type.name)
    mydata = mydata[pd.isnull(mydata.close) == False]  # NOQA
    mydata['quandl_code'] = quandl_code
    mydata.to_sql("price", models.engine, if_exists='append')
