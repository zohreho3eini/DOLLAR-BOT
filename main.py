import requests
from bs4 import BeautifulSoup
import os
import sys
import jdatetime
import pytz
import time

# ================= تنظیمات اولیه =================

# 1. دریافت توکن و آیدی شخصی از تنظیمات محرمانه گیت‌هاب
BOT_TOKEN = os.environ.get('BOT_TOKEN')
MY_PERSONAL_ID = os.environ.get('CHAT_ID')

# 2. 👇 آیدی کانال خود را دقیقاً اینجا وارد کنید 👇
# مثال: CHANNEL_ID = "@MyNewsChannel" یا CHANNEL_ID = "-100123456"
CHANNEL_ID = "@informationbrc"  

# 3. لیست هوشمند گیرندگان (حذف تکراری‌ها برای جلوگیری از ارسال دو باره)
RECIPIENTS = []
raw_list = [MY_PERSONAL_ID, CHANNEL_ID]

for user in raw_list:
    # شرط‌ها: آیدی خالی نباشد + قبلاً اضافه نشده باشد + متن پیش‌فرض نباشد
    if user and user not in RECIPIENTS and user != "@informationbrc":
        RECIPIENTS.append(user)

# لیست مواردی که باید قیمت گرفته شود
ITEMS = [
    ("دلار آمریکا", "price_dollar_rl"),
    ("دلار کانادا", "price_cad"),
    ("یورو", "price_eur"),
    ("پوند انگلیس", "price_gbp"),
    ("درهم امارات", "price_aed"),
    ("یوآن چین", "price_cny"),
    ("لیر ترکیه", "price_try"),
    ("سکه امامی", "retail_sekee"),
    ("اونس طلا", "ons"),
    ("نیم سکه", "retail_nim"),
    ("ربع سکه", "retail_rob"),
    ("هر گرم طلای 18", "geram18"),
    ("مثقال طلا", "mesghal")
]

# ================= توابع برنامه =================

def send_telegram_message(text):
    """پیام را به تمام افراد لیست RECIPIENTS می‌فرستد"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    if not RECIPIENTS:
        print("⚠️ لیست گیرندگان خالی است! (آیدی کانال یا Secret را چک کنید)")
        return

    for chat_id in RECIPIENTS:
        try:
            payload = {"chat_id": chat_id, "text": text}
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                print(f"✅ پیام ارسال شد به: {chat_id}")
            else:
                print(f"❌ خطا در ارسال به {chat_id}: {response.text}")
        except Exception as e:
            print(f"❌ مشکل ارتباطی با {chat_id}: {e}")

def get_price(slug):
    """دریافت قیمت از سایت TGJU"""
    url = f"https://www.tgju.org/profile/{slug}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # تلاش اول برای پیدا کردن قیمت
            price_tag = soup.find('span', {'data-col': 'info.last_price.PDrCotVal'})
            
            # تلاش دوم (اگر کلاس متفاوت بود)
            if not price_tag:
                price_tag = soup.select_one('.price')
                
            if price_tag:
                return price_tag.text.strip()
    except Exception as e:
        print(f"خطا در دریافت {slug}: {e}")
        pass
    
    return "---"

def get_persian_date():
    """تولید تاریخ و ساعت شمسی با فرمت درخواستی"""
    try:
        tz = pytz.timezone('Asia/Tehran')
        now = jdatetime.datetime.now(tz)
        
        weekdays = {
            0: 'شنبه', 1: 'یکشنبه', 2: 'دوشنبه', 3: 'سه شنبه',
            4: 'چهارشنبه', 5: 'پنج شنبه', 6: 'جمعه'
        }
        months = {
            1: 'فروردین', 2: 'اردیبهشت', 3: 'خرداد', 4: 'تیر',
            5: 'مرداد', 6: 'شهریور', 7: 'مهر', 8: 'آبان',
            9: 'آذر', 10: 'دی', 11: 'بهمن', 12: 'اسفند'
        }
        
        day_name = weekdays[now.weekday()]
        month_name = months[now.month]
        
        # خروجی: 15:00 سه شنبه 16 دی 1404
        return f"{now.strftime('%H:%M')} {day_name} {now.day} {month_name} {now.year}"
    except:
        return "تاریخ نامشخص"

# ================= شروع اجرا =================

if __name__ == "__main__":
    # چک کردن توکن
    if not BOT_TOKEN:
        print("🔴 خطا: توکن ربات (BOT_TOKEN) تنظیم نشده است!")
        sys.exit(1)

    print("⏳ در حال دریافت قیمت‌ها...")
    message_lines = []
    
    # حلقه دریافت قیمت‌ها
    for name, slug in ITEMS:
        price = get_price(slug)
        line = f"🔸{name} : {price}"
        message_lines.append(line)
        # مکث کوتاه برای جلوگیری از مسدود شدن توسط سایت
        time.sleep(0.5)

    # افزودن تاریخ و ساعت
    date_str = get_persian_date()
    final_message = "\n".join(message_lines) + f"\n\n\n{date_str}"
    
    # ارسال نهایی
    send_telegram_message(final_message)
