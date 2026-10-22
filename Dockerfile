# Use the official Ubuntu 22.04 image as the base image
# This image provides a minimal Ubuntu environment.
FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

# Install Python and other dependencies
RUN apt-get update && apt-get install -y \
    software-properties-common build-essential wget curl tzdata \
    python3.10 python3.10-dev python3.10-distutils \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install pip for Python 3.10
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10

# Set the working directory inside the container
WORKDIR /app

# Copy the rest of the application code into the container
COPY . /app

# Install any necessary Python packages
# The --no-cache-dir flag helps keep the image small
RUN python3.10 -m pip install --trusted-host pypi.python.org --no-cache-dir -r requirements.txt

# Copy the entrypoint.sh script
COPY entrypoint.sh /entrypoint.sh

# Make entrypoint.sh executable
RUN chmod +x /entrypoint.sh

# Start the server using entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
