from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import sys
import re
 
 
# تشغيل المتصفح
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

url = "https://www.google.com/maps/search/بنزينات+القاهرة/"
driver.get(url)
time.sleep(5)

# تحديد الكروت
cards_xpath = '//div[contains(@class,"lI9IFe")]'

# نحدد الـ scrollable container الصح
scrollable_div = driver.find_element(
    By.XPATH, '//div[contains(@class,"m6QErb") and contains(@class,"DxyBCb") and @role="feed"]'
)


last_count = 0
same_rounds = 0

while True:

    cards = driver.find_elements(By.XPATH, cards_xpath)

    if cards:
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight",scrollable_div)
 
    time.sleep(3)

    cards = driver.find_elements(By.XPATH, cards_xpath)
    current_count = len(cards)

    print(f"✅ تم تحميل {current_count} كارت")

    if current_count == last_count:
        same_rounds += 1
    else:
        same_rounds = 0

    if same_rounds >= 7:
        print("⛔ لا توجد نتائج جديدة")
        break

    last_count = current_count


print (len(cards))
data = []
for idx, card in enumerate(cards, start=1):
        try:
            code = None
            ActionChains(driver).move_to_element(card).click().perform()
            time.sleep(5)  # وقت تحميل الكارت

            # الاسم بالإنجليزية
            try:
                English_name = driver.find_element(By.XPATH, '//h1[contains(@class,"DUwDvf")]').text
                print(f"   الاسم بالإنجليزية: {English_name}")
            except:
                English_name = None

            # الاسم بالعربية
            try:
                Arabic_name = driver.find_element(By.XPATH, "//h2[contains(@class,'bwoZTb')]").text
                print(f"   الاسم بالعربية: {Arabic_name}")
            except:
                Arabic_name = English_name # لو مفيش اسم عربي، نستخدم الإنجليزي

            # الهاتف
            try:
                phone = driver.find_element(By.XPATH, "//button[contains(@data-item-id,'phone')]").text
                print(f"   الهاتف: {phone}")
            except:
                phone = None

            # العنوان
            try:
                address = driver.find_element(By.XPATH, "//button[contains(@data-item-id,'address')]").text
                print(f"   العنوان: {address}")

                match = re.search(r"(\d+)$", address.strip())
                code = match.group(1) if match else None
                print(code)
            except:
                address = None

            # الموقع الإلكتروني
            try:
                website = driver.find_element(By.XPATH, "//a[contains(@data-item-id,'authority')]").get_attribute("href")
                print(f"   الموقع الإلكتروني: {website}")
            except:
                website = None

            # موقع الخريطة (إحداثيات تقريبية)
            try:
                location = driver.find_element(By.XPATH, "//button[contains(@data-item-id,'oloc')]").text
                print(f"   الموقع: {location}")
            except:
                location = None

            # التقييم
            try:
                rating = driver.find_element(By.XPATH, "//div[contains(@class,'fontDisplayLarge')]").text
                print(f"   التقييم: {rating}")
            except:
                rating = None

            try:
                reviews = driver.find_element(By.XPATH, "//button[contains(@class,'QjSyb')]//span").text
                print(f"   عدد التقييمات: {reviews}")
            except:
                reviews = None

            try:
                sub_category = driver.find_element(By.XPATH, "//button[contains(@class,'DkEaL')]").text
                print(f"   الفئة الفرعية: {sub_category}")
            except:
                sub_category = None

            try:
                img_element = driver.find_element(By.XPATH, "//img[contains(@decoding,'async')]")
                img_url = img_element.get_attribute("src")
                print(f"   صورة: {img_url}")
            except:
                img_url = None

            # إضافة البيانات للقائمة
            data.append({
                "City": "Cairo",
                "Category": "Gas Stations",
                "Sub Category": sub_category,
                "English Name": English_name,
                "Arabic Name": Arabic_name,
                "Rating": rating,
                "Reviews": reviews,
                "Address": address,
                "Postal Code":code,
                "Location": location,
                "Phone": phone,
                "Website": website,
                "Image URL": img_url
            })

        except Exception as e:
            print(f"⚠️ مشكلة مع الكارت {idx}: {e}")
            continue


df = pd.DataFrame(data)

df.to_csv(r"D:\Maged\Courses\Data Engineering\Lec2\Urban Services Intelligence\Data Sources\gas_stations.csv", index=False, encoding="utf-8")

driver.quit()
print("🎉 تم حفظ البيانات التفصيلية في gas_stations_cairo_details.csv")
