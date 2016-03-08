# 一度実行した既存imageに対して実行したコマンドは、キャッシュされてる
FROM centos

# RUN yum update
RUN yum install -y \
    gcc \
    gcc-c++ \
    make \
    postgresql \
    postgresql-devel \
    git \    
    python-devel \
    python-setuptools \

# python-pip \

RUN yum install -y epel-release
RUN yum install -y \
    python34 \
    python34-devel \
    python34-setuptools \
 
USER docker
WORKDIR /home/docker

EXPOSE 80

# you can't use ssh agent forwarding
# RUN git clone git@github.com:her0e1c1/pystock.git
RUN git clone https://github.com/her0e1c1/pystock.git

WORKDIR ./pystock

RUN easy_install-3.4 pip
RUN pip3.4 install -r requirements.txt

ENV LANG en_US.UTF-8

# CMD gunicorn -b 0.0.0.0:80 stock.server.main:app --log-file -

# docker build -t pystock-server -f ./docker/Dockerfile .

# docker-machine ip
# docker -it -p 8000:80 IMAGE_NAME /bin/bash
# curl http://192.168.99.100:8000

# on host
# git clone git@github.com:her0e1c1/pystock.git
# docker create -v `pwd`./pystock:/pystock --name pystock
# docker run --volumes-from pystock centos ls /pystock
# docker run -p 8000:80 --rm --volumes-from pystock -it hog5 sh -c "/bin/python3.4 /pystock/setup.py develop && pystock serve --port 80 --host 0.0.0.0"
