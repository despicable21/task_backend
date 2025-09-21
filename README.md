## Описание
Backend для системы задач, реализованный на FastAPI. Программа поддерживает аутентификацию пользователей через JWT-токены, работу с Redis для хранения данных (ttl 60 сек) и обмена сообщениями через pub/sub.


- `/login`: получение JWT-токена для аутентификации.
- `/write`: запись данных в Redis и публикация в канал.
- `/read`: чтение данных из Redis.
- `/longpoll`: long polling для ожидания новых сообщений из канала (таймаут 120 сек).
- `/metrics`: prometheus-метрики.

## Требования
- **Python**
- Зависимости (см. `requirements.txt`)
- Redis-сервер
- Конфигурация в файле `settings.py`

## Запуск
1. Установите WSL и Redis.
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
3. Настройте конфигурацию
4. Запустите сервер 
	```bash
 	python main.py

## Тест /login (получение токена):
	```bash
	$login = Invoke-RestMethod -Uri "http://127.0.0.1:8080/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body "username=admin&password=any"
 	$token = $login.access_token
	$token
 
## Тест /write (запись данных):
	```bash
	$body = @{ data = "task 1" } | ConvertTo-Json
 	Invoke-RestMethod -Uri "http://127.0.0.1:8080/write" -Method Post -Headers @{ Authorization = "Bearer $token" } -ContentType "application/json" -Body $body
	
## Тест /read (чтение данных):
	```bash
	Invoke-RestMethod -Uri "http://127.0.0.1:8080/read" -Headers @{ Authorization = "Bearer $token" }

## Тест /longpoll:
#### Окно 1:
	```bash
	Invoke-RestMethod -Uri "http://127.0.0.1:8080/longpoll" -Headers @{ Authorization = "Bearer $token" }
 
#### Окно 2(в течение 120 сек):
	```bash
	$body2 = @{ data = "longpoll task" } | ConvertTo-Json
 	Invoke-RestMethod -Uri "http://127.0.0.1:8080/write" -Method Post -Headers @{ Authorization = "Bearer $token" } -ContentType "application/json" -Body $body2

## Тест /metrics:
	```bash
	$response = Invoke-WebRequest -Uri http://localhost:8080/metrics -Method GET -ErrorAction Stop
	Write-Output $response.StatusCode
	Write-Output $response.Content



Автор: despicable21
