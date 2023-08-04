# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy requirements.txt into the container at /app
COPY app/requirements.txt requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Run app.py when the container launches
ENTRYPOINT ["streamlit", "run", "Welcome_to_Happy_Graphs.py"]