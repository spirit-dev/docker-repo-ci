ARG alpine_version

# FROM gitlab-registry-internal.spirit-dev.net/infrastructure/docker/alpine:${alpine_version}
FROM alpine:3.21

ARG alpine_version

LABEL alpine_version="${alpine_version}" \
    spiritdev_official="yes" \
    layer="1" \
    from="gitlab-registry-internal.spirit-dev.net/infrastructure/docker/alpine" \
    maintainer="bordat.jean@gmail.com"

COPY docker/assets/requirements.txt /scripts/requirements.txt

RUN apk add --no-cache bash=5.2.37-r0 python3=3.12.11-r0 git=2.47.2-r0 colordiff=1.0.21-r0
# hadolint ignore=DL3018
RUN apk add --no-cache py-pip && \
    pip install --no-cache-dir -r /scripts/requirements.txt --break-system-packages

ENV FILTER_BRANCH_SQUELCH_WARNING=1

COPY docker/assets/clean_repo.py /scripts/clean_repo.py
COPY docker/assets/github_repo.py /scripts/github_repo.py
COPY docker/assets/gitlab_repo.py /scripts/gitlab_repo.py
COPY docker/assets/markdown.py /scripts/markdown.py
COPY docker/assets/repo_sync.py /scripts/repo_sync.py
