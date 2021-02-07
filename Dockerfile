FROM python:3.7-buster

RUN apt-get update && apt-get install nginx vim -y --no-install-recommends
COPY nginx.default /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

RUN mkdir -p /opt/app
RUN mkdir -p /opt/app/converter_web_app
RUN mkdir -p /opt/app/nltk_data

ENV NLTK_DATA=/opt/app/nltk_data

COPY requirements.txt start-server.sh /opt/app/
COPY . /opt/app/converter_web_app/
WORKDIR /opt/app
RUN pip install -r requirements.txt
RUN [ "python", "-c", "import nltk; nltk.download('punkt')" ]
RUN chown -R www-data:www-data /opt/app

EXPOSE 8020
STOPSIGNAL SIGTERM
CMD ["/opt/app/start-server.sh"]