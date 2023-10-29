FROM python:3.9-slim

RUN apt-get update && apt-get -y install gcc python3-dev



COPY .  /app

WORKDIR /app

RUN pip install -r requirements.txt


# keeping container alive
#CMD ["tail", "-f", "/dev/null"]

CMD [ "python","app.py" ]
