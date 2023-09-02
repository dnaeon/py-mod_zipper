FROM httpd:2.4.57-bookworm

WORKDIR /app
COPY . .
COPY ./apache2/mod_zipper.conf /usr/local/apache2/conf/extra/mod_zipper.conf
COPY ./apache2/httpd.conf /usr/local/apache2/conf/httpd.conf

RUN apt-get update && \
    apt-get install -y python3.11 python3-pip python-is-python3 libapache2-mod-python && \
    rm -f /usr/lib/python3.11/EXTERNALLY-MANAGED && \
    pip install . && \
    rm -rf /var/lib/apt/lists/*

EXPOSE 80
