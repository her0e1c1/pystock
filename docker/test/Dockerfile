from docker_base

# update this image
# touch Dockerfile && docker-compose build
ADD ./Dockerfile /tmp
RUN git clone --depth 1 https://github.com/her0e1c1/pystock.git
RUN python3.4 ./pystock/setup.py develop
