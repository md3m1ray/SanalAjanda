FROM python:3.13.1

RUN sudo apt-get update
RUN sudo apt-get install libpq-dev -y
RUN sudo apt-get install python3-dev build-essential -y
RUN sudo apt-get install postgresql-client -y

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV VIRTUAL_ENV=/opt/venv

RUN sudo pip install --upgrade pip
RUN sudo pip install virtualenv && python -m virtualenv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

ADD requirements.txt /tmp/requirements.txt
RUN sudo pip install -r /tmp/requirements.txt

COPY entrypoint.sh /srv/entrypoint.sh
RUN sudo sed -i 's/\r$//g' /srv/entrypoint.sh
RUN sudo chmod +x /srv/entrypoint.sh

COPY . /srv/app
WORKDIR /srv/app

ENTRYPOINT ["/srv/entrypoint.sh"]