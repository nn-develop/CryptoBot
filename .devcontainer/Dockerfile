FROM python:3.13-slim-bookworm

# Create a group with GID 1000 and a user with UID 1000
RUN groupadd -g 1000 devgroup && \
    useradd -u 1000 -g devgroup -m -s /bin/bash devuser

# Set the working directory
# WORKDIR /workspace

# Copy the requirements files
COPY requirements-dev.txt requirements-dev.txt
COPY requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements-dev.txt

# Switch to the non-root user 'devuser'
USER devuser

