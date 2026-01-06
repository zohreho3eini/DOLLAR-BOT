import requests
from bs4 import BeautifulSoup
import os
import sys

# 1. دریافت اطلاعات محرمانه از تنظیمات گیت‌هاب
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# آدرس سایت قیمت دلار
URL = 'https://www.tgju.org/profile/price_dollar_rl'

def send_telegram_message(text):
    """ارسال پیام به تلگرام"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("✅ پیام با موفقیت به تلگرام ارسال شد.")
        else:
            print(f"❌ خطا در ارسال پیام: {response.text}")
    except Exception as e:
        print(f"❌ خطا در ارتباط با تلگرام: {e}")

def get_price():
    """دریافت قیمت از سایت"""
    try:
        # هدر برای اینکه سایت ما را ربات تشخیص ندهد
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print("⏳ در حال دریافت قیمت از سایت...")
        response = requests.get(URL, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # روش اول پیدا کردن قیمت (مخصوص سایت tgju)
            price_tag = soup.find('span', {'data-col': 'info.last_price.PDrCotVal'})
            
            # اگر روش اول جواب نداد، روش دوم (کلاس price)
            if not price_tag:
                price_tag = soup.select_one('.price')

            if price_tag:
                clean_price = price_tag.text.strip()
                print(f"💰 قیمت پیدا شد: {clean_price}")
                return clean_price
            else:
                return "پیدا نشد (تغییر ساختار سایت)"
        else:
            return f"خطای سایت (کد {response.status_code})"
            
    except Exception as e:
        return f"خطای برنامه: {str(e)}"

# شروع برنامه
if __name__ == "__main__":
    # چک کردن اینکه توکن‌ها وجود داشته باشند
    if not BOT_TOKEN or not CHAT_ID:
        print("🔴 خطا: توکن ربات یا چت آیدی در Secrets تنظیم نشده است!")
        sys.exit(1) # خروج با خطا

    # دریافت قیمت
    current_price = get_price()
    
    # ساختن متن پیام
    message = f"📢 گزارش خودکار قیمت دلار:\n\n💵 قیمت: {current_price} ریال\n\n🤖 ربات شما"
    
    # ارسال
    send_telegram_message(message)
