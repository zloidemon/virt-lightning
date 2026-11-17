ARG ALPINE_VERSION=3.19
FROM alpine:${ALPINE_VERSION} AS builder

WORKDIR /app

RUN apk add --no-cache \
  py3-build \
  git

COPY . /app

RUN python -m build

FROM alpine:${ALPINE_VERSION}

WORKDIR /app

# cdrkit provides genisoimage and mkpasswd hashes the root password.
# Both are needed to build the config drive of a virtual machine.
RUN apk add --no-cache \
  ca-certificates \
  cdrkit \
  git \
  mkpasswd \
  py3-libvirt \
  py3-pip \
  py3-wcwidth \
  py3-yaml

COPY --from=builder /app/dist/virt_lightning-*-none-any.whl /app

RUN pip install --break-system-packages \
  "init-system @ git+https://github.com/virt-lightning/init-system.git" \
  virt_lightning-*-none-any.whl && \
  rm -fr \
    virt_lightning-*-none-any.whl \
    /root/.cache
