# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory in the container
WORKDIR /usr/src/app

# Install pip-tools for dependency management
RUN pip install pip-tools

# Copy only the requirements file to use Docker cache
COPY requirements.in ./
RUN pip-compile requirements.in
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Make port available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV NAME World

# Run run.py when the container launches
CMD ["python", "./run.py"]