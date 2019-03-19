FROM python:3

ADD . /home

WORKDIR /home

RUN pip install -r requirements.txt
RUN apt-get update && \
    apt-get install --yes openjdk-8-jre
RUN curl -o /tmp/out_teutostack_teutostack-leistungsverzeichnis-2019-01-28.pdf https://teutostack.de/wp-content/uploads/2019/01/out_teutostack_teutostack-leistungsverzeichnis-2019-01-28.pdf
RUN curl -o /tmp/open-telekom-cloud-leistungsbeschreibung.pdf https://open-telekom-cloud.com/resource/blob/data/160462/0662e233681ca01247fef6a386c62d81/open-telekom-cloud-leistungsbeschreibung.pdf

ENTRYPOINT /bin/bash
