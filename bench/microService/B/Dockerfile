FROM python:3.9
ENV APP_HOME=/home/
WORKDIR $APP_HOME
RUN mkdir -p /home/data
COPY data/ /home/data
COPY B.py B.py

RUN apt-get update && apt-get install -y sudo
RUN apt install -y net-tools
RUN pip install Flask
RUN pip install requests

