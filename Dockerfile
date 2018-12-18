FROM python:2

WORKDIR /wd

COPY . /tmp/passmancli

RUN pip install --no-cache-dir /tmp/passmancli

RUN passman --version

ENTRYPOINT ["passman", "--config", "/config/default"]