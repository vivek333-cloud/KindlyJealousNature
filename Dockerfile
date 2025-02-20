# Use a Python base image
FROM python:3.9  

# Set the working directory
WORKDIR /app  

# Copy project files
COPY . .  

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt  

# Expose the port Flask runs on
EXPOSE 5000  

# Run the application
CMD ["gunicorn", "-b", "0.0.0.0:8080", "main:app"]