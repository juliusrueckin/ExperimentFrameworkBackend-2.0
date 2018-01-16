FROM debian:8

MAINTAINER Julius Rueckin <julius.rueckin@gmail.com>

# install anaconda python 3
RUN apt-get update --fix-missing && apt-get install -y wget bzip2 ca-certificates \
    libglib2.0-0 libxext6 libsm6 libxrender1 \
    git mercurial subversion

RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    wget --quiet https://repo.continuum.io/archive/Anaconda3-5.0.1-Linux-x86_64.sh -O ~/anaconda.sh && \
    /bin/bash ~/anaconda.sh -b -p /opt/conda && \
    rm ~/anaconda.sh

RUN apt-get install -y curl grep sed dpkg && \
    TINI_VERSION=`curl https://github.com/krallin/tini/releases/latest | grep -o "/v.*\"" | sed 's:^..\(.*\).$:\1:'` && \
    curl -L "https://github.com/krallin/tini/releases/download/v${TINI_VERSION}/tini_${TINI_VERSION}.deb" > tini.deb && \
    dpkg -i tini.deb && \
    rm tini.deb && \
    apt-get clean

# install pip
RUN apt-get --assume-yes install python3-pip 

# install dependencies
RUN pip3 install -r requirements.txt

# install python telegram bot
RUN git clone https://github.com/python-telegram-bot/python-telegram-bot --recursive 
RUN cd python-telegram-bot
RUN python setup.py install
RUN cd ..
RUN rm -rf python-telegram-bot

# clean up installations
RUN make clean

# set environment variables for conda and python app
ENV PATH /opt/conda/bin:$PATH
ENV APP /usr/src/app

# create and change to working directory
RUN mkdir -p $APP
RUN cd $APP
WORKDIR $APP

# clone application from github
RUN git clone https://github.com/juliusrueckin/ExperimentFrameworkBackend-2.0.git .

# open port 8080 for bottle api
EXPOSE 8080