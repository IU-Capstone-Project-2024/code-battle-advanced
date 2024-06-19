FROM python:3.13-rc-alpine

USER root

#Installing MongoDB
RUN echo 'http://dl-cdn.alpinelinux.org/alpine/v3.6/main' >> /etc/apk/repositories
RUN echo 'http://dl-cdn.alpinelinux.org/alpine/v3.6/community' >> /etc/apk/repositories
RUN apk add py3-pip

#Installing relevant python packages
RUN pip install Flask-PyMongo markdown bcrypt redis pytz

COPY ./app.py /app.py
COPY ./templates /templates
RUN mkdir -p /static

EXPOSE 5000

ENTRYPOINT ["python3", "/app.py"]

