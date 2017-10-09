FROM nvidia/cuda:latest

ENV APP=barrenero-api

RUN apt-get update && \
    apt-get install -y \
        locales \
        locales-all
ENV LANG='es_ES.UTF-8' LANGUAGE='es_ES.UTF-8:es' LC_ALL='es_ES.UTF-8'

# Install build requirements
RUN apt-get update && \
    apt-get install -y \
        build-essential \
        apt-transport-https \
        software-properties-common \
        git \
        curl

# Install docker
RUN apt-get install -y docker.io

# Install python3.6
RUN add-apt-repository -y ppa:jonathonf/python-3.6 && \
    apt-get update && \
    apt-get install -y python3.6 python3-pip

# Add Phusion ppa
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 561F9B9CAC40B2F7
RUN echo deb https://oss-binaries.phusionpassenger.com/apt/passenger jessie main > /etc/apt/sources.list.d/passenger.list

# Install system requirements
RUN apt-get update && \
    apt-get install -y \
        libpq-dev \
        passenger

# Create project dirs
RUN mkdir -p /srv/apps/$APP/logs
WORKDIR /srv/apps/$APP

# Install pip requirements
COPY requirements.txt constraints.txt /srv/apps/$APP/
RUN python3.6 -m pip install --upgrade pip && \
    python3.6 -m pip install --no-cache-dir -r requirements.txt -c constraints.txt

# Clean up
RUN apt-get clean && \
    apt-get purge --auto-remove -y \
        build-essential \
        apt-transport-https \
        software-properties-common && \
    rm -rf $HOME/.cache/pip/* \
        /tmp/* \
        /etc/apt/sources.list.d/passenger.list \
        /var/tmp/* \
        /var/lib/apt/lists/* \
        /var/cache/apt/archives/*.deb \
        /var/cache/apt/archives/partial/*.deb \
        /var/cache/apt/*.bin

# Copy application
COPY . /srv/apps/$APP/

EXPOSE 8000

ENTRYPOINT ["./run"]
