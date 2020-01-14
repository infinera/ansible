FROM ubuntu:16.04
MAINTAINER Govindhi Venkatachalapathy "gvenkatachal@infinera.com"

RUN apt-get update  && apt-get install -y \
    python-pip \
    libxml2-dev \
    libxslt1-dev \
    python-dev \
    python-lxml \
    vim \
    build-essential \
    libssl-dev \
    libffi-dev
#Install customized ncclient
COPY /ncclient-infinera-0.5.3 /tmp/ncclient-infinera-0.5.3
WORKDIR /tmp/ncclient-infinera-0.5.3
RUN  python setup.py install

#Install Ansible
RUN python -m pip install ansible

#Create directories inside the docker 
RUN mkdir -p /home/infinera/net-automation

#Create the log directories of the test playbooks
RUN mkdir -p /home/infinera/net-automation/src/tests/ansible/library/logs_cli
RUN mkdir -p /home/infinera/net-automation/src/tests/ansible/library/logs_tl1
RUN mkdir -p /home/infinera/net-automation/src/tests/ansible/library/logs_netconf

#Copy the net-auto source code
COPY src/ /home/infinera/net-automation/src

#Copy the ansible.cfg
COPY src/ansible/ansible.cfg /etc/ansible/

#Set the working directory
WORKDIR /home/infinera/
