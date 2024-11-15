import base64
import pprint

import httpx
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time


# /root/.local/share/undetected_chromedriver/undetected_chromedriver

def selenium_modified_del(self):
    try:
        self.service.process.kill()
    except Exception:
        pass
    try:
        self.quit()
    except OSError:
        pass


uc.Chrome.__del__ = selenium_modified_del


# Функция для получения HTML данных страницы
def get_html_data(url, time_sleep=5):
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')

    driver = uc.Chrome(options=chrome_options)
    html_content = ""

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )

        time.sleep(time_sleep)
        html_content = driver.page_source

    except Exception as e:
        print(f"Ошибка при сборе данных: {e}")

    finally:
        driver.quit()

    return html_content


# Custom deletion to avoid lingering processes in undetected_chromedriver
def selenium_modified_del(self):
    try:
        self.service.process.kill()
    except Exception:
        pass
    try:
        self.quit()
    except OSError:
        pass


uc.Chrome.__del__ = selenium_modified_del


# Function to retrieve HTML data from a page after a button click
def get_html_after_click(url, button_selector, time_sleep=5):
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')

    driver = uc.Chrome(options=chrome_options)
    html_content = ""

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        # Click button if exists to load additional details
        button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, button_selector)))
        button.click()
        time.sleep(time_sleep)
        html_content = driver.page_source

    except Exception as e:
        print(f"Error collecting data: {e}")

    finally:
        driver.quit()

    return html_content


# Function to parse Wildberries product details
def parse_html_wb(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract full product description
    description_element = soup.find("section", class_="product-details__description option")
    description = description_element.find("p",
                                           class_="option__text").text.strip() if description_element else "Description not found."
    name = soup.find("h1", class_="product-page__title")
    # Extract characteristics from tables
    characteristics = {}
    tables = soup.find_all("table", class_="product-params__table")
    for table in tables:
        caption = table.find("caption").text if table.find("caption") else "Other Characteristics"
        characteristics[caption] = {}
        for row in table.find_all("tr", class_="product-params__row"):
            cells = row.find_all("td", class_="product-params__cell")
            if len(cells) == 2:
                key = cells[0].text.strip()
                value = cells[1].text.strip()
                characteristics[caption][key] = value

    # Extract all product images
    images = []
    img_tags = soup.select('ul.swiper-wrapper img')
    for img in img_tags:
        if img and "src" in img.attrs:
            images.append(img["src"])

    return {
        'name': name,
        "description": description,
        "characteristics": characteristics,
        "images": images
    }


# Function to parse Ozon product details
def parse_html_ozon(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    description_element = soup.find("div", class_="RA-a1")
    description = description_element.text.strip() if description_element else "Description not found."
    name = soup.find("h1", class_='um_27 tsHeadline550Medium')
    images = []
    img_index = 1
    while True:
        img_tag = soup.find("div", {"data-index": str(img_index)})
        if img_tag:
            img = img_tag.find("img")
            if img and "src" in img.attrs:
                images.append(img["src"])
            img_index += 1
        else:
            break

    return {
        "name": name,
        "description": description,
        "images": images
    }


# Main function to collect data from Ozon or Wildberries
def collect_product_data(url):
    if "ozon.ru" in url:
        html_content = get_html_data(url)
        product_data = parse_html_ozon(html_content)
    elif "wildberries.ru" in url:
        button_selector = 'button.product-page__btn-detail.hide-mobile.j-details-btn-desktop'
        html_content = get_html_after_click(url, button_selector)
        product_data = parse_html_wb(html_content)
    else:
        return {"error": "Unknown marketplace"}

    # Форматируем описание продукта
    description_text = f"Описание продукта:\n{product_data['description']}"

    # Форматируем характеристики продукта (если доступны)
    characteristics_text = "Характеристики продукта:\n"
    if "characteristics" in product_data:
        characteristics_text += "\n".join(
            [f"{key}: {value}" for key, value in product_data["characteristics"].items()]
        )
    else:
        characteristics_text += "Нет информации о характеристиках."

    # Форматируем ссылки на изображения продукта
    images = product_data["images"][:6] if "images" in product_data else []
    name = product_data['name']
    if name == None:
        name = product_data['name']
    else:
        name = product_data['name'].text
    # Возвращаем структурированную информацию в виде словаря
    return {
        'name': name,
        "description": description_text,
        "images": images
    }


# if __name__ == '__main__':
#     url_wb = 'https://www.ozon.ru/product/razer-igrovaya-mysh-provodnaya-basilisk-v3-chernyy-584788836/?campaignId=439'
#     data = collect_product_data(url_wb)
#     pprint.pprint(data)

# Example usage for both marketplaces
# url_ozon = 'https://www.ozon.ru/product/scovo-nabor-ekspert-kastryulya-s-kryshkoy-24-sm-kovsh-s-kryshkoy-18-sm-1705564488/'
# url_wb = 'https://www.wildberries.ru/catalog/118154002/detail.aspx'




