FROM python:3.11-slim


COPY .  /app

WORKDIR /app

RUN pip install -r requirements.txt


# keeping container alive
#CMD ["tail", "-f", "/dev/null"]

CMD [ "python","app.py" ]
