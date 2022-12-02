FROM python:3.10-alpine

RUN mkdir app
WORKDIR /app
COPY . .

RUN pip3 install -r requirements.txt

CMD python3 main.py