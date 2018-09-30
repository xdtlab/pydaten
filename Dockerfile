FROM python:3.5-alpine
RUN echo http://nl.alpinelinux.org/alpine/edge/testing >> /etc/apk/repositories
RUN apk add --no-cache build-base libffi-dev gmp-dev leveldb-dev
RUN mkdir /pydaten
WORKDIR /pydaten
COPY requirements.txt /pydaten
RUN pip install -r requirements.txt
COPY . /pydaten
RUN python setup.py install
ENTRYPOINT ["daten", "--path=/data"]
