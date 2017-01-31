# coding: utf-8
import json
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
@click.option("--queue", envvar="RABBITMQ_QUEUE", default="queue")
@click.option("--queue-back", envvar="RABBITMQ_QUEUE_BACK", default="queue_back")
@click.option("-d", "--debug", default=False, is_flag=True)
def rabbitmq(host, queue, queue_back, debug):
    from stock import query
    from stock.cli import quandl
    modules = {"query": query, "quandl": quandl}

    def callback(ch, method, properties, body):
        ch.basic_ack(delivery_tag=method.delivery_tag)
        click.secho("RECEIVERS: %s" % body, fg="green")

        try:
            payload = json.loads(body.decode())
            m = payload.get("module", "query")
            module = modules[m]
            f = getattr(module, payload.get("method", "get"))
            kwargs = payload.get("kwargs", {})
            result = f(**kwargs)
        except Exception as e:
            click.secho("BAD BODY: %s" % body, fg="red")
            click.secho(str(e), fg="red")
        else:
            if hasattr(result, "to_json"):
                result = result.to_json()
            else:
                result = str(result)
            if debug:
                click.secho("RESULT: %s" % result)
            try:
                channel.basic_publish('', queue_back, result)
            except Exception as e:
                click.secho("BAD RESULT: %s" % result, fg="red")
                click.secho(str(e), fg="red")

    def listen(channel):
        channel.queue_declare(queue=queue, durable=False)  # no_ack=False
        channel.queue_declare(queue=queue_back)
        # channel.basic_qos(prefetch_count=1)
        channel.basic_consume(callback, queue=queue)
        click.secho("START CONSUMING ...", fg="green")
        channel.start_consuming()

    click.secho("RABBITMQ CLIENT: '{queue}' and '{queue_back}' to '{host}'".format(**locals()), fg="green")
    params = pika.ConnectionParameters(host=host)
    connection = pika.BlockingConnection(params)
    while True:
        try:
            channel = connection.channel()
            listen(channel)
        except Exception as e:
            click.secho(str(e), fg="red")
            channel.close()
