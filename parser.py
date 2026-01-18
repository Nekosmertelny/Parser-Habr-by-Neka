import requests
from bs4 import BeautifulSoup
import time

url = "https://habr.com/ru/articles/top/daily/"

def get_url(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}  # добавляем, чтобы не блочило
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        return res.text
    except Exception as e:
        print(f"Ошибка загрузки {url}: {e}")
        return ""

def soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")

# Функция для текста полной статьи (точно под текущую структуру Habr)
def get_full_text(soup):
    body = soup.find("div", class_="article-formatted-body")
    if not body:
        return "Текст статьи не найден (класс изменился)"
    
    paragraphs = body.find_all("p")
    text_lines = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
    return "\n\n".join(text_lines)

def main():
    print("Загружаем топ за сутки...")
    top_html = get_url(url)
    if not top_html:
        return
    
    top_soup = soup(top_html)
    
    # Собираем ссылки на статьи (актуально на январь 2026)
    articles = []
    for h2 in top_soup.find_all("h2"):
        a = h2.find("a", href=True)
        if a and ("/articles/" in a["href"] or "/companies/" in a["href"]):
            title = a.get_text(strip=True)
            link = "https://habr.com" + a["href"] if a["href"].startswith("/") else a["href"]
            articles.append((title, link))
    
    if not articles:
        print("Не нашёл статей в топе. Сайт поменял структуру ещё раз.")
        return
    
    print(f"Нашёл {len(articles)} статей\n")
    
    # Берём только первые 3 статьи, чтобы не нагружать сайт
    for i, (title, article_url) in enumerate(articles[:3], 1):
        print(f"{i}. {title}")
        print(f"   Ссылка: {article_url}")
        
        print("   Загружаем полную статью...")
        article_html = get_url(article_url)
        if article_html:
            article_soup = soup(article_html)
            full_text = get_full_text(article_soup)
            
            print("\nТекст статьи:")
            print(full_text[:2000] + "..." if len(full_text) > 2000 else full_text)
            print("\n" + "-"*100 + "\n")
        
        time.sleep(2)  # пауза между запросами

if __name__ == "__main__":
    main()