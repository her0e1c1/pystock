from docker_base

# update this image
# touch Dockerfile && docker-compose build
ADD ./Dockerfile /tmp
RUN git clone --depth 1 https://github.com/her0e1c1/pystock.git

WORKDIR ./pystock
RUN python3.4 setup.py develop

FROM python:3.5

ADD requirements.txt ./

RUN pip install -r requirements.txt

ENV LANG en_US.UTF-8
