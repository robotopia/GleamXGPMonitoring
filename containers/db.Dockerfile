FROM postgres:15 as postgres-q3c

LABEL description = "PostgreSQL 15 with q3c"

# Install dependencies
RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen &&\
    locale-gen
RUN apt-get -y update &&\
    apt-get -y install \
    git make \
    gcc \
    postgresql-server-dev-15 \
    liblz-dev\
    libz-dev \
    liblz4-dev \
    libreadline-dev \
    libzstd-dev

# install q3c extension
RUN mkdir -p /build && cd /build &&\
    git clone https://github.com/segasai/q3c.git &&\
    cd q3c &&\
    make &&\
    make install