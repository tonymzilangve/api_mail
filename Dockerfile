FROM python:3
RUN apt-get update -y
RUN apt-get upgrade -y

WORKDIR /usr/src/app

ENV PYTHONUNBUFFERED 1

RUN apk update\
    && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install --upgrade pip
COPY .requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . ./mailinglist

CMD [ "python",  "manage.py", "runserver", "0.0.0.0:8000"]