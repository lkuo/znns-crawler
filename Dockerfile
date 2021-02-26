FROM python:3.9.2-buster

WORKDIR /app
COPY . .

RUN pip install scrapy && pip install pillow && pip install boto3

CMD ["scrapy", "crawl", "models"]
