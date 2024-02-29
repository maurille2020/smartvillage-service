FROM registry.access.redhat.com/ubi9/python-311

COPY app.py

RUN pip install --no-cache-dir Flask requests pytz

ENV CLIENT_ID= 
ENV CLIENT_SECRET=
ENV MAP_SERVER_URL=

EXPOSE 8080

CMD ["python", "app.py"]

git config --global user.email "maurille2020@gmail.com"

git config --global user.name "Maurille Beheton"


git config --global credential.helper store



//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