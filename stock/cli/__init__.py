# coding: utf-8

from .main import cli
from . import (  # NOQA
    db,
    quandl,
    server,
)


if __name__ == "__main__":
    cli()
