#!/usr/bin/env sh
#shellcheck shell=sh

set -ex

REPO=gekowa
IMAGE=cue-splitter
PLATFORMS="linux/amd64"

docker context use x86_64
export DOCKER_CLI_EXPERIMENTAL="enabled"
# docker buildx use homecluster

# Build & push latest
docker buildx build -t "${REPO}/${IMAGE}:latest" --compress --push --platform "${PLATFORMS}" .

if ! docker help pushrm >/dev/null 2>&1; then
    printf '%s\n' 'Warning: docker-pushrm is not installed; skipping Docker Hub overview upload. Install: https://github.com/christian-korneck/docker-pushrm#installation' >&2
elif ! docker pushrm --file README.md "${REPO}/${IMAGE}"; then
    printf '%s\n' "Image ${REPO}/${IMAGE}:latest was pushed, but the Docker Hub overview upload failed." >&2
    exit 1
fi
