import requests
from bs4 import BeautifulSoup
import json

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

url = "https://www.liogames.com/product/mobile-legends/"
html = session.get(url).text
soup = BeautifulSoup(html, "html.parser")

form_tag = soup.find("form", {"class": "variations_form"})

if form_tag and form_tag.has_attr("data-product_variations"):
    variations_json = form_tag["data-product_variations"]
    variations = json.loads(variations_json)

    # پیدا کردن کلید attribute واقعی (مثلاً attribute_pa_diamond یا هرچی باشه)
    attribute_keys = set()
    for v in variations:
        attribute_keys.update(v.get("attributes", {}).keys())
    print("🔑 Attribute Keys Found:", attribute_keys)

    # مپ کردن slug ها به متن واقعی
    name_map = {}
    for select in form_tag.find_all("select"):
        for opt in select.find_all("option"):
            if opt.get("value"):
                name_map[opt["value"]] = opt.text.strip()

    # محصولات هدف
    target_names = [
        "Diamond×156 +16",
        "Diamond×234 +23",
        "Diamond×625 +81",
        "Diamond×1860 +335",
        "Twilight Passage",
        "Diamond Weekly Pass"
    ]

    # نمایش فقط محصولات هدف
    print("\n🎯 Target Products & Prices:")
    for var in variations:
        attr_value = None
        for key in attribute_keys:  # اولین کلید موجود رو بگیریم
            attr_value = var.get("attributes", {}).get(key)
            if attr_value:
                break
        price = var.get("display_price")
        name = name_map.get(attr_value, attr_value)
        if name in target_names and price:
            print(f"- {name} → {price}$")
else:
    print("❌ JSON مربوط به قیمت‌ها پیدا نشد!")
