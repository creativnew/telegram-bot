# 🔒 Telegram Bot - Xavfsizlik Hujjati

## 📋 Xavfsizlik Xususiyatlari

Bu bot quyidagi xavfsizlik choralariga ega:

### 1. Environment Variable Protection
- **Bot token** va **ma'lumotlar** `.env` faylida saqlanadi
- Gitga kiritilmaydi (`.gitignore` orqali)
- Kodda hard-coded qilinmaydi

### 2. Rate Limiting
- Foydalanuvchi har daqiqada 30 ta so'rov yuborishi mumkin
- Har soatda 200 ta so'rov limiti
- Limitdan o'tganda xabar o'chiriladi

### 3. Input Validation
- Barcha foydalanuvchi kiritmalari tekshiriladi
- Telefon raqamlar validatsiya qilinadi
- User ID lar tekshiriladi
- Xavfli belgilar olib tashlanadi

### 4. Webhook Security
- Webhook endpoint signature validation
- HMAC-SHA256 bilan himoya
- Secret token orqali tekshiruv

### 5. Anti-Abuse System
- Shubhali faoliyat monitoringi
- Avtomatik blokirlash
- Security loglar

### 6. Database Security
- Sensitive ma'lumotlar hash qilinadi
- SQL injection himoyasi
- Parametrized queries

### 7. Anti-Clone Protection
- Machine ID tekshiruvi
- License validation
- Code integrity checks

## 🚀 O'rnatish

### 1. Environment Variables
`.env.example` faylini `.env` ga nusxalang va quyidagilarni to'ldiring:

```bash
BOT_TOKEN=your_bot_token_here
OWNER_ID=your_telegram_id
WEBHOOK_SECRET=your_random_secret_key
```

### 2. Dependencies
```bash
pip install -r requirements.txt
```

### 3. Botni ishga tushirish
```bash
python main.py
```

## 🔧 Sozlamalar

### Rate Limiting
`.env` faylida quyidagilarni o'zgartiring:
```bash
RATE_LIMIT_ENABLED=1
RATE_LIMIT_PER_MINUTE=30
RATE_LIMIT_PER_HOUR=200
```

### Webhook Secret
```bash
WEBHOOK_SECRET=your_very_long_random_secret_key_here
```

## 📊 Monitoring

### Security Logs
`security.log` faylida quyidagilar yoziladi:
- Webhook events
- Rate limit violations
- Invalid inputs
- Admin actions
- Banned user attempts

### Bot Logs
`bot.log` faylida barcha bot faoliyati yoziladi.

## ⚠️ Xavfsizlik Maslahatlari

1. **Bot tokenni hech kimga bermang**
2. **.env faylni Gitga qo'shmang**
3. **Webhook secretni kuchli qiling**
4. **Adminlarni ehtiyotkor qo'shing**
5. **Loglarni muntazam tekshiring**
6. **Botni yangilab turishni unutmang**

## 🛡️ Himoya Darajalari

### Level 1: Basic
- Environment variables
- Input validation
- Rate limiting

### Level 2: Advanced
- Webhook security
- Anti-abuse system
- Database hashing

### Level 3: Pro
- Anti-clone protection
- License validation
- Code obfuscation

## 📞 Yordam

Agar xavfsizlik muammolari bo'lsa:
1. Loglarni tekshiring
2. Environment variablesni tekshiring
3. Bot tokenni yangilang
4. @userinfobot orqali IDni tekshiring

---

**⚠️ Muhim:** Bu bot professional xavfsizlik choralariga ega. Lekin hech qachon 100% xavfsizlik bo'lmaydi. Doimo ehtiyot bo'ling!
