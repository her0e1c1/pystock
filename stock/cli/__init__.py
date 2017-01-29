# coding: utf-8

from .main import cli
from . import (  # NOQA
    db,
    calc,
    config,
    predict,
    quandl,
    query,
    server,
)


if __name__ == "__main__":
    cli()
