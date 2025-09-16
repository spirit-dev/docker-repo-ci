ARG alpine_version

FROM gitlab-registry-internal.spirit-dev.net/infrastructure/docker/alpine:${alpine_version}
# FROM alpine:3.21

ARG alpine_version

LABEL alpine_version="${alpine_version}" \
    spiritdev_official="yes" \
    layer="1" \
    from="gitlab-registry-internal.spirit-dev.net/infrastructure/docker/alpine" \
    maintainer="bordat.jean@gmail.com"

COPY docker/assets/requirements.txt /scripts/requirements.txt

RUN apk add --no-cache bash=5.2.37-r0 python3=3.12.11-r0 py-pip=24.3.1-r0 git=2.47.3-r0 colordiff=1.0.21-r0 jq=1.7.1-r0 diffutils=3.10-r0 make=4.4.1-r2 curl=8.12.1-r1 \
    && pip install --no-cache-dir -r /scripts/requirements.txt --break-system-packages


# Install Helm
ARG HELM_VERSION=3.18.4
RUN curl -fsSL https://get.helm.sh/helm-v${HELM_VERSION}-linux-amd64.tar.gz | \
    tar -xzC /tmp && \
    mv /tmp/linux-amd64/helm /usr/local/bin/helm && \
    rm -rf /tmp/linux-amd64 && \
    chmod +x /usr/local/bin/helm

# Verify installation
RUN helm version --client

ENV FILTER_BRANCH_SQUELCH_WARNING=1

COPY docker/assets/clean_repo.py /scripts/clean_repo.py
COPY docker/assets/github_repo.py /scripts/github_repo.py
COPY docker/assets/gitlab_repo.py /scripts/gitlab_repo.py
COPY docker/assets/markdown.py /scripts/markdown.py
COPY docker/assets/repo_sync.py /scripts/repo_sync.py
