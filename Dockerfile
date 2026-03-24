FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y nginx gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*


RUN rm -f /etc/nginx/sites-enabled/default \
    && rm -f /etc/nginx/sites-available/default

WORKDIR /app


COPY requirements.txt .
RUN pip install pip --upgrade && pip install -r requirements.txt

COPY . .


RUN cp ./nginx/conf.conf /etc/nginx/conf.d/


RUN chmod +x start.sh

EXPOSE 80

CMD ["./start.sh"]