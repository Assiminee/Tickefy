# Use Ubuntu 22.04 as the base image
FROM ubuntu:22.04

# Set the environment to non-interactive to avoid prompts during installation
ENV DEBIAN_FRONTEND=noninteractive
# Update apt repositories and install required packages (Git, curl, and build essentials)
RUN apt-get update && \
    apt-get install -y \
      git \
      curl \
      build-essential && \
    rm -rf /var/lib/apt/lists/*


# Install Node.js v22.x (which should install a version close to 22.14.0)
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Create and set the working directory
WORKDIR /app

RUN git clone --single-branch --branch FrontendBranch \
    https://github.com/dermokill/Tickefy.git .

# Install the Node.js dependencies
RUN npm install --legacy-peer-deps

# (Optional) Expose the port your application listens on
# Adjust the port number if your application uses a different one (commonly 3000)
EXPOSE 3000

# Define the command to run your application.
# This assumes that your package.json has a "start" script defined.
CMD ["npm", "run", "dev", "--", "--host"]