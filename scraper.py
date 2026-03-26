import requests
from bs4 import BeautifulSoup
import json
import time

def get_player_sources(movie_url):
    """ဇာတ်ကားအတွင်းစာမျက်နှာထဲဝင်ပြီး Player Link များကို ရှာပေးရန်"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    players = {}
    try:
        response = requests.get(movie_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Dooplay Theme ရဲ့ Player Options တွေကို ရှာခြင်း
        options = soup.select('.dooplay_player .options ul li')
        
        for option in options:
            server_name = option.select_one('.title').text.strip() if option.select_one('.title') else ""
            # Player link ကို ယူဖို့အတွက် data-post, data-type, data-nump တွေကို သုံးလေ့ရှိပါတယ်
            # ဒါပေမဲ့ အလွယ်ဆုံးက iframe ထဲက src ကို ရှာတာပါ
            
            if "OK" in server_name.upper():
                players["OK"] = "Available" # ဒီနေရာမှာ link အစစ်ရဖို့ AJAX လိုအပ်တတ်ပါတယ်
            elif "720" in server_name:
                players["Mega_720"] = "Available"
            elif "1080" in server_name:
                players["Mega_1080"] = "Available"
            else:
                players[server_name.replace(" ", "_")] = "Available"
        
        return players
    except:
        return {}

def scrape_all_movies():
    base_url = "https://mmsubmovie.com/movies/page/"
    all_movies = []
    page_num = 1
    
    print("Scraping စတင်နေပါပြီ (Deep Scraping Mode)...")

    # စမ်းသပ်ကြည့်ရန် ပထမစာမျက်နှာ ၅ ခုကိုပဲ အရင်ပြထားပါတယ် (အကုန်လုံးဆိုရင် range ကို တိုးပေးပါ)
    # ဇာတ်ကားအကုန်လုံး ၃၀၀၀ လုံးအတွက်ဆိုရင် page_num < 150 လောက်ထိထားရပါမယ်
    while page_num <= 5: 
        url = f"{base_url}{page_num}/"
        print(f"စာမျက်နှာ {page_num} ကို ဖတ်နေသည်...")
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        if response.status_code != 200: break
            
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.select('article.item')
        if not items: break

        for item in items:
            title_elem = item.select_one('.data h3 a')
            if title_elem:
                title = title_elem.text.strip()
                link = title_elem['href']
                img = item.select_one('.poster img').get('src') or item.select_one('.poster img').get('data-src')
                
                print(f" - Data ယူနေသည်: {title}")
                
                # Player အမျိုးအစားများကို စစ်ဆေးခြင်း
                # မှတ်ချက်: ဒါက အချိန်ပိုကြာစေပါတယ်။ ၃၀၀၀ လုံးဆိုရင် GitHub Action limit ကို သတိထားရပါမယ်။
                player_options = get_player_sources(link)

                all_movies.append({
                    "title": title,
                    "image": img,
                    "link": link,
                    "players": player_options,
                    "rating": item.select_one('.rating').text.strip() if item.select_one('.rating') else "N/A"
                })
        
        page_num += 1
        time.sleep(1) # ဆာဗာကို ခဏနားပေးရန်

    with open('movies.json', 'w', encoding='utf-8') as f:
        json.dump(all_movies, f, ensure_ascii=False, indent=4)
    
    print(f"ပြီးဆုံးပါပြီ။ စုစုပေါင်း: {len(all_movies)}")

if __name__ == "__main__":
    scrape_all_movies()
