FROM python:3.7

WORKDIR /net_workdir
RUN apt-get update && apt-get upgrade g++ build-essential git net-tools vim openssh-server make -y

EXPOSE 22

CMD ["/bin/bash"]