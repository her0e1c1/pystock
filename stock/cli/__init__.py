# coding: utf-8

from .main import cli
from . import (  # NOQA
    db,
    calc,
    config,
    predict,
    quandl,
    server,
    show,
)


if __name__ == "__main__":
    cli()
