# --- Stage 1: Base Image ---
# Use an official, slim Python base image. 'slim' is a good balance
# of size and having necessary OS tools.
FROM python:3.12-slim

# --- Metadata ---
LABEL maintainer="Mohamed Yassine Ben Said"
LABEL description="Backend service for the Automaton Animator project."

# --- Environment Variables ---
# Set the working directory inside the container.
WORKDIR /app

# Prevents Python from writing .pyc files to disc.
ENV PYTHONDONTWRITEBYTECODE = 1
# Ensures Python output is sent straight to the terminal without buffering.
ENV PYTHONUNBUFFERED = 1

# --- Dependency Installation ---
# Copy only the requirements file first to leverage Docker's layer caching.
# This layer will only be rebuilt if requirements.txt changes.
COPY requirements.txt .

# Install the Python dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# --- Application Code ---
# Copy the rest of the application source code into the working directory.
COPY . .

# --- Security Best Practice: Run as non-root user ---
# Create a new user and group to run the application.
RUN addgroup --system app && adduser --system --group app

# Switch to the new, non-privileged user.
USER app

# --- Network Configuration ---
# Expose the port the app will run on. This is documentation for the user
# and allows Docker to map the port. Gunicorn will bind to 0.0.0.0:5000.
EXPOSE 5000

# --- Command to Run the Application ---
# Use Gunicorn to run the app. 'app:app' means "in the file app.py,
# run the Flask instance named app".
# --bind 0.0.0.0:5000 makes it accessible from outside the container.
# --workers=4 is a good starting point for the number of concurrent processes.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers=4", "app:app"]