from bs4 import BeautifulSoup
from pathlib import Path

html = Path("fixtures/search_python_page1.html").read_text(encoding="utf-8", errors="ignore")
soup = BeautifulSoup(html, "html.parser")

print("HTML length:", len(html))

cards1 = soup.find_all('div', class_=lambda c: c and 'slideshow-card' in c)
print('slideshow-card found:', len(cards1))

cards2 = soup.find_all('a', attrs={'data-cy': 'slideshow-card-link'})
print('slideshow-card-link found:', len(cards2))

links = soup.find_all('a', href=True)
ss_links = [l for l in links if 'slideshare.net/slideshow' in l.get('href', '')]
print('slideshow links found:', len(ss_links))
if ss_links:
    print('first link:', ss_links[0].get('href'))
    print('first aria-label:', ss_links[0].get('aria-label'))


# Find first card and print ALL its text
cards = soup.find_all("a", attrs={"data-cy": "slideshow-card-link"})
if cards:
    print("=== FIRST CARD FULL HTML ===")
    print(cards[0].prettify()[:3000])