FROM python:3.9.0

ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive

RUN mkdir -p /deploy/app

WORKDIR /deploy/app

RUN apt-get update && apt-get install -y unzip && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get -y install xvfb
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
RUN apt-get update && apt-get -y install google-chrome-stable

RUN wget -N https://chromedriver.storage.googleapis.com/2.36/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip && rm chromedriver_linux64.zip
RUN mv -f chromedriver /usr/local/bin/chromedriver && chmod u+x /usr/local/bin/chromedriver

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /deploy/app

CMD ["sleep","2"]
