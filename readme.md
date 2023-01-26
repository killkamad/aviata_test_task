# Aviata.kz test task

## Инструкция для запуска.

1. Настройка виртуального окружения

   1.1 Создать и активировать виртуальное окружение

    ```bash
   # Windows:
    python -m venv venv
   .\venv\Scripts\activate
   
   # Linux:
   virtualenv -p python3 venv
   source venv/bin/activate
    ```
   1.2 Установка необходимых библиотек

    ```bash
    pip install -r requirements.txt
    ```

2. Установить и запустить Redis сервер

   ```bash
   # Windows 
   Установить "Redis 5.0.10 for Windows" с github используя msi
   
   # Linux
   sudo apt install redis-server
    ```

3. Для запуска микросервисов:

   ```bash
    Перейти во все папки с сервисами и запустить команды:
    python -m uvicorn provider_a.asgi:application --port 9001 --reload
    python -m uvicorn provider_b.asgi:application --port 9002 --reload
    python -m uvicorn airflow.asgi:application --port 9003 --reload
    ```

4. Для удобства все API запросы собраны в файле Insomnia.json
   
   ```bash
    4.1 Нужно установить программу Insomnia
    4.2 Импортировать из файла Insomnia.json
    ```
   
