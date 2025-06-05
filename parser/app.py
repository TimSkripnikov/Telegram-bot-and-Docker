import os
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from sqlalchemy import (
    create_engine, Column, Integer, String, Text, DateTime, inspect, text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

Base = declarative_base()


class Weather(Base):
    __tablename__ = "weather"

    id = Column(Integer, primary_key=True)
    city = Column(String, nullable=False)
    info = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Currency(Base):
    __tablename__ = "currency"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    rate = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class DBUtils:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self._ensure_tables_exist()
        self.Session = sessionmaker(bind=self.engine)

    def _ensure_tables_exist(self):
        Base.metadata.create_all(self.engine)
        print("✅ Все необходимые таблицы созданы или уже существуют.")

    def clear_table(self, table_class):
        with self.engine.begin() as conn:
            conn.execute(text(f"TRUNCATE TABLE {table_class.__tablename__} RESTART IDENTITY"))
            print(f"🧹 Таблица '{table_class.__tablename__}' очищена.")

    def save_weather(self, data):
        session = self.Session()
        try:
            self.clear_table(Weather)
            for item in data:
                record = Weather(city=item["city"], info=item["info"])
                session.add(record)
            session.commit()
            print("✅ Погодные данные успешно сохранены.")
        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка при сохранении погоды: {e}")
        finally:
            session.close()

    def save_currency(self, data):
        session = self.Session()
        try:
            self.clear_table(Currency)
            for item in data:
                record = Currency(name=item["name"], rate=item["rate"])
                session.add(record)
            session.commit()
            print("✅ Курсы валют успешно сохранены.")
        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка при сохранении курсов валют: {e}")
        finally:
            session.close()


def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)


class WeatherParser:
    def __init__(self, url):
        self.url = url
        self.driver = None
        self.data = []

    def start(self):
        self.driver = create_driver()
        self.driver.get(self.url)
        time.sleep(3)

    def stop(self):
        if self.driver:
            self.driver.quit()

    def go_to_main_page(self):
        self.driver.get(self.url)
        time.sleep(3)

    def get_weather_info(self):
        try:
            info_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div[1]/p/span"))
            )
            return info_element.text.strip()
        except Exception as e:
            print(f"❌ Не удалось получить информацию о погоде: {e}")
            return "Информация не найдена"

    def fetch_data(self):
        self.start()

        cities = {
            "Барнаул": "/html/body/div[1]/div[2]/div[1]/div[3]/div[1]/ul[2]/li[4]/a",
            "Иркутск": "/html/body/div[1]/div[2]/div[1]/div[3]/div[1]/ul[8]/li[4]/a",
            "Красноярск": "/html/body/div[1]/div[2]/div[1]/div[3]/div[1]/ul[10]/li[18]/a",
            "Новосибирск": "/html/body/div[1]/div[2]/div[1]/div[3]/div[1]/ul[13]/li[16]/a",
            "Омск": "/html/body/div[1]/div[2]/div[1]/div[3]/div[2]/ul[1]/li[3]/a",
            "Томск": "/html/body/div[1]/div[2]/div[1]/div[3]/div[2]/ul[5]/li[6]/a",
            "Улан-Удэ": "/html/body/div[1]/div[2]/div[1]/div[3]/div[2]/ul[6]/li[2]/a"
        }

        for city, xpath in cities.items():
            print(f"🌆 Переход к городу: {city}")
            try:
                city_link = self.driver.find_element(By.XPATH, xpath)
                city_link.click()
                time.sleep(3)

                weather_info = self.get_weather_info()
                self.data.append({
                    "city": city,
                    "info": weather_info
                })

                self.go_to_main_page()
                time.sleep(3)
            except Exception as e:
                print(f"❌ Ошибка при обработке города {city}: {e}")

        self.stop()

    def save_to_db(self, db_utils):
        db_utils.save(self.data)


class CurrencyParser:
    def __init__(self, url):
        self.url = url
        self.driver = None
        self.data = []

    def start(self):
        self.driver = create_driver()
        self.driver.get(self.url)
        time.sleep(3)

    def stop(self):
        if self.driver:
            self.driver.quit()

    def fetch_data(self):
        self.start()

        currencies = {
            "Евро": "/html/body/main/div/div/div/div[3]/div/table/tbody/tr[16]",
            "Доллар": "/html/body/main/div/div/div/div[3]/div/table/tbody/tr[14]",
            "Тенге": "/html/body/main/div/div/div/div[3]/div/table/tbody/tr[36]",
            "Юань": "/html/body/main/div/div/div/div[3]/div/table/tbody/tr[44]"
        }

        for name, xpath in currencies.items():
            print(f"Получение курса для {name}")
            try:
                row = self.driver.find_element(By.XPATH, xpath)
                rate = row.find_elements(By.TAG_NAME, "td")[-1].text.strip()
                self.data.append({
                    "name": name,
                    "rate": rate
                })
            except Exception as e:
                print(f"Ошибка при получении курса для {name}: {e}")

        self.stop()

    def save_to_db(self, db_utils):
        db_utils.save_currency(self.data)

def main():
    db_utils = DBUtils()

    weather_parser = WeatherParser(url="https://world-weather.ru/pogoda/russia/")
    weather_parser.fetch_data()
    db_utils.save_weather(weather_parser.data)

    currency_parser = CurrencyParser(url="https://www.cbr.ru/currency_base/daily/")
    currency_parser.fetch_data()
    currency_parser.save_to_db(db_utils)


if __name__ == "__main__":
    main()
