FROM python:3.11-alpine

# Install strace for syscall monitoring
RUN apk add --no-cache strace iproute2

# Create a non-root user (never run untrusted code as root)
RUN adduser -D sandboxuser
USER sandboxuser

WORKDIR /sandbox
