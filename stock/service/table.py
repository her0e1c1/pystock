# coding: utf-8
from stock import models


def create():
    models.Base.metadata.create_all()


def drop():
    models.Base.metadata.drop_all()
