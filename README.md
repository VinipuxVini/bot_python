# Telegram Bot на Aiogram

## Структура проекта
```
├── bot/
│   ├── __init__.py
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── admin.py
│   ├── keyboards/
│   │   ├── __init__.py
│   │   └── reply.py
│   ├── middlewares/
│   │   ├── __init__.py
│   │   └── throttling.py
│   ├── filters/
│   │   ├── __init__.py
│   │   └── role.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── database.py
│   └── utils/
│       ├── __init__.py
│       └── misc.py
├── config/
│   ├── __init__.py
│   └── config.py
├── .env
├── .env.example
├── requirements.txt
└── main.py
```

## Установка и запуск

1. Создайте виртуальное окружение:
```bash
python -m venv venv
```

2. Активируйте виртуальное окружение:
- Windows:
```bash
.\venv\Scripts\activate
```
- Linux/MacOS:
```bash
source venv/bin/activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл .env на основе .env.example и заполните необходимые переменные окружения

5. Запустите бота:
```bash
python main.py
```

## Основные компоненты

- `handlers/` - обработчики сообщений и команд
- `keyboards/` - клавиатуры и кнопки
- `middlewares/` - промежуточные обработчики
- `filters/` - пользовательские фильтры
- `services/` - сервисы для работы с базой данных и внешними API
- `utils/` - вспомогательные функции
- `config/` - конфигурация проекта 