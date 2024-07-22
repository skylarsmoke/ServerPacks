FROM python:3.9

ADD SynergyBassServer.py .
ADD KeyGen.py .
ADD SynergyLicenseKey.db .

# Install Cloud SQL Auth Proxy
RUN wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O /cloud_sql_proxy && \
    chmod +x /cloud_sql_proxy

RUN pip install pycryptodome
RUN pip install cryptography
RUN pip install pyodbc
RUN pip install sendgrid
RUN pip install google-auth
RUN pip install google-auth-oauthlib
RUN pip install google-auth-httplib2
RUN pip install sqlalchemy
RUN pip install google-cloud
RUN pip install pymysql
RUN pip install "cloud-sql-python-connector[pytds]"

RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    libpq-dev \
    build-essential \
    curl \
    apt-transport-https \
    gnupg \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

CMD /cloud_sql_proxy -instances="synergybassserver:us-central1:synergy-bass-licenses"=tcp:1433 & python SynergyBassServer.py