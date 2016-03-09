# need docker_ prefix
from docker_pystock_base

# 外にあるsetup.pyを見にいく必要がでてきてしまう.のでrepo dirしておく?
# ADD repo
# そうすると、開発中のrepoの更新ができない

# "1つのDockerfile にCMD、ENTRYPOINT は1度のみ" らしい

# run CMDの上書きみたい
# ENTRYPOINT ["ls", "-l"]
# CMD ["-a"]

RUN python3.4 /pystock/setup.py develop
