#!/bin/bash

set -e

PROJECT_DIR=$(pwd)
PROJECT_NAME=$(basename "$PROJECT_DIR")
SERVICE_NAME="tg-bot-$PROJECT_NAME"

echo "=== Старт автоматического деплоя бота: $PROJECT_NAME ==="

echo "Инициализация окружения..."
sudo apt update -y
sudo apt install python3 python3-pip python3-venv -y

if [ ! -d ".venv" ]; then
    echo "Создание виртуального окружения .venv..."
    python3 -m venv .venv
fi

echo "Установка зависимостей..."
source .venv/bin/activate
pip install --upgrade pip
pip install aiogram

echo "Создание системного сервиса $SERVICE_NAME..."
sudo bash -c "cat > /etc/systemd/system/$SERVICE_NAME.service <<EOF
[Unit]
Description=Telegram Bot - $PROJECT_NAME
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/.venv/bin/python3 $PROJECT_DIR/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF"

echo "Запуск и активация службы..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

echo "=== Деплой успешно завершен! ==="
echo "Проверить статус бота: sudo systemctl status $SERVICE_NAME"
echo "Посмотреть логи: sudo journalctl -u $SERVICE_NAME -f"