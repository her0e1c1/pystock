# coding: utf-8
import logging

import pika
import click

from stock import config as C
from .main import cli


@click.option("--port", default=C.PORT, type=int)
@click.option("--host", default=C.HOST)
@click.option("-l", "--log-level", default=C.LOG_LEVEL, type=int)
@click.option("--debug", default=(not C.DEBUG), is_flag=True)
@cli.command(help="Start server")
def serve(**kw):
    from stock.server import app
    msg = ", ".join(["%s = %s" % (k, v) for k, v in kw.items()])
    click.echo(msg)
    C.set(**kw)
    click.echo("DATABASE_URL: %s" % C.DATABASE_URL)
    logging.basicConfig(level=kw.pop("log_level"))
    app.run(**kw)


@cli.command(help="Start rabbitmq client")
@click.option("--host", envvar="RABBITMQ_HOST")
def rabbitmq(host):
    def callback(ch, method, properties, body):
        print("START TASK")
        import json
        from stock import cli
        j = json.loads(body.decode())
        main = getattr(cli, j["main"])
        sub = getattr(main, j["sub"])
        defaults = [p.default for p in sub.params]
        sub.callback(*defaults)
        # ret = sub.callback(*j["args"])
        ch.basic_ack(delivery_tag=method.delivery_tag)
        channel.basic_publish('', 'queue_back', "BUY")

    def listen(channel):
        channel.queue_declare(queue="queue", durable=True)  # no_ack=False
        channel.queue_declare(queue="queue_back")
        # channel.basic_qos(prefetch_count=1)
        channel.basic_consume(callback, queue='queue')
        click.secho("START CONSUMING ...", fg="blue")
        channel.start_consuming()

    params = pika.ConnectionParameters(host=host)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    while True:
        try:
            listen(channel)
        except Exception as e:
            click.secho(str(e), fg="red")
            channel.close()
