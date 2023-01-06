FROM ubuntu:22.04
USER root


ARG     instafarm_mongo_pass \
        instafarm_mongo_port \
        instafarm_mongo_ip \
        instafarm_mongo_db_name \
        instafarm_mongo_user


WORKDIR /sanic

ENV DEBIAN_FRONTEND noninteractive

RUN echo "locales locales/locales_to_be_generated multiselect en_US.UTF-8 UTF-8" | debconf-set-selections \
    && echo "locales locales/default_environment_locale select en_US.UTF-8" | debconf-set-selections \
    && apt-get update \
    && apt-get --yes --no-install-recommends install \
        locales tzdata ca-certificates sudo \
        bash-completion iproute2 tar unzip curl rsync vim nano tree \
    && rm -rf /var/lib/apt/lists/*
ENV LANG en_US.UTF-8


RUN apt-get update \
    && apt-get --yes --no-install-recommends install \
        python3 python3-dev \
        python3-pip python3-venv python3-wheel python3-setuptools \
        build-essential cmake \
        graphviz git openssh-client \
        libssl-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*


ENV     INSTAFARM_MONGO_PASS=$instafarm_mongo_pass \
        INSTAFARM_MONGO_PORT=$instafarm_mongo_port \
        INSTAFARM_MONGO_IP=$instafarm_mongo_ip \
        INSTAFARM_MONGO_DB_NAME=$instafarm_mongo_db_name \
        INSTAFARM_MONGO_USER=$instafarm_mongo_user


COPY ./ ./

RUN python3 -m pip install -r requirements.txt
CMD ["python3", "rest_api_launcher.py"]
