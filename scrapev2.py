import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import urllib3
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import time


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

# ---- Scraper Functions ----

def scrape_ancon():
    url = "https://www.ancon.co.uk/whats-new"
    articles_data = []
    response = requests.get(url, headers=HEADERS, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all('article', class_='post')
    for article in articles:
        title_tag = article.find('h2', class_='post__title')
        link_tag = title_tag.find('a') if title_tag else None
        title = link_tag.text.strip() if link_tag else ""
        link = link_tag['href'] if link_tag else ""
        time_tag = article.find('time')
        if time_tag and time_tag.has_attr('datetime'):
            datetime_str = time_tag['datetime']
            try:
                article_date = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            except Exception:
                article_date = None
        else:
            datetime_str = ""
            article_date = None
        articles_data.append({
            "Title": title,
            "DateText": datetime_str,
            "Date": article_date,
            "Link": link,
            "Image": "",
            "Summary": "",
            "Source": "Ancon"
        })
    return articles_data

def scrape_dextra_elementor():
    url = "https://www.dextragroup.com/news/"
    articles_data = []
    response = requests.get(url, headers=HEADERS, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    posts = soup.find_all('h3', class_='elementor-heading-title elementor-size-default')
    for post in posts:
        title = post.get_text(strip=True)
        link = ""
        sibling_link = post.find_next_sibling("a")
        if sibling_link and sibling_link.has_attr("href"):
            link = sibling_link['href']
        else:
            parent = post.find_parent()
            link_tag = parent.find('a') if parent else None
            if link_tag and link_tag.has_attr('href'):
                link = link_tag['href']
        if link and not link.startswith("http"):
            link = "https://www.dextragroup.com" + link
        articles_data.append({
            "Title": title,
            "DateText": "",
            "Date": None,
            "Link": link,
            "Image": "",
            "Summary": "",
            "Source": "Dextra"
        })
    return articles_data

def scrape_nvent_lenton():
    url = "https://blog.nvent.com/category/lenton/"
    articles_data = []
    response = requests.get(url, headers=HEADERS, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all('article')
    for article in articles:
        a_tag = article.find('a', class_='panel-link')
        link = a_tag['href'].strip() if a_tag and a_tag.has_attr('href') else ""
        if link and not link.startswith("http"):
            link = "https://blog.nvent.com" + link
        title = ""
        for tag in ['h2', 'h3', 'h4']:
            title_tag = article.find(tag)
            if title_tag and title_tag.text.strip():
                title = title_tag.text.strip()
                break
        if not title:
            title = article.get_text(separator=" ", strip=True).replace('\n', ' ')
        date_text = ""
        article_date = None
        date_li = article.find('li', class_='date')
        if date_li:
            date_text = date_li.text.strip()
            try:
                article_date = datetime.strptime(date_text, "%b %d, %Y")
            except Exception:
                try:
                    article_date = datetime.strptime(date_text, "%B %d, %Y")
                except Exception:
                    article_date = None
        articles_data.append({
            "Title": title,
            "DateText": date_text,
            "Date": article_date,
            "Link": link,
            "Image": "",
            "Summary": "",
            "Source": "nVent LENTON"
        })
    return articles_data

def scrape_moment_solutions():
    url = "https://www.moment-solutions.com/latest-news/"
    articles_data = []
    response = requests.get(url, headers=HEADERS, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    titles = soup.find_all('div', class_='vc_custom_heading vc_gitem-post-data vc_gitem-post-data-source-post_title')
    for title_div in titles:
        h4_tag = title_div.find('h4')
        title = h4_tag.get_text(strip=True) if h4_tag else ""
        date_div = title_div.find_next_sibling('div', class_='vc_custom_heading vc_gitem-post-data vc_gitem-post-data-source-post_date')
        date_text = date_div.get_text(strip=True) if date_div else ""
        try:
            article_date = datetime.strptime(date_text, "%b %d, %Y")
        except Exception:
            article_date = None
        link = ""
        link_tag = title_div.find('a')
        if not link_tag:
            parent = title_div.parent
            link_tag = parent.find('a') if parent else None
        if link_tag and link_tag.has_attr('href'):
            link = link_tag['href']
        if link and not link.startswith("http"):
            link = "https://www.moment-solutions.com" + link
        articles_data.append({
            "Title": title,
            "DateText": date_text,
            "Date": article_date,
            "Link": link,
            "Image": "",
            "Summary": "",
            "Source": "Moment Solutions"
        })
    return articles_data

def scrape_williams_form():
    url = "https://www.williamsform.com/insights/"
    articles_data = []
    response = requests.get(url, headers=HEADERS, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all('h2', class_='post-title')
    for h2 in articles:
        a_tag = h2.find('a')
        title = a_tag.get_text(strip=True) if a_tag else ""
        link = a_tag['href'] if a_tag else ""
        article_tag = h2.find_parent('article')
        img_tag = article_tag.find('img') if article_tag else None
        img_url = img_tag['src'] if img_tag and img_tag.has_attr('src') else ""
        date_text = ""
        article_date = None
        match = re.search(r'/(\d{4})/(\d{2})/', img_url)
        if match:
            date_text = f"{match.group(1)}-{match.group(2)}"
            try:
                article_date = datetime.strptime(date_text, "%Y-%m")
            except Exception:
                article_date = None
        articles_data.append({
            "Title": title,
            "DateText": date_text,
            "Date": article_date,
            "Link": link,
            "Image": img_url,
            "Summary": "",
            "Source": "Williams Form"
        })
    return articles_data

def scrape_macalloy():
    url = "https://macalloy.com/news/"
    articles_data = []
    response = requests.get(url, headers=HEADERS, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    title_tags = soup.find_all('h2', class_='post__title entry-title h4')
    for title_tag in title_tags:
        link_tag = title_tag.find('a')
        title = link_tag.get_text(strip=True) if link_tag else (title_tag.get_text(strip=True) if title_tag else "")
        link = link_tag['href'] if link_tag and link_tag.has_attr('href') else ""
        if link and not link.startswith("http"):
            link = "https://macalloy.com" + link
        date_text = ""
        article_date = None
        if link:
            try:
                article_resp = requests.get(link, headers=HEADERS, verify=False)
                article_resp.raise_for_status()
                article_soup = BeautifulSoup(article_resp.content, 'html.parser')
                time_tag = article_soup.find('time')
                if time_tag and time_tag.has_attr('datetime'):
                    date_text = time_tag['datetime']
                elif time_tag:
                    date_text = time_tag.text.strip()
                try:
                    article_date = datetime.strptime(date_text[:10], "%Y-%m-%d")
                except Exception:
                    article_date = None
            except Exception:
                date_text = ""
                article_date = None
            time.sleep(0.2)
        articles_data.append({
            "Title": title,
            "DateText": date_text,
            "Date": article_date,
            "Link": link,
            "Image": "",
            "Summary": "",
            "Source": "Macalloy"
        })
    return articles_data

def scrape_linxion():
    url = "https://www.linxion.com/blog/"
    articles_data = []
    response = requests.get(url, headers=HEADERS, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all('article')
    for article in articles:
        title_tag = article.find('h2', class_='entry-title')
        link_tag = title_tag.find('a') if title_tag else None
        title = link_tag.get_text(strip=True) if link_tag else (title_tag.get_text(strip=True) if title_tag else "")
        link = link_tag['href'] if link_tag and link_tag.has_attr('href') else ""
        if link and not link.startswith("http"):
            link = "https://www.linxion.com" + link
        date_tag = article.find('time', class_='entry-date')
        date_text = date_tag.get_text(strip=True) if date_tag else ""
        article_date = None
        if date_text:
            for fmt in ("%B %d, %Y", "%d %B %Y", "%Y-%m-%d"):
                try:
                    article_date = datetime.strptime(date_text, fmt)
                    break
                except Exception:
                    continue
        if not article_date and date_tag and date_tag.has_attr('datetime'):
            try:
                article_date = datetime.strptime(date_tag['datetime'][:10], "%Y-%m-%d")
            except Exception:
                article_date = None
        articles_data.append({
            "Title": title,
            "DateText": date_text,
            "Date": article_date,
            "Link": link,
            "Image": "",
            "Summary": "",
            "Source": "Linxion"
        })
    return articles_data

def scrape_tokyo_tekko():
    url = "https://www.tokyotekko.co.jp/en/index.html"
    articles_data = []
    response = requests.get(url, headers=HEADERS, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    for h3 in soup.find_all('h3'):
        date_tag = h3.find('span', class_='date')
        date_text = date_tag.get_text(strip=True) if date_tag else ""
        try:
            article_date = datetime.strptime(date_text, "%Y/%m/%d") if date_text else None
        except Exception:
            article_date = None
        a_tag = h3.find('a')
        title = a_tag.get_text(strip=True) if a_tag else ""
        link = a_tag['href'] if a_tag and a_tag.has_attr('href') else ""
        if link and link.startswith("/"):
            link = "https://www.tokyotekko.co.jp" + link
        if title and link:
            articles_data.append({
                "Title": title,
                "DateText": date_text,
                "Date": article_date,
                "Link": link,
                "Image": "",
                "Summary": "",
                "Source": "Tokyo Tekko"
            })
    return articles_data

def scrape_peikko():
    url = "https://www.peikko.com/blog/?cm_lang=en"
    articles_data = []
    response = requests.get(url, headers=HEADERS, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all('a', href=True)
    for a_tag in articles:
        content_div = a_tag.find('div', class_='content')
        if not content_div:
            continue
        date_tag = content_div.find('span', class_='date')
        date_text = date_tag.get_text(strip=True) if date_tag else ""
        try:
            article_date = datetime.strptime(date_text, "%B %d, %Y") if date_text else None
        except Exception:
            article_date = None
        h4_tag = content_div.find('h4')
        title = h4_tag.get_text(strip=True) if h4_tag else ""
        summary_tag = content_div.find('p')
        summary = summary_tag.get_text(strip=True) if summary_tag else ""
        link = a_tag['href']
        if link and link.startswith('/'):
            link = "https://www.peikko.com" + link
        image_div = a_tag.find('div', class_='image')
        image_url = ""
        if image_div and image_div.has_attr('style'):
            m = re.search(r'url\(([^)]+)\)', image_div['style'])
            if m:
                image_url = m.group(1).strip('"').strip("'")
        articles_data.append({
            "Title": title,
            "DateText": date_text,
            "Date": article_date,
            "Link": link,
            "Image": image_url,
            "Summary": summary,
            "Source": "Peikko"
        })
    return articles_data

def scrape_terwa():
    url = "https://www.terwa.com/en/news.html"
    articles_data = []
    response = requests.get(url, headers=HEADERS, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all('div', class_='news-article-body')
    for article in articles:
        date_tag = article.find('span', class_='time')
        date_text = date_tag.get_text(strip=True) if date_tag else ""
        try:
            article_date = datetime.strptime(date_text, "%d-%m-%Y")
        except Exception:
            article_date = None
        h2_tag = article.find('h2', class_='news-article-title')
        a_tag = h2_tag.find('a') if h2_tag else None
        title = a_tag.get_text(strip=True) if a_tag else ""
        link = a_tag['href'] if a_tag and a_tag.has_attr('href') else ""
        if link and not link.startswith("http"):
            link = "https://www.terwa.com" + link
        figure_tag = article.find_previous_sibling('figure')
        img_url = ""
        if figure_tag and 'style' in figure_tag.attrs:
            style = figure_tag['style']
            start = style.find("url('") + 5
            end = style.find("')", start)
            img_url = style[start:end] if start > 4 and end > start else ""
            if img_url and not img_url.startswith("http"):
                img_url = "https://www.terwa.com" + img_url
        articles_data.append({
            "Title": title,
            "DateText": date_text,
            "Date": article_date,
            "Link": link,
            "Image": img_url,
            "Summary": "",
            "Source": "Terwa"
        })
    return articles_data

def scrape_srg_global():
    url = "https://srgglobal.com.au/news-media/"
    articles_data = []
    response = requests.get(url, headers=HEADERS, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all('div', class_='post')
    for article in articles:
        a_tag = article.find('a')
        link = a_tag['href'] if a_tag and a_tag.has_attr('href') else ""
        h3_tag = article.find('h3')
        title = h3_tag.get_text(strip=True) if h3_tag else ""
        date_span = article.find('span', class_='post-date')
        date_text = date_span.get_text(strip=True) if date_span else ""
        try:
            article_date = datetime.strptime(date_text, "%b %d, %Y")
        except Exception:
            article_date = None
        img_url = ""
        img_div = article.find('div', class_='post-img')
        if img_div and 'style' in img_div.attrs:
            style = img_div['style']
            start = style.find("url('") + 5
            end = style.find("')", start)
            img_url = style[start:end] if start > 4 and end > start else ""
            if img_url and not img_url.startswith("http"):
                img_url = "https://srgglobal.com.au" + img_url
        articles_data.append({
            "Title": title,
            "DateText": date_text,
            "Date": article_date,
            "Link": link,
            "Image": img_url,
            "Summary": "",
            "Source": "SRG Global"
        })
    return articles_data

def scrape_anker_schroeder():
    url = "https://www.anker.de/en/news"
    response = requests.get(url, headers=HEADERS, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    articles = []
    for li in soup.select('ul.row > li.col-md-12'):
        title_tag = li.find('h3')
        title = title_tag.get_text(strip=True) if title_tag else ''
        link_tag = title_tag.find_parent('a') if title_tag else None
        link = link_tag['href'] if link_tag and link_tag.has_attr('href') else ''
        if link and not link.startswith("http"):
            link = "https://www.anker.de" + link
        img_tag = li.find('img')
        img_src = img_tag['data-src'] if img_tag and img_tag.has_attr('data-src') else ''
        if img_src and not img_src.startswith("http"):
            img_src = "https://www.anker.de" + img_src
        text_container = li.find('div', class_='col-md-10')
        summary = ''
        if text_container:
            p_tags = text_container.find_all('p')
            summary = "\n".join([p.get_text(strip=True) for p in p_tags]) if p_tags else ''
        articles.append({
            "Title": title,
            "DateText": "",
            "Date": None,
            "Link": link,
            "Image": img_src,
            "Summary": summary,
            "Source": "Anker Schroeder"
        })
    return articles

def _parse_date_safe(text: str, datetime_attr: str = None):
    """
    Parse date robustly. Prefer `datetime_attr` if provided (YYYY-MM-DD).
    Fallback to trying multiple common formats.
    Returns (date_obj, iso_text) or (None, None) if parsing fails.
    """
    if datetime_attr:
        try:
            d = datetime.strptime(datetime_attr.strip(), "%Y-%m-%d").date()
            return d, d.isoformat()
        except Exception:
            pass

    candidates = [
        "%m/%d/%Y",  # 11/28/2025
        "%d/%m/%Y",  # 28/11/2025
        "%m-%d-%Y",
        "%d-%m-%Y",
        "%b %d, %Y", # Nov 28, 2025
        "%B %d, %Y", # November 28, 2025
        "%Y-%m-%d",
    ]
    for fmt in candidates:
        try:
            d = datetime.strptime(text.strip(), fmt).date()
            return d, d.isoformat()
        except Exception:
            continue
    return None, None

def scrape_dywidag_selenium():
    options = Options()
    options.add_argument("--headless=new")  # Chrome 109+; for older Chrome use "--headless"
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    driver.get("https://dywidag.com/press")

    wait = WebDriverWait(driver, 20)
    # Wait for at least one press card to be present
    # Use a flexible CSS selector: any div containing `press-card` in its class list
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='press-card']")))

    # Try to load more items—scrolling to bottom a few times to trigger lazy load
    # (If there is a "Load more" button, click it instead.)
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(5):  # adjust iterations if you want to load more
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    soup = BeautifulSoup(driver.page_source, "html.parser")
    # Find cards more broadly
    cards = soup.select("div[class*='press-card'], article[class*='press-card']")
    articles_data = []

    for card in cards:
        # Title: look for h2/h3, or anchor with card title
        title_tag = card.find(["h2", "h3"])
        if not title_tag:
            # sometimes the title is within an <a>
            title_tag = card.find("a")
        title = title_tag.get_text(strip=True) if title_tag else ""

        # Link: prefer the first anchor inside the card
        a_tag = card.find("a", href=True)
        link = a_tag["href"].strip() if a_tag else ""
        if link and not link.startswith("http"):
            link = "https://dywidag.com" + link

        # Summary: try paragraph inside the card
        summary_tag = card.find("p")
        summary = summary_tag.get_text(strip=True) if summary_tag else ""

        # Date: prefer <time> element (often has datetime="YYYY-MM-DD")
        date_text = ""
        date_iso_attr = None
        time_tag = card.find("time")
        if time_tag:
            date_text = time_tag.get_text(strip=True)
            date_iso_attr = time_tag.get("datetime")

        if not date_text:
            # fallback: a span likely containing the date
            # Try spans that look like a date (contains '/' or month name)
            span_candidates = card.find_all("span")
            for s in span_candidates:
                txt = s.get_text(strip=True)
                if any(ch in txt for ch in ["/", "-", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul",
                                            "Aug", "Sep", "Oct", "Nov", "Dec"]):
                    date_text = txt
                    break

        date_obj, date_iso = _parse_date_safe(date_text, datetime_attr=date_iso_attr)

        # Static image
        img_url = "https://raw.githubusercontent.com/jumpbcc158/Logos/main/DYWIDAG_16x9.png"

        articles_data.append({
            "Title": title,
            "DateText": date_text,
            "Date": date_obj.isoformat() if date_obj else None,
            "Link": link,
            "Image": img_url,
            "Summary": summary,
            "Source": "Dywidag"
        })

    driver.quit()
    return articles_data


def scrape_boowon():
    url = "https://ibms.co.kr/?page_id=8350&lang=en"
    articles_data = []
    response = requests.get(url, headers=HEADERS, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all('div', class_='elementor-post__card')
    for article in articles:
        title_tag = article.find('h3', class_='elementor-post__title')
        title = title_tag.get_text(strip=True) if title_tag else ""
        link_tag = title_tag.find('a') if title_tag else None
        link = link_tag['href'] if link_tag and link_tag.has_attr('href') else ""
        if link and not link.startswith("http"):
            link = "https://ibms.co.kr" + link
        date_tag = article.find('span', class_='elementor-post-date')
        date_text = date_tag.get_text(strip=True) if date_tag else ""
        try:
            article_date = datetime.strptime(date_text, "%B %d, %Y")
        except Exception:
            article_date = None
        articles_data.append({
            "Title": title,
            "DateText": date_text,
            "Date": article_date,
            "Link": link,
            "Image": "",
            "Summary": "",
            "Source": "Boowon"
        })
    return articles_data
def scrape_annahutte():
    url = "https://www.annahuette.com/en/news/"  # <-- update to the correct news URL if different
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(url, headers=HEADERS, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    articles = []
    # Find all news card containers (adjust selector if needed)
    news_cards = soup.find_all("div", class_=re.compile("elementor-element-f850515"))
    for card in news_cards:
        # Find the date (assume it's in a child with class 'elementor-widget-container' and looks like 'Juli 2025')
        date_div = card.find("div", class_="elementor-widget-container")
        date_text = date_div.get_text(strip=True) if date_div else ""
        # Try to parse date (optional, can get creative here)
        article_date = None
        if date_text:
            try:
                # Example for German months: replace 'Juli' with 'July', etc., if you want to parse as datetime
                month_map = {'Januar':'January','Februar':'February','März':'March','April':'April','Mai':'May','Juni':'June','Juli':'July',
                             'August':'August','September':'September','Oktober':'October','November':'November','Dezember':'December'}
                parts = date_text.split()
                if len(parts) == 2:
                    month_en = month_map.get(parts[0], parts[0])
                    article_date = datetime.strptime(f"{month_en} {parts[1]}", "%B %Y")
            except Exception:
                article_date = None

        # Find headline (usually another div.elementor-widget-heading or h2/h3)
        headline_div = card.find("div", class_=re.compile("elementor-widget-heading"))
        title = ""
        if headline_div:
            heading_tag = headline_div.find(re.compile("^h[1-6]$"))
            title = heading_tag.get_text(strip=True) if heading_tag else headline_div.get_text(strip=True)

        # Get image: it's usually in a previous sibling above (walk up DOM to parent, then previous sibling)
        img_url = ""
        parent = card.parent
        prev_img = None
        while parent and not prev_img:
            prev_img = parent.find_previous_sibling("div", class_=re.compile("elementor-widget-image"))
            parent = parent.parent if parent else None
        if prev_img:
            img_tag = prev_img.find("img")
            if img_tag and img_tag.has_attr("src"):
                img_url = img_tag["src"]
            elif img_tag and img_tag.has_attr("data-src"):
                img_url = img_tag["data-src"]
        
        articles.append({
            "Title": title,
            "DateText": date_text,
            "Date": article_date,
            "Image": img_url,
            "Source": "SAH Annahütte",
            "Link": url  # No article link per card visible in screenshot; update if there is one!
        })

    return articles

# Example usage
if __name__ == "__main__":
    from pprint import pprint
    annahutte_news = scrape_annahutte()
    pprint(annahutte_news)

def scrape_splice_sleeve():
    # No English news page available
    return [{
        "Title": "",
        "DateText": "",
        "Date": None,
        "Link": "https://www.splicesleeve.com/",
        "Image": "",
        "Summary": "No news page available",
        "Source": "Splice Sleeve"
    }]

# ---- Configurable Source List ----

COMPETITOR_SOURCES = [
    ("Ancon", scrape_ancon),
    ("Dextra", scrape_dextra_elementor),
    ("nVent LENTON", scrape_nvent_lenton),
    ("Moment Solutions", scrape_moment_solutions),
    ("Williams Form", scrape_williams_form),
    ("Macalloy", scrape_macalloy),
    ("Linxion", scrape_linxion),
    ("Tokyo Tekko", scrape_tokyo_tekko),
    ("Peikko", scrape_peikko),
    ("Terwa", scrape_terwa),
    ("SRG Global", scrape_srg_global),
    ("Dywidag", scrape_dywidag_selenium),
    ("Anker Schroeder", scrape_anker_schroeder),
    ("Boowon", scrape_boowon),
    ("Splice Sleeve", scrape_splice_sleeve),
    ("SAH Annahutte", scrape_annahutte),
]

def scrape_with_status(scrape_func, site_name):
    try:
        data = scrape_func()
        status = "success"
        count = len(data)
    except Exception as e:
        data = []
        status = f"error: {str(e)}"
        count = 0
    return data, {"Site": site_name, "Status": status, "ArticlesFound": count}

def scrape_all_and_export_csv():
    all_articles = []
    status_list = []
    for name, func in COMPETITOR_SOURCES:
        data, status = scrape_with_status(func, name)
        all_articles.extend(data)
        status_list.append(status)
    df = pd.DataFrame(all_articles)
    print(df)
    df.to_csv("export_combined.csv", index=False)
    df_status = pd.DataFrame(status_list)
    print("\nScrape Status:")
    print(df_status)
    df_status.to_csv("scrape_status.csv", index=False)
    print('\nData exported to "export_combined.csv" and "scrape_status.csv".')

if __name__ == "__main__":
    scrape_all_and_export_csv()
