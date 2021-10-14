FROM docker.io/centos

ENV LANG en_US.UTF-8
ENV PACKER_VERSION=1.7.2
ENV TERRAFORM_VERSION=1.0.9
ENV VAULT_VERSION=1.8.3

LABEL com.bcgaudio.version="1.0" \
      com.bcgaudio.name="BCGAudio CentOS 8 Base Image" \
      com.bcgaudio.build-date="20200407" \
      com.bcgaudio.maintainer="Marco Guarnieri <mguarnieri@outlook.es>"

RUN groupadd -g 1000 jenkins \
    && adduser --create-home --home-dir /home/jenkins -g jenkins -u 1000 -s /bin/bash jenkins \
    && mkdir /home/jenkins/.ssh && chown jenkins:jenkins /home/jenkins/.ssh \
    && chown -R jenkins: /home/jenkins \
    && yum install -y git centos-release-ansible-29 unzip glibc-locale-source  \
    && yum install -y ansible openssh-clients python3-dns python3-requests python3-pip \
    && yum clean all \
    && rm -rf /var/cache/yum \
    && architecture=$(case $(arch) in aarch64) echo "arm64";; x86_64) echo "amd64";; armv7l)  echo "arm";; esac) \
    && curl https://releases.hashicorp.com/packer/${PACKER_VERSION}/packer_${PACKER_VERSION}_linux_${architecture}.zip -o /tmp/packer.zip && unzip /tmp/packer.zip -d /usr/local/bin/ && rm -rf /tmp/packer.zip \ 
    && curl https://releases.hashicorp.com/vault/${VAULT_VERSION}/vault_${VAULT_VERSION}_linux_${architecture}.zip -o /tmp/vault.zip && unzip /tmp/vault.zip -d /usr/local/bin/ && rm -rf /tmp/vault.zip \
    && curl https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_${architecture}.zip -o /tmp/terraform.zip && unzip /tmp/terraform.zip -d /usr/local/bin/ && rm -rf /tmp/terraform.zip \
    && pip3 install awscli \
    && mkdir -p /usr/share/ansible/plugins/lookup 

COPY scripts/vault.py /usr/share/ansible/plugins/lookup
COPY sshconfig /home/jenkins/.ssh/config
RUN chown jenkins:jenkins /home/jenkins/.ssh/config && chmod 600 /home/jenkins/.ssh/config
WORKDIR /home/jenkins
VOLUME /home/jenkins

USER jenkins
CMD ["/bin/bash"]
