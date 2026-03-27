import requests
from bs4 import BeautifulSoup
import json
import time
import re

def get_best_player(movie_url):
    """ဇာတ်ကားအတွင်းစာမျက်နှာထဲဝင်ပြီး 1080p သို့မဟုတ် အကောင်းဆုံး Player ID ကို ရှာရန်"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        response = requests.get(movie_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # ၁။ Post ID ကို ရှာခြင်း (Dooplay Theme တွင် များသောအားဖြင့် id='player-option-1' စသဖြင့် ရှိတတ်သည်)
        # သို့မဟုတ် JavaScript ထဲက dooPlayer value ကို ရှာခြင်း
        post_id = ""
        scripts = soup.find_all('script')
        for s in scripts:
            if 'dooPlayer' in s.text:
                match = re.search(r'"post_id":"(\d+)"', s.text)
                if match:
                    post_id = match.group(1)
                    break
        
        # ၂။ Player Options များထဲမှ 1080p သို့မဟုတ် အကောင်းဆုံးနံပါတ်ကို ရှာခြင်း
        best_nump = "1" # Default က နံပါတ် ၁
        options = soup.select('.dooplay_player .options ul li')
        
        for option in options:
            title = option.select_one('.title').text.strip().upper() if option.select_one('.title') else ""
            nump = option.get('data-nump')
            
            # 1080p ပါတာကို အရင်ရှာမယ်
            if "1080" in title:
                best_nump = nump
                break
            # 1080 မရှိရင် 720p ကို ယူမယ်
            elif "720" in title:
                best_nump = nump
        
        return {"post_id": post_id, "nump": best_nump}
    except:
        return {"post_id": "", "nump": "1"}

def scrape_all_movies():
    base_url = "https://mmsubmovie.com/movies/page/"
    all_movies = []
    page_num = 1
    
    print("ဇာတ်ကားအားလုံးကို Deep Scraping စတင်နေပါပြီ (ဒီအဆင့်သည် အချိန်ကြာမြင့်နိုင်ပါသည်)...")

    while True: 
        url = f"{base_url}{page_num}/"
        print(f"စာမျက်နှာ {page_num} ကို ဖတ်နေသည်...")
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=15)
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
                    
                    # တစ်ကားချင်းစီထဲဝင်ပြီး Player Data ယူခြင်း
                    player_data = get_best_player(link)

                    all_movies.append({
                        "title": title,
                        "image": img,
                        "link": link,
                        "post_id": player_data["post_id"],
                        "nump": player_data["nump"],
                        "rating": item.select_one('.rating').text.strip() if item.select_one('.rating') else "N/A"
                    })

            # Pagination Check
            if not soup.select_one('.pagination .next') and page_num > 5: break
            
            page_num += 1
            time.sleep(0.5)

        except Exception as e:
            print(f"Error: {e}")
            break

    with open('movies.json', 'w', encoding='utf-8') as f:
        json.dump(all_movies, f, ensure_ascii=False, indent=4)
    
    print(f"ပြီးဆုံးပါပြီ။ စုစုပေါင်း: {len(all_movies)}")

if __name__ == "__main__":
    scrape_all_movies()
