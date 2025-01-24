FROM python:3.9
ENV APP_HOME=/home/
WORKDIR $APP_HOME
COPY client.py client.py

RUN apt-get update && apt-get install -y sudo
RUN apt-get install -y iputils-ping
RUN apt-get install -y vim
RUN sudo apt install -y telnet
RUN pip install requests
