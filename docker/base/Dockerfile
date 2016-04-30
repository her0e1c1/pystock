FROM python:3.5

# We don't need this for development
# RUN apt-get install -y postgresql-9.4

ADD requirements.txt ./

RUN pip install -r requirements.txt

ENV LANG en_US.UTF-8
