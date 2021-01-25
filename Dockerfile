FROM centos:latest
LABEL maintainer="Denis O. Pavlov pavlovdo@gmail.com"

ARG project

RUN dnf update -y && dnf install -y \ 
    cronie \
    epel-release \
    python36

COPY *.py requirements.txt /etc/zabbix/externalscripts/${project}/
WORKDIR /etc/zabbix/externalscripts/${project}

RUN pip3.6 install -r requirements.txt 

ENV TZ=Europe/Moscow
RUN ln -fs /usr/share/zoneinfo/$TZ /etc/localtime

RUN echo "00 03 * * 6 /usr/local/orbit/pyvmsnap/pyvmsnap.py create > /usr/local/orbit/pyvmsnap/data/output" > /tmp/crontab && \
    echo "00 03 * * 3 /usr/local/orbit/pyvmsnap/pyvmsnap.py remove > /usr/local/orbit/pyvmsnap/data/output" >> /tmp/crontab && \
    crontab /tmp/crontab && \
    rm /tmp/crontab

CMD ["crond","-n"]
