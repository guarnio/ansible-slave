FROM docker.io/centos

ENV LANG en_US.UTF-8
LABEL com.bcgaudio.version="1.0" \
      com.bcgaudio.name="BCGAudio CentOS 8 Base Image" \
      com.bcgaudio.build-date="20200407" \
      com.bcgaudio.maintainer="Marco Guarnieri <mguarnieri@outlook.es>"

#RUN yum install -y git java-11-openjdk centos-release-ansible-29

#ENV JAVA_HOME /usr/lib/jvm/jre-11-openjdk/

RUN groupadd -g 1000 jenkins \
    && adduser --create-home --home-dir /home/jenkins -g jenkins -u 1000 -s /bin/bash jenkins \
    && mkdir /home/jenkins/.ssh && chown jenkins:jenkins /home/jenkins/.ssh \
    && chown -R jenkins: /home/jenkins \
    && yum install -y git centos-release-ansible-29 unzip glibc-locale-source  \
    && yum install -y ansible openssh-clients python3-dns python3-requests \
    && yum clean all \
    && rm -rf /var/cache/yum \
    && architecture=$(case $(arch) in aarch64) echo "arm64";; x86_64) echo "amd64";; armv7l)  echo "arm";; esac) \
    && curl https://releases.hashicorp.com/packer/1.5.6/packer_1.5.6_linux_${architecture}.zip -o /tmp/packer.zip && unzip /tmp/packer.zip -d /usr/local/bin/ && rm -rf /tmp/packer.zip \ 
    && curl https://releases.hashicorp.com/vault/1.4.2/vault_1.4.2_linux_${architecture}.zip -o /tmp/vault.zip && unzip /tmp/vault.zip -d /usr/local/bin/ && rm -rf /tmp/vault.zip \
    && mkdir -p /usr/share/ansible/plugins/lookup \
    && localedef -i en_US -f UTF-8 en_US.UTF-8

COPY scripts/vault.py /usr/share/ansible/plugins/lookup
WORKDIR /home/jenkins
VOLUME /home/jenkins

USER jenkins
CMD ["/bin/bash"]
