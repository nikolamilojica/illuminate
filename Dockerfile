FROM python:3.12-slim

RUN addgroup --system nonroot \
    && adduser --system --ingroup nonroot illuminate

COPY dist/*.whl /tmp/

RUN apt-get update \
    && apt-get -y --no-install-recommends install \
        build-essential \
        gcc \
        libpq-dev \
    && pip3 install bs4 /tmp/*.whl \
    && apt-get purge -y --auto-remove gcc build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/*.whl

USER illuminate
WORKDIR /home/illuminate
