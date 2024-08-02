# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Update and install necessary packages
RUN apt-get update && apt-get install -y \
    git \
    python3-dev \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository
RUN git clone https://github.com/ganeshmo/Flask4Ferry.git /app

# Create and activate the virtual environment
RUN python3 -m venv myenv

# Activate the virtual environment and install required Python packages
RUN /bin/bash -c "source myenv/bin/activate && \
    pip install --upgrade pip && \
    pip install bcrypt flask-mysqldb email_validator flask-wtf && \
    pip freeze"

# Expose the required port
EXPOSE 5000

# Start the application
CMD ["/bin/bash", "-c", "source myenv/bin/activate && python app.py"]
