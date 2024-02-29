FROM registry.access.redhat.com/ubi9/python-311

COPY app.py

RUN pip install --no-cache-dir Flask requests pytz

ENV CLIENT_ID= 
ENV CLIENT_SECRET=
ENV MAP_SERVER_URL=

EXPOSE 8080

CMD ["python", "app.py"]
