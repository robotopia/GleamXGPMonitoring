# Use the miniconda container
FROM condaforge/mambaforge:latest as gleamxdev

LABEL description = "Development web container for GleamXGPMonitoring"

# Install curl
RUN apt-get -y update && apt-get -y install curl cron gcc

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
COPY ./requirements.txt .

# Create environment and activate it
RUN mamba env update --name base --file environment.yml

FROM  gleamxdev as gleamxprod
LABEL description = "Production web container for GleamXGPMonitoring"

# install this app
COPY gleam_webapp $APP_HOME
