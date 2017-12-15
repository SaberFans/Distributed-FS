FROM python:3


RUN mkdir -p /root/.ssh

RUN touch /root/.ssh/known_hosts

WORKDIR /tmp

RUN apt-get update

ADD . /code

WORKDIR /code

RUN pip install -r requirements.txt

CMD ["python", "fileserver.py"]