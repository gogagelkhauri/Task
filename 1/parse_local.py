import json
import re
from bs4 import BeautifulSoup


def clean_title(title_text):
    if not title_text:
        return ""
    cleaned = re.sub(r'^(View\s+)', '', title_text, flags=re.IGNORECASE)
    cleaned = re.sub(r'(\s+details)$', '', cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def extract_prices_from_html(html_content):
    price_map = {}
    match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', html_content)
    if match:
        try:
            data = json.loads(match.group(1))
            products = data.get('plp', {}).get('products', [])
            for p in products:
                code = p.get('productCode')
                price = p.get('price', {}).get('listPrice')
                if code and price:
                    price_map[code] = price
            return price_map
        except Exception:
            pass

    product_blocks = re.split(r'("productCode":|class="product-tile")', html_content)
    for i in range(len(product_blocks) - 1):
        block = product_blocks[i] + product_blocks[i + 1]
        code_match = re.search(r'(CT\d{3}|CV\d{3}|CE\d{3}|[A-Z0-9]{5})', block)
        price_match = re.search(r'\$(\d+(?:\.\d{2})?)', block)
        if code_match and price_match:
            code = code_match.group(1)
            if code not in price_map:
                price_map[code] = f"${price_match.group(1)}"

    return price_map


def parse_jcrew_html(html_content, page_url=""):
    soup = BeautifulSoup(html_content, 'html.parser')
    price_map = extract_prices_from_html(html_content)

    products_dict = {}
    links = soup.find_all('a', href=re.compile(r'/p/mens/'))

    for link in links:
        url = link.get('href', '')
        if not url:
            continue

        full_url = f"https://www.jcrew.com{url}" if url.startswith('/') else url

        aria_label = link.get('aria-label', '')
        raw_title = aria_label if aria_label else link.get_text(strip=True)
        title = clean_title(raw_title)

        if not title or title.lower() in ['home', 'shop all']:
            continue

        # Extract product code
        code_match = re.search(r'/([A-Z0-9]{5})(?:\?|$)', full_url)
        product_code = code_match.group(1) if code_match else "UNKNOWN"

        # Extract color name from query params if available
        color_match = re.search(r'color_name=([^&]+)', full_url)
        color_name = color_match.group(1).replace('-', ' ') if color_match else None

        price = price_map.get(product_code)

        # Deduplicate and group by product_code
        if product_code not in products_dict:
            products_dict[product_code] = {
                "title": title,
                "product_code": product_code,
                "price": price,
                "base_url": full_url.split('?')[0],
                "available_colors": []
            }

        if color_name and color_name not in products_dict[product_code]["available_colors"]:
            products_dict[product_code]["available_colors"].append(color_name)

    unique_items = list(products_dict.values())

    return {
        "page_type": "PLP",
        "source": "dom_and_regex_deduplicated",
        "total_unique_items_found": len(unique_items),
        "items": unique_items
    }


if __name__ == "__main__":
    with open("jcrew_pdp.html", "r", encoding="utf-8") as f:
        html = f.read()

    url = "https://www.jcrew.com/plp/mens/categories/clothing/shirts/linen"
    result = parse_jcrew_html(html, page_url=url)
    print(json.dumps(result, indent=2))