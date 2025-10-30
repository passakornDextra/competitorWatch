import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import urllib3
import re
import time
from deep_translator import GoogleTranslator
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from urllib.parse import urljoin, quote


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

# ---- Scraper Functions ----
def scrape_mateenbar_and_pultron():
    all_articles = []

    # --- Pultron News ---
    url_pultron = "https://pultron.com/insights/pultron-composite-news/"
    response_pultron = requests.get(url_pultron, headers=HEADERS, verify=False)
    response_pultron.raise_for_status()
    soup_pultron = BeautifulSoup(response_pultron.content, 'html.parser')

    articles_pultron = soup_pultron.select('div.blog-type-blog')
    for article in articles_pultron:
        h2_tag = article.find('h2')
        a_tag = h2_tag.find_parent('a') if h2_tag else None
        title = h2_tag.get_text(strip=True) if h2_tag else ""
        link = a_tag['href'] if a_tag and a_tag.has_attr('href') else ""
        img_tag = article.find('img', class_='img-fluid')
        img_url = img_tag['src'] if img_tag else ""
        if img_url.startswith('/'):
            img_url = f"https://pultron.com{img_url}"

        date_text = ""
        article_date = None
        date_tag = article.find('div', class_='blog-post-meta')
        if date_tag:
            date_text = date_tag.get_text(strip=True)
            try:
                article_date = datetime.strptime(date_text, "%d %B %Y")
            except Exception:
                article_date = None

        summary_tag = article.find('div', class_='post-summary')
        summary = summary_tag.get_text(strip=True) if summary_tag else ""

        all_articles.append({
            "Title": title,
            "DateText": date_text,
            "Date": article_date.strftime("%B %d, %Y") if article_date else date_text,
            "Link": link,
            "Image": img_url,
            "Summary": summary,
            "Source": "Mateenbar Pultron"
        })

    # --- Mateenbar Blog ---
    url_mateenbar = "https://mateenbar.com/en-us/blog/"
    response_mateenbar = requests.get(url_mateenbar, headers=HEADERS, verify=False)
    response_mateenbar.raise_for_status()
    soup_mateenbar = BeautifulSoup(response_mateenbar.content, "html.parser")

    article_blocks = soup_mateenbar.find_all("article")
    for block in article_blocks:
        title_tag = block.find("a", itemprop="url")
        title = title_tag.get("title", "").strip() if title_tag else ""
        link = title_tag.get("href", "") if title_tag else ""
        if link and not link.startswith("http"):
            link = "https://mateenbar.com" + link

        # Extract date from URL
        date_text = ""
        article_date = None
        if link:
            parts = link.split("/")
            if len(parts) >= 6:
                year, month, day = parts[4], parts[5], parts[6]
                date_text = f"{year}-{month}-{day}"
                try:
                    article_date = datetime.strptime(date_text, "%Y-%m-%d")
                except ValueError:
                    article_date = None

        img_tag = block.find("img", class_="wp-post-image")
        image_url = img_tag["src"] if img_tag and img_tag.has_attr("src") else ""
        summary_tag = block.find("div", class_="mkd-post-text-inner")
        summary_text = summary_tag.get_text(strip=True) if summary_tag else ""

        all_articles.append({
            "Title": title,
            "DateText": date_text,
            "Date": article_date.strftime("%B %d, %Y") if article_date else date_text,
            "Link": link,
            "Image": image_url,
            "Summary": summary_text,
            "Source": "Mateenbar Pultron"
        })

    return all_articles

def scrape_ancon():
    url = "https://www.ancon.co.uk/whats-new"
    base_url = "https://www.ancon.co.uk"
    articles_data = []

    # Use your existing HEADERS
    response = requests.get(url, headers=HEADERS, verify=False)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all('article', class_='post')

    for article in articles:
        # Title and link
        title_tag = article.find('h2', class_='post__title')
        link_tag = title_tag.find('a') if title_tag else None
        title = link_tag.text.strip() if link_tag else ""
        link = link_tag['href'] if link_tag else ""
        if link.startswith("/"):
            link = base_url + link

        # Date
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

        # Image
        img_tag = article.find('img')
        image_url = ""
        if img_tag:
            # Prefer lazy-loaded image
            if img_tag.has_attr('data-srcset'):
                image_url = img_tag['data-srcset'].split()[0]
            elif img_tag.has_attr('src'):
                image_url = img_tag['src']
            if image_url.startswith("/"):
                image_url = base_url + image_url
            # Ignore placeholder images
            if "placeholder" in image_url.lower():
                image_url = ""

        # Assemble article data
        articles_data.append({
            "Title": title,
            "DateText": datetime_str,
            "Date": article_date,
            "Link": link,
            "Image": image_url,
            "Summary": "",
            "Source": "Ancon"
        })

    return articles_data


