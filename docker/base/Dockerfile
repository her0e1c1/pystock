FROM python:3.5

# RUN apt-get update -y
# RUN apt-get install -y grsync xinetd

# We don't need this for development
# RUN apt-get install -y postgresql-9.4

ADD requirements.txt ./

RUN pip install -r requirements.txt

# for dev
RUN pip install ipython pytest
RUN easy_install pdbpp

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
