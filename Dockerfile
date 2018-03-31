FROM python:3.6

RUN apt-get update -y && apt-get install -y sqlite3

ADD requirements.txt ./

RUN pip install -r requirements.txt
