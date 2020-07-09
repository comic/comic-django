USER_ID = $(shell id -u)
export DOCKER_BUILDKIT = 1
PYTHON_VERSION = 3.8
GDCM_VERSION_TAG = 3.0.6

build_web_base:
	docker build \
        --build-arg PYTHON_VERSION=$(PYTHON_VERSION) \
        --build-arg GDCM_VERSION_TAG=$(GDCM_VERSION_TAG) \
        -t grandchallenge/web-base:py$(PYTHON_VERSION)-gdcm$(GDCM_VERSION_TAG) \
        -f dockerfiles/web-base/Dockerfile \
        .

build_web:
	docker build \
		--build-arg PYTHON_VERSION=$(PYTHON_VERSION) \
        --build-arg GDCM_VERSION_TAG=$(GDCM_VERSION_TAG) \
		--build-arg COMMIT_ID=$(GIT_COMMIT_ID) \
		--target test \
		-t grandchallenge/web-test:$(GIT_COMMIT_ID)-$(GIT_BRANCH_NAME) \
		-t grandchallenge/web-test:latest \
		-f dockerfiles/web/Dockerfile \
		.
	docker build \
		--build-arg PYTHON_VERSION=$(PYTHON_VERSION) \
        --build-arg GDCM_VERSION_TAG=$(GDCM_VERSION_TAG) \
		--build-arg COMMIT_ID=$(GIT_COMMIT_ID) \
		--target dist \
		-t grandchallenge/web:$(GIT_COMMIT_ID)-$(GIT_BRANCH_NAME) \
		-t grandchallenge/web:latest \
		-f dockerfiles/web/Dockerfile \
		.

build_http:
	docker build \
		-t grandchallenge/http:$(GIT_COMMIT_ID)-$(GIT_BRANCH_NAME) \
		-t grandchallenge/http:latest \
		dockerfiles/http

build: build_web build_http

push_web_base:
	docker push grandchallenge/web-base:py$(PYTHON_VERSION)-gdcm$(GDCM_VERSION_TAG)

push_web:
	docker push grandchallenge/web:$(GIT_COMMIT_ID)-$(GIT_BRANCH_NAME)
	docker push grandchallenge/web:latest

push_http:
	docker push grandchallenge/http:$(GIT_COMMIT_ID)-$(GIT_BRANCH_NAME)
	docker push grandchallenge/http:latest

push: push_web push_http

migrations:
	docker-compose run -u $(USER_ID) --rm web python manage.py makemigrations

.PHONY: docs
docs:
	docker-compose run --rm -v `pwd`/docs:/docs -u $(USER_ID) web bash -c "cd /docs && make html"
