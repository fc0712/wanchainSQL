FROM python:3.9.12-slim-buster

COPY .  /app

WORKDIR /app

RUN pip install -r requirements.txt


# keeping container alive
CMD ["tail", "-f", "/dev/null"]

#CMD [ "python","app.py" ]
