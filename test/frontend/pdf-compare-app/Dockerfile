FROM debian:buster

# Install system packages
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    wget \
    curl \
    vim \
    libc6 \
    libc-bin \
    gnupg \
    ca-certificates \
    && apt-get clean

# Show glibc version
RUN ldd --version

# Install Node.js (v18 LTS)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

# Check versions
RUN node -v && npm -v && npx -v

# Set working directory
WORKDIR /workspace

# Default to bash shell
CMD ["/bin/bash"]
