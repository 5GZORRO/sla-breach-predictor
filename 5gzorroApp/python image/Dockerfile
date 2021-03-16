FROM ubuntu:latest

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# Install conda in order to get tensorflow. Instaling tensorflow from pip does not work.

ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"
RUN apt-get update

RUN apt-get install -y wget && rm -rf /var/lib/apt/lists/*

RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh 
RUN conda --version

# Install tensorflow
RUN conda install -c conda-forge tensorflow

ENV PATH="/usr/local/lib/:${PATH}"

# Download and install python libraries needed for sla-service
RUN pip install kafka-python

RUN pip install fastapi

RUN pip install uvicorn

RUN pip install pandas

RUN pip install numpy

RUN pip install scipy

RUN pip install scikit-learn

RUN pip install pillow

RUN pip install h5py

RUN pip install keras

RUN pip install statsmodels