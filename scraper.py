import requests
from bs4 import BeautifulSoup
import json
import time

def scrape_all_movies():
    base_url = "https://mmsubmovie.com/movies/page/"
    all_movies = []
    page_num = 1
    
    print("Scraping စတင်နေပါပြီ...")

    while True:
        url = f"{base_url}{page_num}/"
        print(f"စာမျက်နှာ {page_num} ကို ဖတ်နေသည်: {url}")
        
        try:
            # Website ကို ပုံမှန် Browser လိုမျိုး User-Agent ထည့်ပြီး တောင်းဆိုခြင်း
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                print(f"စာမျက်နှာကုန်သွားပြီ သို့မဟုတ် Error တက်နေသည် (Status: {response.status_code})")
                break
                
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select('article.item')

            # ဇာတ်ကားမရှိတော့ရင် ရပ်မယ်
            if not items:
                print("ထပ်မံတွေ့ရှိသော ဇာတ်ကားမရှိတော့ပါ။")
                break

            for item in items:
                try:
                    title_elem = item.select_one('.data h3 a')
                    img_elem = item.select_one('.poster img')
                    
                    if title_elem:
                        title = title_elem.text.strip()
                        link = title_elem['href']
                        # Image link ကို fix လုပ်ခြင်း (Lazy load သုံးထားရင် data-src ကို ယူရတတ်တယ်)
                        img = img_elem.get('src') or img_elem.get('data-src')
                        rating = item.select_one('.rating').text.strip() if item.select_one('.rating') else "N/A"
                        quality = item.select_one('.quality').text.strip() if item.select_one('.quality') else "HD"
                        year = item.select_one('.data span').text.strip() if item.select_one('.data span') else ""

                        all_movies.append({
                            "title": title,
                            "link": link,
                            "image": img,
                            "rating": rating,
                            "quality": quality,
                            "year": year
                        })
                except Exception as e:
                    print(f"Item တစ်ခုဆွဲရာတွင် Error တက်သည်: {e}")
                    continue

            # စာမျက်နှာ တစ်ခုပြီးတိုင်း ၁ စက္ကန့် နားမယ် (Block မခံရစေရန်)
            time.sleep(1)
            page_num += 1

        except Exception as e:
            print(f"စာမျက်နှာ {page_num} မှာ Error ဖြစ်ပေါ်သည်: {e}")
            break

    # ရလာတဲ့ Data အားလုံးကို JSON အဖြစ်သိမ်းမယ်
    with open('movies.json', 'w', encoding='utf-8') as f:
        json.dump(all_movies, f, ensure_ascii=False, indent=4)
    
    print(f"စုစုပေါင်း ဇာတ်ကားအရေအတွက် {len(all_movies)} ကို movies.json ထဲတွင် သိမ်းဆည်းပြီးပါပြီ။")

if __name__ == "__main__":
    scrape_all_movies()
