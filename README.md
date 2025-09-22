# Color Studio - Конвертер цветовых моделей

Интерактивный конвертер цветов между моделями CMYK ↔ RGB ↔ HLS с графическим интерфейсом.

## Установка и запуск

### Вариант 1: Готовый EXE (Windows)
1. Скачайте `ColorStudio.exe` из папки `dist/`
2. Запустите файл

### Вариант 2: Исходный код
```bash
git clone https://github.com/ваш-логин/color-studio.git
cd color-studio
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python color_converter.py