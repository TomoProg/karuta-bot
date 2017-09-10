FROM python:3.4.3
MAINTAINER TomoProg <helloworld0306.xxx@gmail.com>
RUN apt-get update && apt-get install -y \
    vim-tiny
RUN pip install --upgrade pip
RUN pip install twitter
WORKDIR /app
