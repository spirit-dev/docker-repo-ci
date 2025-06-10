ARG alpine_version

# FROM gitlab-registry-internal.spirit-dev.net/infrastructure/docker/alpine:${alpine_version}
FROM alpine

ARG alpine_version

LABEL alpine_version="${alpine_version}" \
    spiritdev_official="yes" \
    layer="1" \
    from="gitlab-registry-internal.spirit-dev.net/infrastructure/docker/alpine" \
    maintainer="bordat.jean@gmail.com"

COPY docker/assets/requirements.txt /scripts/requirements.txt

RUN apk add --no-cache bash python3 py-pip git colordiff && \
    pip install -r /scripts/requirements.txt --break-system-packages

ENV FILTER_BRANCH_SQUELCH_WARNING=1

COPY docker/assets/clean_repo.py /scripts/clean_repo.py
COPY docker/assets/github_repo.py /scripts/github_repo.py
COPY docker/assets/gitlab_repo.py /scripts/gitlab_repo.py
COPY docker/assets/markdown.py /scripts/markdown.py
COPY docker/assets/repo_sync.py /scripts/repo_sync.py
