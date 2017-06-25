FROM python:3.6

RUN apt-get update -y
RUN apt-get install -y sqlite3
RUN apt-get install -y grsync

ADD requirements.txt ./

RUN pip install -r requirements.txt
