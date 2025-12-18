# Build
FROM golang:1.25-alpine AS builder
RUN apk add --no-cache git build-base

WORKDIR /src
RUN git clone --branch v0.5.8 --depth 1 https://github.com/firefart/stunner.git .

ENV CGO_ENABLED=0
RUN go build -ldflags="-s -w" -o /usr/local/bin/stunner .

# Runtime minimale
FROM alpine:3.19
RUN apk add --no-cache ca-certificates curl
RUN addgroup -S stunner && adduser -S -G stunner stunner
COPY --from=builder /usr/local/bin/stunner /usr/local/bin/stunner
USER stunner
WORKDIR /home/stunner
