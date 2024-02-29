# Use the miniconda container
FROM condaforge/mambaforge:latest as Daiquiri

LABEL description = "Daiquiri container for GleamXGPMonitoring"

# Install curl
RUN  apt-get -y update && \
    DEBIAN_FRONTEND="noninteractive" TZ="Australia/Perth" apt-get -y install curl gcc \
    git \
    build-essential \
    libxml2-dev libxslt-dev \
    zlib1g-dev \
    libssl-dev \
    sqlite3
    # python3-dev \
    # python3-venv

# create the app user
RUN addgroup --system app &&\
    adduser --system --group app &&\
    mkdir -p /home/app

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir -p $APP_HOME/staticfiles
WORKDIR $APP_HOME

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# create a location for Django to keep static files
RUN mkdir -p /var/www/static

# copy project requirements
COPY ./environment.yml .

# Create environment and activate it
RUN mamba env update --name base --file environment.yml