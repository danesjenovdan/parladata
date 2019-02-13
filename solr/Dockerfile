FROM solr:7.6.0

USER root

RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get -y install \
      apt-transport-https \
      build-essential \
      ca-certificates \
      curl \
      git \
      libssl-dev \
      wget \
      openjdk-8-jdk \
      maven

# RUN update-java-alternatives -s java-1.8.0-openjdk-amd64
# ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64

RUN mkdir -p /home/solr; chown solr:solr /home/solr;
USER solr

RUN git clone https://bitbucket.org/mavrik/slovene_lemmatizer.git
RUN cd slovene_lemmatizer && \
    make && \
    JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64 mvn compile && \
    JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64 mvn package

USER root
RUN cp slovene_lemmatizer/bin/libLemmatizer.so /usr/lib
RUN cp slovene_lemmatizer/bin/lemmatizer /usr/bin
USER solr
