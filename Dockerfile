FROM nvidia/cuda:9.1-runtime
LABEL maintainer="José Antonio Perdiguero López <perdy.hh@gmail.com>"

ENV APP=barrenero-api

# Install locales
RUN apt-get update && \
    apt-get install -y locales locales-all
ENV LANG='es_ES.UTF-8' LANGUAGE='es_ES.UTF-8:es' LC_ALL='es_ES.UTF-8' PYTHONIOENCODING='utf-8'

# Install system requirements
RUN apt-get update && \
    apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        software-properties-common \
        git \
        curl && \
    apt-get clean && \
    rm -rf /tmp/* \
        /var/tmp/* \
        /var/lib/apt/lists/* \
        /var/cache/apt/archives/*.deb \
        /var/cache/apt/archives/partial/*.deb \
        /var/cache/apt/*.bin

RUN add-apt-repository -y ppa:jonathonf/python-3.6 && \
    apt-get update && \
    apt-get install -y python3.6 python3-pip python3.6-dev && \
    apt-get clean && \
    rm -rf /tmp/* \
        /var/tmp/* \
        /var/lib/apt/lists/* \
        /var/cache/apt/archives/*.deb \
        /var/cache/apt/archives/partial/*.deb \
        /var/cache/apt/*.bin

# Install docker
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add - && \
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" && \
    apt-get update && \
    apt-get install -y docker-ce && \
    apt-get clean && \
    rm -rf /tmp/* \
        /var/tmp/* \
        /var/lib/apt/lists/* \
        /var/cache/apt/archives/*.deb \
        /var/cache/apt/archives/partial/*.deb \
        /var/cache/apt/*.bin

# Create project dirs
RUN mkdir -p /srv/apps/$APP/logs
WORKDIR /srv/apps/$APP

# Install pip requirements
COPY requirements.txt constraints.txt /srv/apps/$APP/
RUN python3.6 -m pip install --upgrade pip && \
    python3.6 -m pip install --no-cache-dir -r requirements.txt -c constraints.txt && \
    rm -rf $HOME/.cache/pip/*

# Copy application
COPY . /srv/apps/$APP/

ENTRYPOINT ["./run"]
