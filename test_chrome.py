from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# اجرای مرورگر کروم
driver = webdriver.Chrome()

# باز کردن سایت مورد نظر
driver.get("https://caliph.dev/projects/mobile-legends-id-checker")

# چند ثانیه صبر کن تا صفحه کامل لود بشه
time.sleep(5)

print("✅ صفحه باز شد:", driver.title)

# بستن مرورگر
driver.quit()
