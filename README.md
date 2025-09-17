Описание:
Backend для системы задач, реализованный на FastAPI. Программа поддерживает аутентификацию пользователей через JWT-токены, работу с Redis для хранения данных (ttl 60 сек) и обмена сообщениями через pub/sub.

/login: получение JWT-токена для аутентификации
/write: запись данных в Redis и публикация в канал
/read: чтение данных из Redis
/longpoll: long polling для ожидания новых сообщений из канала (таймаут 120 сек)
/metrics: prometheus-метрики

Требования:
Python
FastAPI, Uvicorn, PyJWT, redis.asyncio, prometheus-fastapi-instrumentator (см. requirements.txt)
Redis-сервер
Конфигурация в config.ini

Запуск:
1. Установите WSL и Redis
2. Установите зависимости (requirements.txt)
3. Настройте конфигурацию (config.ini)
4. Запустите сервер (python main.py)

Тест /login (получение токена):
$body = "username=user&password=pass"
$response = Invoke-WebRequest -Uri http://localhost:8080/login -Method POST -Body $body -ContentType "application/x-www-form-urlencoded" -ErrorAction Stop
$token = ($response.Content | ConvertFrom-Json).access_token
Write-Output $token

Тест /write (запись данных):
$response = Invoke-WebRequest -Uri http://localhost:8080/write -Method POST -Body '{"data": "Test Data"}' -Headers @{"Authorization"="Bearer $token"; "Content-Type"="application/json"} -ErrorAction Stop
Write-Output $response.StatusCode
Write-Output $response.Content

Тест /read (чтение данных):
$response = Invoke-WebRequest -Uri http://localhost:8080/read -Method GET -Headers @{"Authorization"="Bearer $token"} -ErrorAction Stop
Write-Output $response.StatusCode
Write-Output $response.Content

Тест /longpoll:
Окно 1:
$response = Invoke-WebRequest -Uri http://localhost:8080/longpoll -Method GET -Headers @{"Authorization"="Bearer $token"} -ErrorAction Stop
Write-Output $response.StatusCode
Write-Output $response.Content
Окно 2(в течение 120 сек):
$response = Invoke-WebRequest -Uri http://localhost:8080/write -Method POST -Body '{"data": "Hello"}' -Headers @{"Authorization"="Bearer $token"; "Content-Type"="application/json"} -ErrorAction Stop
Write-Output $response.StatusCode
Write-Output $response.Content

Тест /metrics:
$response = Invoke-WebRequest -Uri http://localhost:8080/metrics -Method GET -ErrorAction Stop
Write-Output $response.StatusCode
Write-Output $response.Content



Автор: despicable21
