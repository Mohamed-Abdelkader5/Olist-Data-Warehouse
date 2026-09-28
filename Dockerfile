FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y \
        curl \
        gnupg \
        unixodbc \
        unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Add Microsoft package repository
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
    | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg

RUN curl https://packages.microsoft.com/config/debian/12/prod.list \
    > /etc/apt/sources.list.d/mssql-release.list

# Install Microsoft ODBC Driver
RUN apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Run ETL pipeline
CMD ["python", "-m", "main.main"]