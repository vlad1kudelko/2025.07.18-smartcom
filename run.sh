cd base         && docker compose down && docker compose up --build -d && cd ..
cd minio        && docker compose down && docker compose up --build -d && cd ..

cd mod_admin    && docker compose down && docker compose up --build -d && cd ..
cd mod_watchdog && docker compose down && docker compose up --build -d && cd ..

cd rabbitmq     && docker compose down && docker compose up --build -d && cd ..
cd sftp_servers && docker compose down && docker compose up --build -d && cd ..