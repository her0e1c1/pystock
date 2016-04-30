FROM python:3.4

# We don't need this for development
# RUN apt-get install -y postgresql-9.4

USER docker

ADD requirements.txt ./

RUN easy_install-3.4 pip && pip3 install -r requirements.txt

ENV LANG en_US.UTF-8
