FROM python:3.5

WORKDIR /workdir

RUN apt-get update -y
RUN apt-get install -y sqlite3
RUN apt-get install -y grsync

# We don't need this for development
# RUN apt-get install -y postgresql-9.4

ADD requirements.txt ./

RUN pip install -r requirements.txt

# for dev
RUN pip install ipython pytest
RUN easy_install pdbpp

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

ADD .pdbrc.py ~/
