FROM postgres:16
RUN apt-get update && apt-get install postgresql-16-wal2json
RUN rm -rf /var/lib/apt/lists/*
CMD [ "postgres" ,"-c", "wal_level=logical" ]