# Basic Django Template

## Ishga tushirish

### 1. Virtual muhit yaratish va faollashtirish

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Kutubxonalarni o‘rnatish
```bash
pip install -r requirements.txt
```

### 3. `.env` faylini yaratish  
Loyihada `.env-example` fayl mavjud. Shu fayldan nusxa olib `.env` fayl yarating:
```bash
cp .env-example .env
```
Agar Windows ishlatayotgan bo‘lsangiz:
```bash
copy .env-example .env
```
So‘ng `.env` fayldagi qiymatlarni o‘zingizga moslab tahrirlang.

### 4. Ma’lumotlar bazasini yaratish
```bash
python manage.py migrate
```

### 5. Serverni ishga tushurish
```bash
python manage.py runserver
```

Brauzerda oching:  
👉 [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
