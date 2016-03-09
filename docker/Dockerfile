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
# docker create -v `pwd`./pystock:/pystock --name pystock-repo centos
# busybox seems to be not updated even if host changes it
# docker create -v `pwd`./pystock:/pystock --name pystock-repo busybox
# check if the repo is mounted
# docker run --volumes-from pystock-repo centos ls /pystock
# run
# docker run -e DATABASE_URL="mysql+pymysql://root@192.168.99.100:3306/stock?charset=utf8" -p 8000:80 --rm --volumes-from pystock -it pystock-repo sh -c "/bin/python3.4 /pystock/setup.py develop && pystock setup && pystock serve --port 80 --host 0.0.0.0"

# mysql
# need -d (or you can't handle the mysql process)
# need setting port (or you can't access from outside)
# need one of env vars. MYSQL_ROOT_PASSWORD, MYSQL_ALLOW_EMPTY_PASSWORD and MYSQL_RANDOM_ROOT_PASSWORD
# docker run -v `pwd`/pystock/docker/mysql/conf.d:/etc/mysql/conf.d --name pystock-mysql -d -e MYSQL_ALLOW_EMPTY_PASSWORD="1" -e MYSQL_DATABASE=stock -p 3306:3306 mysql
