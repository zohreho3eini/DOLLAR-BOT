import requests
from bs4 import BeautifulSoup
import os
import sys

# تنظیمات (این‌ها را از متغیرهای محیطی می‌خوانیم تا امن باشد)
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# آدرس سایتی که می‌خواهید قیمت را از آن بردارید
URL = 'https://www.tgju.org/profile/price_dollar_rl'

def send_telegram_message(message):
    send_url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    requests.post(send_url, data=payload)

def get_dollar_price():
    try:
        # درخواست به سایت
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(URL, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # پیدا کردن قیمت (این قسمت بسته به سایت هدف باید تغییر کند)
            # در سایت TGJU معمولا قیمت در کلاسی به نام value قرار دارد
            price_tag = soup.find('span', {'data-col': 'info.last_price.PDrCotVal'})
            
            if price_tag:
                return price_tag.text.strip()
            else:
                # تلاش دوم برای پیدا کردن قیمت اگر روش اول کار نکرد
                current_price = soup.select_one('.price')
                return current_price.text.strip() if current_price else "پیدا نشد"
        else:
            return "خطا در اتصال به سایت"
            
    except Exception as e:
        return f"خطا: {str(e)}"

if __name__ == "__main__":
    if not BOT_TOKEN or not CHAT_ID:
        print("توکن یا چت آیدی تنظیم نشده است")
        sys.exit(1)
        
    price = get_dollar_price()
    message = f"💵 قیمت دلار امروز:\n{price} ریال"
    
    send_telegram_message(message)
    print("پیام ارسال شد.")