def scrape_nvent_lenton():
    url = "https://blog.nvent.com/category/lenton/"
    base_url = "https://blog.nvent.com"
    articles_data = []

    response = requests.get(url, headers=HEADERS, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all('article')

    for article in articles:
        # Link
        a_tag = article.find('a', class_='panel-link')
        link = a_tag['href'].strip() if a_tag and a_tag.has_attr('href') else ""
        if link and not link.startswith("http"):
            link = base_url + link

        # Title
        title = ""
        for tag in ['h2', 'h3', 'h4']:
            title_tag = article.find(tag)
            if title_tag and title_tag.text.strip():
                title = title_tag.text.strip()
                break
        if not title:
            title = article.get_text(separator=" ", strip=True).replace('\n', ' ')

        # Date
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

        # Image
        image_url = ""
        img_tag = article.find('img')
        if img_tag:
            # Use srcset if available
            if img_tag.has_attr('srcset'):
                srcset = img_tag['srcset'].split(',')[0].strip()  # Get first source
                image_url = srcset.split()[0]  # Remove resolution part like '2x'
            elif img_tag.has_attr('src'):
                image_url = img_tag['src']
            # Convert to full URL
            if image_url.startswith("/"):
                image_url = base_url + image_url
            # Skip placeholder
            if "placeholder" in image_url.lower():
                image_url = ""

        articles_data.append({
            "Title": title,
            "DateText": date_text,
            "Date": article_date,
            "Link": link,
            "Image": image_url,
            "Summary": "",
            "Source": "nVent LENTON"
        })

    return articles_data

def scrape_moment_latest_news():
    import re
    from urllib.parse import urljoin
    from datetime import datetime

    url = "https://www.moment-solutions.com/latest-news/"
    base_url = "https://www.moment-solutions.com"
    articles_data = []

    resp = requests.get(url, headers=HEADERS, verify=False, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, "html.parser")

    # Heuristic: the listing uses "Read more" links; use those as anchors for each card
    read_more_links = soup.find_all(
        "a",
        string=lambda s: isinstance(s, str) and "read more" in s.lower()
    )

    DATE_PAT = re.compile(r"([A-Za-z]{3,9}\s+\d{1,2},\s+\d{4})")

    for a in read_more_links:
        # Link
        href = (a.get("href") or "").strip()
        link = urljoin(base_url, href) if href else ""

        # Find a reasonable container that holds title/date/img
        container = a
        for _ in range(6):
            if not container or not getattr(container, "parent", None):
                break
            container = container.parent
            if container.find(["h2", "h3", "h4"]):
                break

        # Title
        title = ""
        for tag in ["h2", "h3", "h4"]:
            t = container.find(tag) if container else None
            if t and t.get_text(strip=True):
                title = t.get_text(strip=True)
                break
        if not title:
            t = a.find_previous(["h2", "h3", "h4"])
            if t:
                title = t.get_text(strip=True)

        # Date
        date_text = ""
        article_date = None
        block_text = container.get_text(" ", strip=True) if container else ""
        m = DATE_PAT.search(block_text)
        if m:
            date_text = m.group(1)
            for fmt in ("%B %d, %Y", "%b %d, %Y"):
                try:
                    article_date = datetime.strptime(date_text, fmt)
                    break
                except Exception:
                    pass

        # Image
        image_url = ""
        img = (container.find("img") if container else None) or a.find_previous("img")
        if img:
            candidate = ""
            if img.has_attr("srcset"):
                # Take first candidate in srcset
                first_part = img["srcset"].split(",")[0].strip().split()
                if first_part:
                    candidate = first_part[0]
            elif img.has_attr("src"):
                candidate = img["src"]
            if candidate.startswith("/"):
                candidate = urljoin(base_url, candidate)
            if "placeholder" in candidate.lower():
                candidate = ""
            image_url = candidate

        articles_data.append({
            "Title": title,
            "DateText": date_text,
            "Date": article_date,
            "Link": link,
            "Image": image_url,
            "Summary": "",
            "Source": "Moment (Leviat)"
        })

    # De-dup by Link (the page can sometimes repeat blocks)
    seen, deduped = set(), []
    for item in articles_data:
        if item["Link"] and item["Link"] not in seen:
            deduped.append(item)
            seen.add(item["Link"])

    return deduped

def scrape_macalloy():
    from urllib.parse import urljoin
    import time
    from datetime import datetime

    url = "https://macalloy.com/news/"
    base = "https://macalloy.com"
    articles_data = []

    resp = requests.get(url, headers=HEADERS, verify=False, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, "html.parser")

    # same selector you used
    title_tags = soup.find_all("h2", class_="post__title entry-title h4")

    def first_image(article_soup, page_link):
        # 1) typical featured image
        img = (article_soup.select_one("div.post__thumbnail img")
               or article_soup.select_one(".entry-content img")
               or article_soup.select_one("article img")
               or article_soup.find("img"))
        cand = ""
        if img:
            if img.has_attr("srcset"):
                # take first candidate in srcset
                part = img["srcset"].split(",")[0].strip().split()
                if part:
                    cand = part[0]
            if not cand:
                cand = (img.get("src") or "").strip()
        # 2) fall back to OG/Twitter image
        if not cand:
            meta = (article_soup.find("meta", attrs={"property": "og:image"})
                    or article_soup.find("meta", attrs={"name": "twitter:image"}))
            if meta and meta.get("content"):
                cand = meta["content"].strip()
        # absolutize
        return urljoin(page_link, cand) if cand else ""

    for title_tag in title_tags:
        link_tag = title_tag.find("a")
        title = link_tag.get_text(strip=True) if link_tag else (title_tag.get_text(strip=True) if title_tag else "")
        link = link_tag["href"].strip() if link_tag and link_tag.has_attr("href") else ""
        link = urljoin(base, link)

        date_text = ""
        article_date = None
        image_url = ""

        if link:
            try:
                article_resp = requests.get(link, headers=HEADERS, verify=False, timeout=30)
                article_resp.raise_for_status()
                article_soup = BeautifulSoup(article_resp.content, "html.parser")

                # date (prefer datetime attr)
                time_tag = article_soup.find("time")
                if time_tag:
                    date_text = (time_tag.get("datetime") or time_tag.get_text(strip=True)).strip()
                # parse a few common forms
                try:
                    article_date = datetime.fromisoformat(date_text.replace("Z", "+00:00"))
                except Exception:
                    try:
                        article_date = datetime.strptime(date_text[:10], "%Y-%m-%d")
                    except Exception:
                        article_date = None

                # first image inside the article page
                image_url = first_image(article_soup, link)

            except Exception:
                pass
            time.sleep(0.2)

        articles_data.append({
            "Title": title,
            "DateText": date_text,
            "Date": article_date,
            "Link": link,
            "Image": image_url,
            "Summary": "",
            "Source": "Macalloy"
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

def scrape_dywidag_selenium():
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.get("https://dywidag.com/press")
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    articles = soup.find_all("div", class_=lambda c: c and c.startswith("card-press_press-card_"))
    articles_data = []

    if articles:
        for article in articles:
            # Title
            title_tag = article.find(["h2", "h3"])
            title = title_tag.get_text(strip=True) if title_tag else ""

            # Link
            a_tag = article.find("a", href=True)
            link = a_tag['href'] if a_tag else ""
            if link and not link.startswith("http"):
                link = "https://dywidag.com" + link

            # Summary
            summary_tag = article.find("p")
            summary = summary_tag.get_text(strip=True) if summary_tag else ""

            # Date
            date_tag = article.find("span")
            date = date_tag.get_text(strip=True) if date_tag else ""

            # Image: Use static DYWIDAG logo
            img_url = "https://raw.githubusercontent.com/jumpbcc158/Logos/main/DYWIDAG_16x9.png"

            # Append data
            articles_data.append({
                "Title": title,
                "DateText": date,
                "Date": None,
                "Link": link,
                "Image": img_url,
                "Summary": summary,
                "Source": "Dywidag"
            })

    driver.quit()
    return articles_data



from datetime import datetime
BASE_URL = "https://www.annahuette.com"
LISTING_URL = urljoin(BASE_URL, "/news/")
TRANSLATE_PREFIX = "https://translate.google.com/translate?hl=en&sl=de&u="

GERMAN_MONTHS = {
    'Januar': 'January', 'Februar': 'February', 'März': 'March',
    'April': 'April', 'Mai': 'May', 'Juni': 'June', 'Juli': 'July',
    'August': 'August', 'September': 'September', 'Oktober': 'October',
    'November': 'November', 'Dezember': 'December'
}

def _build_driver(headless=True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(options=opts)

def _map_german_months(s: str) -> str:
    for de, en in GERMAN_MONTHS.items():
        s = s.replace(de, en)
    return s

def _parse_date_from_strings(candidates):
    """
    Try ISO (from datetime attribute), dd.mm.yyyy, or German month text -> English.
    Return 'YYYY-MM-DD' or '' if none matched.
    """
    for raw in candidates:
        if not raw:
            continue
        text = raw.strip()

        # 1) ISO 'yyyy-mm-dd' in attributes or strings
        m = re.search(r"(\d{4}-\d{2}-\d{2})", text)
        if m:
            try:
                dt = datetime.strptime(m.group(1), "%Y-%m-%d")
                return dt.strftime("%Y-%m-%d")
            except Exception:
                pass

        # 2) dd.mm.yyyy or d.m.yyyy
        m = re.search(r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b", text)
        if m:
            try:
                d, mn, y = map(int, m.groups())
                dt = datetime(y, mn, d)
                return dt.strftime("%Y-%m-%d")
            except Exception:
                pass

        # 3) German month words -> English, then parse common formats
        t = _map_german_months(text)
        t = re.sub(r'(\d{1,2})\.', r'\1', t)  # "3. Juli 2025" -> "3 Juli 2025"
        for fmt in ("%B %d, %Y", "%d %B %Y", "%B %d %Y"):
            try:
                dt = datetime.strptime(t, fmt)
                return dt.strftime("%Y-%m-%d")
            except Exception:
                continue

    return ""

def _accept_cookies_if_present(driver, wait):
    try:
        cookie_btn = wait.until(EC.presence_of_element_located((
            By.XPATH, "//button[contains(., 'Accept') or contains(., 'Zustimmen') or contains(., 'OK')]"
        )))
        cookie_btn.click()
        time.sleep(0.3)
    except Exception:
        pass

def _scroll_to_bottom(driver):
    # Basic lazy-load support: scroll in steps
    last_h = 0
    for _ in range(10):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.3)
        h = driver.execute_script("return document.body.scrollHeight")
        if h == last_h:
            break
        last_h = h

def _collect_listing_items_on_page(driver, wait):
    """
    Collect all article items on the current listing page as plain strings.
    Returns a list of dicts: {title, url, img, summary}
    """
    _scroll_to_bottom(driver)  # ensure lazy images/text rendered

    # Grab all <h2><a>
    link_elems = driver.find_elements(By.CSS_SELECTOR, "h2 a[href]")
    items = []

    for a in link_elems:
        try:
            title = (a.get_attribute("innerText") or a.text or "").strip()
            href = a.get_attribute("href") or ""
            url = href if href.startswith("http") else urljoin(BASE_URL, href)

            # Nearest preceding img in DOM order
            img_url = ""
            try:
                img_elem = a.find_element(By.XPATH, "ancestor-or-self::*[1]/preceding::img[1]")
                img_url = img_elem.get_attribute("src") or img_elem.get_attribute("data-src") or ""
            except Exception:
                pass

            # Nearest following paragraph as summary
            summary = ""
            try:
                p_elem = a.find_element(By.XPATH, "ancestor-or-self::*[1]/following::p[1]")
                summary = (p_elem.get_attribute("innerText") or p_elem.text or "").strip()
            except Exception:
                pass

            items.append({
                "title": title,
                "url": url,
                "img": img_url,
                "summary": summary
            })
        except Exception:
            continue

    return items

def _find_next_page_and_go(driver):
    """
    Try common 'next' links. Returns True if navigated; False otherwise.
    """
    candidates = [
        "//a[contains(@class,'next')]",
        "//a[contains(., 'Older') or contains(., 'Ältere') or contains(., 'Weiter') or contains(., 'Nächste')]",
        "//a[@rel='next']"
    ]
    for xp in candidates:
        links = driver.find_elements(By.XPATH, xp)
        for l in links:
            try:
                href = l.get_attribute("href") or ""
                if href:
                    l.click()
                    time.sleep(0.8)
                    return True
            except Exception:
                # As a fallback, navigate via href directly
                try:
                    if href:
                        driver.get(href)
                        time.sleep(0.8)
                        return True
                except Exception:
                    continue
    return False

def scrape_annahutte_selenium_all(headless=True, timeout=20, date_fmt="%Y-%m-%d"):
    driver = _build_driver(headless=headless)
    wait = WebDriverWait(driver, timeout)
    articles = []

    try:
        driver.get(LISTING_URL)
        _accept_cookies_if_present(driver, wait)

        page_num = 1
        all_items = []

        # Iterate pages
        while True:
            items = _collect_listing_items_on_page(driver, wait)
            # Deduplicate by URL (if same appears across pages)
            known_urls = {it['url'] for it in all_items}
            new_items = [it for it in items if it['url'] not in known_urls]
            all_items.extend(new_items)
            # Try next page
            moved = _find_next_page_and_go(driver)
            if not moved:
                break
            page_num += 1

        # Now visit each article to extract the real date
        for it in all_items:
            url = it["url"]
            translated_link = TRANSLATE_PREFIX + quote(url, safe="")

            try:
                driver.get(url)

                date_candidates = []

                # Prefer <time> tag
                time_elems = driver.find_elements(By.XPATH, "//time")
                for te in time_elems:
                    date_candidates.append(te.get_attribute("datetime"))
                    date_candidates.append(te.get_attribute("innerText"))

                # Meta fallbacks (WordPress often sets these)
                meta_elems = driver.find_elements(
                    By.CSS_SELECTOR,
                    "meta[property='article:published_time'], "
                    "meta[name='date'], meta[name='pubdate'], "
                    "meta[name='DC.date'], meta[itemprop='datePublished']"
                )
                for me in meta_elems:
                    date_candidates.append(me.get_attribute("content"))

                article_date_iso = _parse_date_from_strings(date_candidates)

                # Format date per preference
                article_date = ""
                if article_date_iso:
                    dt = datetime.strptime(article_date_iso, "%Y-%m-%d")
                    article_date = dt.strftime(date_fmt)

                articles.append({
                    "Title": it["title"],
                    "Date": article_date,
                    "DateText": article_date,    # keep consistent
                    "Summary": it["summary"],
                    "Image": it["img"],
                    "Link": translated_link,     # raw '&', not '&amp;'
                    "Source": "SAH Annahutte"
                })

            except Exception:
                # Continue even if some article fails
                continue

            time.sleep(0.3)

    finally:
        driver.quit()

    return articles



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
# ---- Configurable Source List ----





def scrape_minova_apac_news():
    import re
    import requests
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin
    from datetime import datetime

    base_url = "https://www.minovaglobal.com"
    url = f"{base_url}/apac/news"
    headers = globals().get("HEADERS", {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })

    r = requests.get(url, headers=headers, timeout=30, verify=False)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    link_re = re.compile(r"/apac/news/(\d{4}-\d{2}-\d{2})/")

    def abs_url(src: str) -> str:
        if not src:
            return ""
        s = src.strip()
        # handle srcset: "url 1200w, url2 600w"
        if "," in s and " " in s:
            s = s.split(",")[0].strip().split()[0]
        s = urljoin(base_url, s)
        return s.replace(" ", "%20")

    def get_listing_img(a):
        # Prefer the card image inside the anchor
        img = a.select_one("img.object-cover") or a.find("img")
        if not img:
            return ""
        return abs_url(img.get("src") or img.get("data-src") or img.get("srcset") or img.get("data-srcset") or "")

    # Collect (a_tag, full_url, date_from_url, listing_img)
    items = []
    seen = set()
    for a in soup.select('a[href^="/apac/news/"], a[href*="/apac/news/"]'):
        href = (a.get("href") or "").strip()
        if not href:
            continue
        full = urljoin(base_url, href)
        m = link_re.search(full)
        if not m or full in seen:
            continue
        seen.add(full)
        durl = m.group(1)  # YYYY-MM-DD
        items.append((a, full, durl, get_listing_img(a)))

    out = []
    for a, link, durl, listing_img in items:
        try:
            # date from URL
            dt = datetime.strptime(durl, "%Y-%m-%d")
            date_text = dt.strftime("%B %d, %Y")

            # title from link text (fallback to article H1 later)
            raw = " ".join(a.stripped_strings)
            title = raw

            image_url = listing_img  # ← prefer listing-card image you pointed out

            # If we still need title/summary/OG image, fetch article
            if not image_url or not title or len(title) < 8:
                d = requests.get(link, headers=headers, timeout=30, verify=False)
                if d.ok:
                    ds = BeautifulSoup(d.text, "html.parser")
                    if not title:
                        h1 = ds.find("h1")
                        if h1 and h1.get_text(strip=True):
                            title = h1.get_text(strip=True)
                    if not image_url:
                        og = ds.find("meta", attrs={"property": "og:image"})
                        if og and og.get("content"):
                            image_url = abs_url(og["content"])
                        else:
                            img = ds.select_one("main img, article img, .prose img, .content img, img.object-cover")
                            if img:
                                image_url = abs_url(img.get("srcset") or img.get("src") or "")

                    # short summary
                    desc = ds.find("meta", attrs={"name": "description"})
                    summary = (desc.get("content").strip() if desc and desc.get("content") else "")
                    if not summary:
                        p = ds.select_one("main p, article p, .prose p, .content p")
                        if p:
                            summary = p.get_text(" ", strip=True)
                    if summary and len(summary) > 280:
                        summary = summary[:277] + "…"
                else:
                    summary = ""
            else:
                summary = ""

            out.append({
                "Title": title or "",
                "DateText": date_text,
                "Date": dt,
                "Link": link,
                "Image": image_url or "",
                "Summary": summary,
                "Source": "FiReP Minova"
            })
        except Exception:
            continue

    return out

def scrape_tagembed_widget_headless(
    widget_url: str = "https://widget.tagembed.com/298372?website=1",
    max_posts: int = 200,
    max_clicks: int = 10,
    headless: bool = True,
):
    """
    Scrape a Tagembed widget *without* API key by rendering in a real browser and
    capturing the JSON responses that the widget loads from api.tagembed.com.

    Returns list of dicts with keys:
      Title, DateText, Date (datetime|None), Link, Image, Summary, Source
    """
    import re
    from datetime import datetime
    from urllib.parse import urlparse
    from collections import deque

    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        raise RuntimeError(
            "Playwright is required. Install with:\n"
            "  pip install playwright\n"
            "  playwright install"
        ) from e

    def map_feeds(feeds):
        out = []
        for f in feeds:
            content = (f.get("postContent") or "").strip()
            author  = f.get("postAuthorName") or f.get("postUsername") or f.get("feedName") or ""
            network = f.get("networkName") or ""
            # Title strategy: Author — first part of content (trim)
            title = (author + " — " + content).strip(" —")[:120] if (author or content) else (network or "Tagembed post")

            # Image candidates
            image = f.get("postMediaFile") or f.get("postPicture") or f.get("image") or ""
            if not image:
                il = f.get("imageList") or []
                if isinstance(il, list) and il:
                    image = il[0]

            # Link candidates (absolute only)
            link = ""
            for k in ("CTAurl", "postLinkUrl", "postUrl"):
                cand = f.get(k) or ""
                if isinstance(cand, str) and cand.startswith(("http://", "https://")):
                    link = cand
                    break

            # Date (epoch seconds is typical)
            dt = None
            ts = f.get("postCreatedAt") or f.get("postTimeStamp")
            try:
                if ts is not None:
                    dt = datetime.utcfromtimestamp(int(ts))
            except Exception:
                dt = None

            out.append({
                "Title": title or (network or "Tagembed post"),
                "DateText": dt.strftime("%b %d, %Y") if dt else "",
                "Date": dt,
                "Link": link,
                "Image": image or "",
                "Summary": content,
                "Source": f"Tagembed Widget {widget_url.split('/')[-1].split('?')[0]}"
                          + (f" ({network})" if network else "")
            })
        return out

    # ---- Playwright session ----
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        )

        captured = []
        seen_batches = set()

        def on_response(resp):
            url = resp.url
            if "api.tagembed.com" not in url:
                return
            try:
                j = resp.json()
            except Exception:
                return
            # Expect structure: {"body": {"feeds": [...]}}
            feeds = (j.get("body") or {}).get("feeds")
            if not feeds:
                return
            # De-dupe batches by a simple hash of feed IDs + count
            ids = tuple(sorted([str(x.get("postId") or x.get("_id") or x.get("postLinkUrl") or x.get("CTAurl") or "") for x in feeds]))
            sig = (len(feeds), hash(ids))
            if sig in seen_batches:
                return
            seen_batches.add(sig)
            captured.extend(feeds)

        context.on("response", on_response)
        page = context.new_page()

        page.goto(widget_url, wait_until="networkidle", timeout=90000)
        page.wait_for_timeout(1500)  # tiny buffer for late XHRs

        # Try to click "Load more" a few times to get additional pages
        # Common selectors used by Tagembed themes:
        load_more_selectors = [
            'button:has-text("Load more")',
            'button:has-text("Load More")',
            ".taLoadMoreBtn",
            ".load-more",
            "button.loadMore",
        ]
        clicks = 0
        while clicks < max_clicks and len(captured) < max_posts:
            clicked = False
            for sel in load_more_selectors:
                try:
                    btn = page.locator(sel)
                    if btn.count() > 0 and btn.first.is_visible():
                        btn.first.click()
                        page.wait_for_timeout(1200)
                        clicked = True
                        clicks += 1
                        break
                except Exception:
                    continue
            if not clicked:
                # Some widgets paginate on scroll
                try:
                    page.mouse.wheel(0, 2000)
                    page.wait_for_timeout(900)
                    clicks += 1
                    continue
                except Exception:
                    break

        # Final buffer to catch trailing requests
        page.wait_for_timeout(1500)
        context.close()
        browser.close()

    # Map & de-dupe items
    items = map_feeds(captured)

    # De-dupe by (Link, Title) or fallback hash
    seen = set()
    deduped = []
    for it in items:
        key = (it.get("Link"), it.get("Title"))
        if not key[0] and not key[1]:
            key = (it.get("Image"), it.get("DateText"))
        if key not in seen:
            deduped.append(it)
            seen.add(key)

    # Sort newest first
    deduped.sort(key=lambda x: x["Date"] or datetime(1970,1,1), reverse=True)

    # Truncate to max_posts
    if max_posts and len(deduped) > max_posts:
        deduped = deduped[:max_posts]

    return deduped
def scrape_splicesleeve_events():
    url = "https://www.splicesleeve.com/events"
    response = requests.get(url, headers=HEADERS, verify=False)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    events_data = []

    # Each event block
    event_blocks = soup.find_all("div", class_="box_wrapper")

    for block in event_blocks:
        # Description (used as Title base)
        description = block.find("div", class_="description")
        description_text = description.get_text(strip=True) if description else ""

        # Start and End dates
        start_date = block.find("div", class_="data-inizio")
        start_text = start_date.get_text(strip=True).replace("Start:", "").strip() if start_date else ""

        end_date = block.find("div", class_="data-fine")
        end_text = end_date.get_text(strip=True).replace("End:", "").strip() if end_date else ""

        # Month and Year
        month = block.find("div", class_="data-evento-destra")
        month_text = month.get_text(strip=True) if month else ""

        year = block.find("div", class_="data-evento-destra-2")
        year_text = year.get_text(strip=True) if year else ""

        # Image (optional)
        img_tag = block.find("img")
        image_url = img_tag["src"] if img_tag and img_tag.has_attr("src") else ""

        # Link (fixed for all)
        link = "https://www.splicesleeve.com/events"

        # Combine Title: description + start + end
        title_combined = f"{description_text} start date {start_text} end date {end_text}"

        # DateText and Date from month/year
        datetime_str = f"{month_text} {year_text}"

        # Append in requested format
        events_data.append({
            "Title": title_combined,
            "DateText": datetime_str,
            "Date": datetime_str,
            "Link": link,
            "Image": image_url,
            "Summary": description_text,
            "Source": "nmb splice sleeve"
        })

    return events_data

COMPETITOR_SOURCES = [
    ("Ancon", scrape_ancon),
    ("nVent LENTON", scrape_nvent_lenton),
    ("Dywidag", scrape_dywidag_selenium),
    ("Anker Schroeder", scrape_anker_schroeder),
    ("SAH Annahutte", scrape_annahutte_selenium_all),
    ("Moment", scrape_moment_latest_news),
    ("Macalloy",  scrape_macalloy),
    ("Williams Form", scrape_williams_form),
    ("FiReP Minova",scrape_minova_apac_news),
    ("MST Bar",scrape_tagembed_widget_headless),
    ("Mateenbar Pultron", scrape_mateenbar_and_pultron),
    ("nmb splice sleeve",scrape_splicesleeve_events),
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


def _extract_date_from_url(url: str):
    if not isinstance(url, str):
        return None
    m = re.search(r'(19|20\d{2})[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])', url)
    if m:
        y, mo, d = m.group(1), m.group(2), m.group(3)
        try:
            return pd.Timestamp(f'{y}-{mo}-{d}', tz='UTC')
        except Exception:
            pass
    m = re.search(r'(19|20\d{2})[-/](0[1-9]|1[0-2])(?:/|$)', url)
    if m:
        y, mo = m.group(1), m.group(2)
        try:
            return pd.Timestamp(f'{y}-{mo}-01', tz='UTC')
        except Exception:
            pass
    return None

def _normalize_and_sort_dates(df: pd.DataFrame) -> pd.DataFrame:
    import pandas as pd
    import numpy as np

    # 1) Start from existing Date (may be dt/str/None) → coerce to proper UTC datetimes
    d = pd.to_datetime(df.get("Date"), errors="coerce", utc=True)

    # 2) Fallback: DateText (handle day-first when looks like d/m/Y or d-m-Y or d.m.Y)
    if "DateText" in df.columns:
        mask = d.isna() & df["DateText"].astype(str).str.strip().ne("")
        if mask.any():
            s = df.loc[mask, "DateText"].astype(str).str.strip()

            # Patterns like 01/10/2025, 01-10-2025, 01.10.2025 → parse as day-first
            dmy_mask = s.str.match(r"^\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{4}$")
            if dmy_mask.any():
                d.loc[s.index[dmy_mask]] = pd.to_datetime(
                    s[dmy_mask], errors="coerce", utc=True, dayfirst=True
                )

            # The rest (e.g., 'Sep 29, 2025', ISO, etc.) → general parser
            rest_idx = s.index[~dmy_mask]
            if len(rest_idx) > 0:
                d.loc[rest_idx] = pd.to_datetime(
                    s.loc[rest_idx], errors="coerce", utc=True
                )

    # 3) Fallback: parse from Link (YYYY-MM-DD / YYYY/MM/DD / YYYY-MM in URL)
    if "Link" in df.columns:
        mask2 = d.isna() & df["Link"].astype(str).str.strip().ne("")
        if mask2.any():
            extracted = df.loc[mask2, "Link"].map(_extract_date_from_url)
            d.loc[mask2] = pd.to_datetime(extracted, errors="coerce", utc=True)

    # Ensure final dtype is datetimetz[UTC]
    d = pd.to_datetime(d, errors="coerce", utc=True)
    df["DateParsed"] = d

    # 4) Strict ISO string (YYYY-MM-DD). NaT → ""
    df["DateISO"] = ""
    has_dt = df["DateParsed"].notna()
    if has_dt.any():
        df.loc[has_dt, "DateISO"] = df.loc[has_dt, "DateParsed"].dt.strftime("%Y-%m-%d")

    # 5) Sort newest → oldest (stable tiebreakers on Source, Title)
    df.sort_values(
        ["DateParsed", "Source", "Title"],
        ascending=[False, True, True],
        inplace=True,
        kind="mergesort",
    )
    df.reset_index(drop=True, inplace=True)
    return df


def scrape_all_and_export_csv():
    all_articles = []
    status_list = []
    for name, func in COMPETITOR_SOURCES:
        data, status = scrape_with_status(func, name)

        # 🔥 Translate Annahütte just before adding
        if name == "SAH Annahutte":
            for article in data:
                try:
                    article["Title"] = GoogleTranslator(source='de', target='en').translate(article["Title"])
                except Exception:
                    pass
                try:
                    if article["Summary"]:
                        article["Summary"] = GoogleTranslator(source='de', target='en').translate(article["Summary"])
                except Exception:
                    pass

        all_articles.extend(data)
        status_list.append(status)

    df = pd.DataFrame(all_articles)
    df = _normalize_and_sort_dates(df)   # ← date-only normalization & sorting
    df.to_csv("export_combined.csv", index=False, encoding="utf-8-sig")

    df_status = pd.DataFrame(status_list)
    df_status.to_csv("scrape_status.csv", index=False, encoding="utf-8-sig")

    print('\nData exported to "export_combined.csv" and "scrape_status.csv".')

if __name__ == "__main__":
    scrape_all_and_export_csv()
