.ONESHELL:

ALPINE_VERSION:=3.18

CONTAINER_DEFINITION_FILE=docker/Dockerfile
CONTAINER_BUILD_ARGS:="--build-arg alpine_version=${ALPINE_VERSION}"
CONTAINER_IMAGE_NAME=repo-ci
CONTAINER_IMAGE_TAG:=latest

help:
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make \033[36m<command> <option>\033[0m\n"} /^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@printf "\033[1mVariables\033[0m\n"
	@grep -E '^[a-zA-Z0-9_-]+.*?### .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?### "}; {printf "  \033[36m%-21s\033[0m %s\n", $$1, $$2}'
	@# Use ##@ <section> to define a section
	@# Use ## <comment> aside of the target to get it shown in the helper
	@# Use ### <comment> to comment a variable

##@ build
build: ## docker build
	@docker build -f ${CONTAINER_DEFINITION_FILE} "${CONTAINER_BUILD_ARGS}" -t ${CONTAINER_IMAGE_NAME}:${CONTAINER_IMAGE_TAG} .
	@docker images | grep ${CONTAINER_IMAGE_NAME}

run: build ## jump in the container
	@docker run -it --rm ${CONTAINER_IMAGE_NAME}:${CONTAINER_IMAGE_TAG} bash
