FROM kalilinux/kali-rolling

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Rome

# Imposta il timezone senza prompt interattivo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Installa solo i pacchetti necessari
RUN apt-get update && \
    apt-get install -y --no-install-recommends sippts && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*