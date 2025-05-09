# KontekstnoHack — Desktop приложение

Удобный GUI-клиент для автоматического угадывания секретного слова на контекстно.рф.

---

## 🚀 Быстрый старт

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/alpin0s/KontekstnoHack.git
   cd KontekstnoHack

Установите зависимости:
pip install -r requirements.txt

Запустите приложение:
python gui.py


🎮Как получить ID:

Обычный (random) режим

Откройте в браузере https://контекстно.рф/random

Нажмите F12 → вкладка Network → фильтр XHR.

Введите в поле любое слово и нажмите Enter.

В списке запросов найдите запрос типа get_random_challenge?user_id=… (или get_score → get_tip).

Во вкладке Response скопируйте значение поля "id": "ВАШ_CHALLENGE_ID".

Режим «вечеринки» (party mode)

Перейдите по ссылке, например:
https://контекстно.рф/room/(тут id)

Скопируйте часть URL после /room/ — это и есть ваш Room ID.

