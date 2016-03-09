# 一度実行した既存imageに対して実行したコマンドは、キャッシュされてる
FROM centos

RUN yum update -y && yum install -y epel-release
RUN yum install -y \
    gcc \
    gcc-c++ \
    make \
    postgresql \
    postgresql-devel \
    git \
    python-devel \
    python-setuptools \
    python34 \
    python34-devel \
    python34-setuptools \

# # python-pip \

USER docker

WORKDIR /home/docker

# WARN: need to fix import
# docker build -t base -f ./path/to/Dockerfile .
ADD requirements.txt ./

RUN easy_install-3.4 pip && pip3 install -r requirements.txt

ENV LANG en_US.UTF-8
