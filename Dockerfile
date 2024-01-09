# Use Ubuntu as the base image
FROM ubuntu:latest

# Install necessary dependencies
RUN apt-get update && apt-get install -y python3 python3-pip

# Set the working directory inside the container
WORKDIR /app

# Copy the Python application files to the container
COPY . .

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Create a non-privileged user
RUN useradd -m myuser

# Set the ownership of the application files to the non-privileged user
RUN chown -R myuser:myuser /app

# Switch to the non-privileged user
USER myuser

# Expose port 8000
EXPOSE 8000

# Set the command to run the application
CMD ["python3", "veracode_prometheus_exporter.py"]