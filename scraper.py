import requests
from bs4 import BeautifulSoup
import json
import time
import re

def get_direct_video_link(movie_url):
    """ဇာတ်ကား link ထဲဝင်ပြီး အကောင်းဆုံး embed link ကို တိုက်ရိုက်ဆွဲထုတ်ရန်"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    try:
        # ၁။ ဇာတ်ကား Detail Page ကို အရင်ဖတ်ပြီး post_id ရှာမယ်
        res = requests.get(movie_url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        post_id = ""
        scripts = soup.find_all('script')
        for s in scripts:
            if 'dooPlayer' in s.text:
                match = re.search(r'"post_id":"(\d+)"', s.text)
                if match:
                    post_id = match.group(1)
                    break
        
        if not post_id:
            return ""

        # ၂။ ၁၀၈၀p (သို့မဟုတ်) အကောင်းဆုံး server နံပါတ် (nump) ကို ရှာမယ်
        best_nump = "1"
        options = soup.select('.dooplay_player .options ul li')
        for option in options:
            title = option.select_one('.title').text.strip().upper() if option.select_one('.title') else ""
            if "1080" in title or "MEGA" in title:
                best_nump = option.get('data-nump')
                break

        # ၃။ Website ရဲ့ AJAX API ဆီကနေ embed_url ကို လှမ်းတောင်းမယ်
        ajax_url = "https://mmsubmovie.com/wp-admin/admin-ajax.php"
        payload = {
            'action': 'doo_player_ajax',
            'post': post_id,
            'nump': best_nump,
            'type': 'movie'
        }
        
        # Referer header ပါမှ API က ခွင့်ပြုမှာပါ
        headers['Referer'] = movie_url
        api_res = requests.post(ajax_url, data=payload, headers=headers, timeout=10)
        json_data = api_res.json()
        
        return json_data.get('embed_url', "") # ဒါကတော့ တိုက်ရိုက်ကြည့်လို့ရမယ့် Player Link ပါ

    except Exception as e:
        print(f"Error getting video link: {e}")
        return ""

def scrape_all_movies():
    base_url = "https://mmsubmovie.com/movies/page/"
    all_movies = []
    page_num = 1
    
    # စမ်းသပ်ရန် စာမျက်နှာ ၂ ခုကို အရင်ဆွဲပြထားပါမယ် (အကုန်ရချင်ရင် page_num limit ဖြုတ်ပါ)
    while page_num <= 2:
        url = f"{base_url}{page_num}/"
        print(f"စာမျက်နှာ {page_num} ကို ဖတ်နေသည်...")
        
        try:
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.select('article.item')
            
            if not items: break

            for item in items:
                title_elem = item.select_one('.data h3 a')
                if title_elem:
                    title = title_elem.text.strip()
                    m_link = title_elem['href']
                    img = item.select_one('.poster img').get('src') or item.select_one('.poster img').get('data-src')
                    
                    print(f" - Link ယူနေသည်: {title}")
                    # ဗီဒီယို link အစစ်ကို ဆွဲယူခြင်း
                    direct_video = get_direct_video_link(m_link)

                    all_movies.append({
                        "title": title,
                        "image": img,
                        "link": m_link,
                        "video_url": direct_video, # JSON ထဲမှာ ဒါအရေးကြီးဆုံးပါ
                        "rating": item.select_one('.rating').text.strip() if item.select_one('.rating') else "N/A"
                    })
            
            page_num += 1
            time.sleep(1)
        except: break

    with open('movies.json', 'w', encoding='utf-8') as f:
        json.dump(all_movies, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    scrape_all_movies()
