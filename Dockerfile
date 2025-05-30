FROM ubuntu:18.04 as base

COPY ./build /app/build 
WORKDIR /app/build/
RUN apt-get update && \
    apt-get install -y \
    # git \
    build-essential \
    apt-utils \
    libudev-dev \
    libusb-1.0-0-dev \
    libfox-1.6-dev \
    autotools-dev \
    autoconf \
    automake \
    libtool \
    libffi-dev \
    # && git clone https://github.com/signal11/hidapi.git \
    && cd /app/build/hidapi \
    && ./bootstrap \
    && ./configure \
    && make \
    && make install \
    && cd /app/build \
    # && git clone https://github.com/wjasper/Linux_Drivers.git \
    && cd /app/build/Linux_Drivers/USB/mcc-libusb \
    && make \
    && make install \
    && ldconfig \
    # clean up install
    && rm -rf /var/lib/apt/lists/*

FROM python:3.9-slim
COPY --from=base /usr/lib/libmccusb.so /usr/lib/libmccusb.so
COPY --from=base /usr/lib/libmccusb.a /usr/lib/libmccusb.a
COPY --from=base /usr/local /usr/local

ENV DEBIAN_FRONTEND=noninteractive 
RUN apt-get update && \
    apt-get install -y \
    bash \
    python3-pip \
    libtool pkg-config build-essential autoconf automake \
    libzmq3-dev \
    libftdi1 \
    git \ 
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN python3 -m pip install --upgrade pip && \
     pip3 --no-cache-dir install -r requirements.txt

# COPY ./build/gpib /app/build/gpib
WORKDIR /app/build/gpib
RUN python3 setup.py install

##FROM ubuntu:18.04
# FROM python:3.6-alpine
# COPY --from=base /usr/lib/libmccusb.so /usr/lib/libmccusb.so
# COPY --from=base /usr/lib/libmccusb.a /usr/lib/libmccusb.a
# COPY --from=base /usr/local /usr/local