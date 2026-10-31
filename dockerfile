# Use a lightweight Python image for the runtime
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install uv for fast package installation
RUN pip install uv

# Copy requirements file first to leverage Docker layer caching
COPY requirements.txt ./

# Install dependencies system-wide using uv and cache downloaded packages
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app

# Expose the port the app will run on (matching main.py port 8080)
EXPOSE 8080

# Use uvicorn to run the FastAPI app defined in main.py
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]