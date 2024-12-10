# Gunakan image resmi Python versi 3.9
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    APP_HOME=/app

# Buat direktori kerja aplikasi
WORKDIR $APP_HOME

# Copy file requirements.txt ke dalam container
COPY requirements.txt .

# Install dependencies
RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy seluruh source code ke dalam container
COPY . .

# Ekspos port 5000 (port default Flask)
EXPOSE 8081

# Jalankan aplikasi Flask
CMD ["python", "app.py"]
