FROM python:3.8

ADD . /home

WORKDIR /home

RUN pip3 install -r requirements.txt
RUN apt-get update && \
    apt-get install --yes openjdk-11-jre
RUN curl -o /tmp/open-telekom-cloud-leistungsbeschreibung.pdf https://open-telekom-cloud.com/resource/blob/data/160462/9772ae6e12c4299ce2fa6efe60a603af/open-telekom-cloud-leistungsbeschreibung.pdf

ENTRYPOINT /bin/bash
