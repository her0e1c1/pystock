FROM python:3.4

RUN apt-get install -y \
    postgresql

USER docker

WORKDIR /home/docker

ADD requirements.txt ./

RUN easy_install-3.4 pip && pip3 install -r requirements.txt

ENV LANG en_US.UTF-8
