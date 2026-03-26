import requests
from bs4 import BeautifulSoup
import json
import time

def get_player_sources(movie_url):
    """ဇာတ်ကားအတွင်းစာမျက်နှာထဲဝင်ပြီး Player အမျိုးအစားများကို ရှာရန်"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    players = []
    try:
        response = requests.get(movie_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Player options များကို ရှာခြင်း
        options = soup.select('.dooplay_player .options ul li')
        for option in options:
            server_name = option.select_one('.title').text.strip() if option.select_one('.title') else ""
            if server_name:
                players.append(server_name)
        return players
    except:
        return []

def scrape_all_movies():
    base_url = "https://mmsubmovie.com/movies/page/"
    all_movies = []
    page_num = 1
    
    print("ဇာတ်ကားအားလုံး (၃၀၀၀ နီးပါး) ကို စတင်ဆွဲယူနေပါပြီ...")

    # ဒီနေရာမှာ ကန့်သတ်ချက်မထားဘဲ အကုန်ဆွဲပါမယ်
    while True: 
        url = f"{base_url}{page_num}/"
        print(f"စာမျက်နှာ {page_num} ကို ဖတ်နေသည်...")
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                print("နောက်ထပ်စာမျက်နှာ မရှိတော့ပါ။")
                break
                
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select('article.item')
            
            if not items:
                break

            for item in items:
                title_elem = item.select_one('.data h3 a')
                if title_elem:
                    title = title_elem.text.strip()
                    link = title_elem['href']
                    img_elem = item.select_one('.poster img')
                    img = img_elem.get('src') or img_elem.get('data-src')
                    
                    # ဇာတ်ကားအသေးစိတ်ထဲဝင်ပြီး Player တွေကြည့်မည့်အပိုင်း (အချိန်ကြာနိုင်သည်)
                    # player_info = get_player_sources(link) # Player ပါယူချင်ရင် ဒါကို ဖွင့်ပါ

                    all_movies.append({
                        "title": title,
                        "image": img,
                        "link": link,
                        "rating": item.select_one('.rating').text.strip() if item.select_one('.rating') else "N/A",
                        "quality": item.select_one('.quality').text.strip() if item.select_one('.quality') else "HD",
                        "year": item.select_one('.data span').text.strip() if item.select_one('.data span') else ""
                    })

            # စာမျက်နှာကုန်၊ မကုန် စစ်ဆေးခြင်း (Next Page ခလုတ်ရှိမရှိကြည့်ခြင်း)
            next_page = soup.select_one('.pagination .next')
            if not next_page and page_num > 10: # စာမျက်နှာ ၁၀ ကျော်မှ next မရှိရင် ရပ်မယ်
                break

            page_num += 1
            # Website က block မလုပ်အောင် ခဏနားမယ်
            time.sleep(0.5)

        except Exception as e:
            print(f"Error: {e}")
            break

    # JSON သိမ်းဆည်းခြင်း
    with open('movies.json', 'w', encoding='utf-8') as f:
        json.dump(all_movies, f, ensure_ascii=False, indent=4)
    
    print(f"ပြီးဆုံးပါပြီ။ စုစုပေါင်းဇာတ်ကား {len(all_movies)} ကား ရရှိခဲ့ပါတယ်။")

if __name__ == "__main__":
    scrape_all_movies()
