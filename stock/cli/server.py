import io
import json
import contextlib
import tornado

import quandl
import pika
import click

from .main import cli
from stock.server import websocket


@cli.command(help="Start rabbitmq client")
@click.option("--host", envvar="RABBITMQ_HOST")
@click.option("--queue", envvar="RABBITMQ_QUEUE", default="queue")
@click.option("--queue-back", envvar="RABBITMQ_QUEUE_BACK", default="queue_back")
@click.option("-d", "--debug", default=False, is_flag=True)
def rabbitmq(host, queue, queue_back, debug):

    def callback(ch, method, properties, body):
        def send_error(e):
            # TODO: error_queue
            channel.basic_publish('', queue_back, json.dumps({"error": "%s: %s" % (e, body)}))

        ch.basic_ack(delivery_tag=method.delivery_tag)
        if debug:
            click.secho("RECEIVERS: %s" % body, fg="green")
        try:
            payload = json.loads(body.decode())
            ref = payload.pop("ref", None)
            args = payload.pop("args", None)
        except Exception as e:
            if debug:
                click.secho("BAD BODY: %s" % body, fg="red")
                click.secho(str(e), fg="red")
            send_error(e)
            return

        out = io.StringIO()
        err = io.StringIO()
        r = None
        try:
            args2 = ["-k", quandl.ApiConfig.api_key] + args
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                r = cli.main(args2, standalone_mode=False)
        except SystemExit as e:
            if debug:
                click.secho("SystemExit: %s" % str(e), fg="red")
                click.secho("BAD BODY: %s" % body, fg="red")
                click.secho(str(e), fg="red")
            send_error(e)
            return
        except Exception as e:
            if debug:
                click.secho("BAD RESULT: %s" % str(e), fg="red")
                click.secho("BAD BODY: %s" % body, fg="red")
                click.secho(str(e), fg="red")
            send_error(e)
            return

        out = out.getvalue()
        err = err.getvalue()
        if debug:
            click.secho(out)
            click.secho(err, fg="red")

        def convert(result):
            import pandas as pd
            if isinstance(result, float) and pd.isnull(result):  # result is pd.np.nan
                return None
            else:
                return result

        result = {"result": convert(r), "ref": ref, "stdout": out, "stderr": err, "args": args}
        if debug:
            click.secho("RESULT: %s" % result)
        channel.basic_publish('', queue_back, json.dumps(result))

    def listen(channel):
        channel.queue_declare(queue=queue, durable=False)  # no_ack=False
        channel.queue_declare(queue=queue_back)
        # channel.basic_qos(prefetch_count=1)
        channel.basic_consume(callback, queue=queue)
        if debug:
            click.secho("START CONSUMING ...", fg="green")
        channel.start_consuming()

    click.secho("RABBITMQ CLIENT: '{queue}' and '{queue_back}' to '{host}'".format(**locals()), fg="green")
    if debug:
        click.secho("QUANDL_API_KEY: {}".format(quandl.ApiConfig.api_key), fg="green")
    params = pika.ConnectionParameters(host=host)
    connection = pika.BlockingConnection(params)
    while True:
        try:
            channel = connection.channel()
            listen(channel)
        except Exception as e:
            click.secho(str(e), fg="red")
            channel.close()


def make_app():
    return tornado.web.Application([(r"/", websocket.MainHandler)])


@cli.command(name="tornado", help="Start tornado server")
@click.option("--port", default="8080", envvar="TORNADO_PORT")
def start_tornado(port):
    click.secho(f"Start tornado at {port}")
    app = make_app()
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()
