FROM python:3.4

RUN yum update -y && yum install -y epel-release
RUN yum install -y \
    gcc \
    gcc-c++ \
    make \
    postgresql \
    postgresql-devel \
    git

USER docker

WORKDIR /home/docker

ADD requirements.txt ./

RUN easy_install-3.4 pip && pip3 install -r requirements.txt

ENV LANG en_US.UTF-8
