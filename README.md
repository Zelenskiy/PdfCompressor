# Інструкція з використання PDF компресора

## Встановлення

Спочатку встановіть необхідні залежності:

```bash
# Для Linux
sudo apt-get install ghostscript poppler-utils
pip install pillow img2pdf

# Для MacOS
brew install ghostscript poppler
pip install pillow img2pdf

# Для Windows
pip install pillow img2pdf
# Ghostscript потрібно встановити окремо з офіційного сайту
```

## Як запустити

### Базове використання
```bash
python pdf_compressor.py scanned_document.pdf
```

### Із вказанням цільового розміру (12 МБ)
```bash
python pdf_compressor.py scanned_document.pdf -s 12
```

### Із вказанням вихідного файлу, методу стиснення
```bash
python pdf_compressor.py scanned_document.pdf -o compressed.pdf -m ghostscript
```

## Як це працює

1. **Скрипт відкриває PDF-файл** та оцінює його розмір
2. **Застосовує стиснення** використовуючи один із двох методів:
   - **Ghostscript** - швидкий і надійний метод для більшості документів
   - **Extract-compress** - витягує кожне зображення, стискає його та створює новий PDF
3. **Автоматично підбирає рівень якості**, якщо задано цільовий розмір
4. **Зберігає оптимізований PDF** із балансом між розміром і якістю

## Параметри командного рядка

| Параметр | Опис |
|----------|------|
| `input` | Шлях до вхідного PDF файлу |
| `-o, --output` | Шлях для збереження стисненого PDF |
| `-s, --size` | Цільовий розмір в МБ |
| `-m, --method` | Метод стиснення (`ghostscript` або `extract_compress`) |

Зазвичай зменшення з 48МБ до 12МБ можна досягти без суттєвої втрати якості для відсканованих документів.