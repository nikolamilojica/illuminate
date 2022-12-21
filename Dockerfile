FROM python:3.9-slim

COPY dist/*.whl /tmp/
RUN apt-get update \
    && apt-get -y install gcc libpq-dev \
    && pip3 install bs4 /tmp/*.whl \
    && rm -f /tmp/*.whl

WORKDIR /root/illuminate
