FROM apache/airflow:3.3.1

USER root

# System dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        gnupg \
        unixodbc \
        unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Microsoft repository
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
    | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg

RUN curl https://packages.microsoft.com/config/debian/12/prod.list \
    > /etc/apt/sources.list.d/mssql-release.list

# Microsoft ODBC Driver 17
RUN apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql17 \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Python packages needed by the DW project
RUN pip install --no-cache-dir \
    pandas \
    PyYAML \
    SQLAlchemy \
    pyodbc