FROM google/cloud-sdk:290.0.0
MAINTAINER "GFT"

ENV TERRAFORM_VERSION=0.12.24

RUN apt-get update
RUN apt-cache policy python3
RUN apt-cache policy python3-pip
RUN apt-cache policy git
RUN apt-cache policy unzip
RUN apt-cache policy wget
RUN apt-cache policy curl
RUN apt-cache policy dos2unix
RUN apt-cache policy nano
RUN apt-get install python3=3.8.2-3 python3-pip=20.0.2-5 unzip=6.0-25 wget=1.20.1-1.1 dos2unix=7.4.0-1 nano=3.2-3 -y \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*
RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# install terraform
ENV TF_DEV=true
ENV TF_RELEASE=true
RUN wget https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip
RUN unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip
RUN mv terraform /usr/local/bin/
# Enable Terraform logging
ENV TF_LOG=ERROR
ENV TF_LOG_PATH=/var/log/tb-gcp-dac-deployment.log

# install python libraries
WORKDIR /app
COPY . .
RUN pip install -r ./requirements.txt
RUN dos2unix app_docker.sh

RUN ["chmod", "+x", "./app_docker.sh"]
EXPOSE 3100
CMD ["/bin/bash", "./app_docker.sh"]

