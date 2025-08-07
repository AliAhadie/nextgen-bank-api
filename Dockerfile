# base image
FROM  python:3.12-alpine

LABEL maintainer="ali.ahadi.official@gmail.com"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

COPY /app /app/

# Install the dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user


USER django-user        


