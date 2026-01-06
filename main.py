import requests
from bs4 import BeautifulSoup
import os
import sys
import jdatetime
import pytz
import time

# دریافت توکن و آیدی شخصی از تنظیمات گیت‌هاب
BOT_TOKEN = os.environ.get('BOT_TOKEN')
MY_PERSONAL_ID = os.environ.get('CHAT_ID')

# 👇👇👇 آیدی کانال خود را اینجا وارد کنید 👇👇👇
# مثال: CHANNEL_ID = "@MyChannel"  یا  CHANNEL_ID = "-100123456789"
CHANNEL_ID = "@informationbrc"

# لیست گیرندگان (هم شما، هم کانال)
RECIPIENTS = [MY_PERSONAL_ID, CHANNEL_ID]

# لیست مواردی که می‌خواهید (نام فارسی + شناسه سایت TGJU)
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

def send_telegram_message(text):
    """پیام را برای تمام افراد لیست گیرندگان می‌فرستد"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    for chat_id in RECIPIENTS:
        # چک می‌کنیم که آیدی خالی نباشد (مثلا اگر آیدی کانال را ننویسید ارور ندهد)
        if chat_id and chat_id != "@informationbrc": 
            try:
                payload = {"chat_id": chat_id, "text": text}
                requests.post(url, json=payload)
                print(f"✅ پیام ارسال شد به: {chat_id}")
            except Exception as e:
                print(f"❌ خطا در ارسال به {chat_id}: {e}")
        else:
            if chat_id == "@informationbrc":
                print("⚠️ هشدار: آیدی کانال را در کد تغییر نداده‌اید!")

def get_price(slug):
    """قیمت یک مورد خاص را از سایت می‌گیرد"""
    url = f"https://www.tgju.org/profile/{slug}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # پیدا کردن قیمت
            price_tag = soup.find('span', {'data-col': 'info.last_price.PDrCotVal'})
            if not price_tag:
                price_tag = soup.select_one('.price')
                
            if price_tag:
                return price_tag.text.strip()
    except:
        pass
    return "---"

def get_persian_date():
    """تاریخ و ساعت شمسی دقیق"""
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
    
    return f"{now.strftime('%H:%M')} {day_name} {now.day} {month_name} {now.year}"

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("توکن ربات تنظیم نشده است!")
        sys.exit(1)

    message_lines = []
    
    # حلقه برای گرفتن قیمت تک تک موارد
    for name, slug in ITEMS:
        price = get_price(slug)
        line = f"🔸{name} : {price}"
        message_lines.append(line)
        time.sleep(0.5)

    # اضافه کردن تاریخ و ساعت در آخر پیام
    date_str = get_persian_date()
    final_message = "\n".join(message_lines) + f"\n\n\n{date_str}"
    
    send_telegram_message(final_message)
