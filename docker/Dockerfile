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

RUN apk add --no-cache \
  py3-libvirt \
  py3-pip \
  py3-wcwidth \
  py3-yaml

COPY --from=builder /app/dist/virt_lightning-*-none-any.whl /app

RUN pip install --break-system-packages \
  virt_lightning-*-none-any.whl && \
  rm -fr \
    virt_lightning-*-none-any.whl \
    /root/.cache
