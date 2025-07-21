cd base           && docker compose down && cd ..
cd minio          && docker compose down && cd ..

cd mod_admin      && docker compose down && cd ..
cd mod_downloader && docker compose down && cd ..
cd mod_watchdog   && docker compose down && cd ..

cd rabbitmq       && docker compose down && cd ..
cd sftp_servers   && docker compose down && cd ..
