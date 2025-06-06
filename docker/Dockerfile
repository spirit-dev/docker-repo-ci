ARG alpine_version

# FROM gitlab-registry-internal.spirit-dev.net/infrastructure/docker/alpine:${alpine_version}
FROM alpine

ARG alpine_version

LABEL alpine_version="${alpine_version}" \
    spiritdev_official="yes" \
    layer="1" \
    from="gitlab-registry-internal.spirit-dev.net/infrastructure/docker/alpine" \
    maintainer="bordat.jean@gmail.com"

RUN apk add --no-cache bash python3 py-pip git colordiff && \
    pip install pyyaml git-filter-repo detect-secrets python-gitlab PyGithub --break-system-packages

ENV FILTER_BRANCH_SQUELCH_WARNING=1

COPY docker/assets/clean_repo.py /scripts/clean_repo.py
COPY docker/assets/github-repo.py /scripts/github-repo.py
COPY docker/assets/gitlab-repo.py /scripts/gitlab-repo.py
