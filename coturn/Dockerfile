FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    coturn \
    && rm -rf /var/lib/apt/lists/*

COPY turnserver.conf /etc/turnserver.conf

EXPOSE 3478/tcp 3478/udp 49152-65535/udp

CMD ["turnserver", "-c", "/etc/turnserver.conf"] 