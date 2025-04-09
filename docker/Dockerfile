FROM mcr.microsoft.com/mssql/server:2019-latest

# Passer en utilisateur root pour installer mssql-tools
USER root
RUN apt-get update && \
    apt-get install -y mssql-tools unixodbc-dev && \
    ln -s /opt/mssql-tools/bin/sqlcmd /usr/local/bin/sqlcmd && \
    ln -s /opt/mssql-tools/bin/bcp /usr/local/bin/bcp

# Revenir à l’utilisateur non-root
USER mssql

# Variables d'environnement pour SQL Server
ENV ACCEPT_EULA=Y
ENV SA_PASSWORD=Your$tr0ngP@ssw0rd!
ENV MSSQL_PID=Express

# Copier le script d'initialisation dans l'image
COPY init.sql /init.sql

# Démarrage du serveur SQL et exécution du script d'initialisation
CMD /bin/bash -c "/opt/mssql/bin/sqlservr & pid=\$!; \
    sleep 30; \
    sqlcmd -S localhost -U SA -P \"$SA_PASSWORD\" -i /init.sql; \
    wait \$pid"
