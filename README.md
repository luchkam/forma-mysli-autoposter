# ФОРМА МЫСЛИ — автопостер для Telegram

## 1) Настройка
- Создай бота в @BotFather, добавь админом в @forma_mysli.
- Скопируй репозиторий, создай .env по .env.example.
- Локально: `pip install -r requirements.txt` и `python -m app.run` (или `python app/run.py`).

## 2) Render (Cron Job)
- New → Cron Job → GitHub repo.
- Command:
  python -m pip install -r requirements.txt && python -m app.run
- Schedule (UTC):
  - 09:00 UTC (= 12:00 MSK)
  - 16:00 UTC (= 19:00 MSK)
- Env vars: TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, OPENAI_API_KEY, OCR=on/off, POSTS_PER_RUN=1.

## 3) Ручной резерв
- Сложи в /manual_inbox:
  - example.jpg
  - example_en.txt
- При следующем запуске скрипт инвертирует картинку, переведёт подпись и запостит.

## Примечания
- Если snscrape не вернёт посты, в логах будет ошибка — в этом случае работай через manual_inbox или повтори запуск.
- OCR можно отключить (OCR=off), если ресурс ограничен.
