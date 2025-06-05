# Telegram Weather & Currency Bot

This project is a **Telegram bot** that allows users to get **up-to-date weather** and **currency exchange rates** for selected Russian cities and currencies. The system consists of two main components:

* A **parser service** that fetches data and populates a PostgreSQL database.
* A **Telegram bot service** that interacts with users and serves the latest data.

The entire application is containerized using **Docker**, and the services are connected via a shared Docker network.


## Installation
```bash
git clone https://github.com/TimSkripnikov/Telegram-bot-and-Docker.git
```

## Used Libraries

- ![pyTelegramBotAPI](https://pytba.readthedocs.io/en/latest/_images/logo.png) [**pyTelegramBotAPI**](https://github.com/eternnoir/pyTelegramBotAPI) — a wrapper for the Telegram Bot API.
- ![SQLAlchemy](https://seeklogo.com/images/S/sqlalchemy-logo-488283/vector-logo.png) [**SQLAlchemy**](https://www.sqlalchemy.org/) — the Python SQL toolkit and ORM.
- ![python-dotenv](https://raw.githubusercontent.com/theskumar/python-dotenv/master/docs/_static/logo.png) [**python-dotenv**](https://github.com/theskumar/python-dotenv) — reads key-value pairs from `.env` files and sets them as environment variables.
- ![psycopg2](https://www.psycopg.org/images/psycopg-logo.png) [**psycopg2-binary**](https://www.psycopg.org/) — a PostgreSQL adapter for Python.
- ![Selenium](https://seeklogo.com/images/S/selenium-logo-456125/vector-logo.png) [**selenium**](https://www.selenium.dev/) — a browser automation framework.
- ![urllib3](https://raw.githubusercontent.com/urllib3/urllib3/main/docs/_static/urllib3-logo.png) [**urllib3**](https://github.com/urllib3/urllib3) — a powerful, user-friendly HTTP client for Python.


## Usage



### 1. Copy the .env files from the templates before running:

```bash
cp .env.example .env
cp bot/.env.example bot/.env
cp parser/.env.example parser/.env
```
### 2. How to Get a Telegram Bot Token

- Open the Telegram app and search for the user [@BotFather](https://t.me/BotFather).

- Start a chat with BotFather by clicking **Start** or sending `/start`.

- To create a new bot, send the command:

   ```
   /newbot
   ```

- Follow the instructions:

   * Choose a **name** for your bot (this will be displayed to users).
   * Choose a unique **username** for your bot, which must end with `bot` (e.g., `weather_helper_bot`).

- After successful creation, BotFather will send you a message containing your bot **token**. It looks like this:

   ```
   123412345:ABCdefGhIJKlmfghjkgUvWXyz1234567890
   ```

- Copy this token and use it in `/bot/.env` file as the value for `BOT_TOKEN`.

### 3. Start with the help of docker compose:
```bash
docker compose up --build
```


## Data Flow

### 1. Parsing Service (`/parser`)

* **Weather** is scraped from trusted online sources (e.g., weather websites) for a list of predefined Russian cities.
* **Currency exchange rates** (USD, EUR, CNY, KZT) are also scraped from financial or banking sites.
* Parsed data is stored into the PostgreSQL database, in two tables:

  * `weather`: contains city name, info, and timestamp.
  * `currency`: contains currency name, exchange rate, and timestamp.
* The parser is intended to be run on a schedule (e.g., via cron or Docker job).

### 2. Telegram Bot (`/bot`)

* Listens for user interactions using long polling.
* Reads weather and currency data from the same PostgreSQL database.
* Sends formatted messages in response to user input.



## Bot Functionality

### Main Menu (`/start` or `/menu`)

The bot provides an inline keyboard with two main options:

```
🔘 Choose an action:
[🌆 Weather]  [💱 Currencies]
```



### Weather Mode

* After clicking "🌆 Weather", the user is shown a list of cities:

  ```
  📍 Choose a city:
  [Новосибирск] [Томск]
  [Красноярск]  [Барнаул]
  [Иркутск]     [Омск]
  [Улан-Удэ]
  ```
* Upon selecting a city, the bot fetches the **latest weather** record for that city from the `weather` table and sends it.
* If data is not available, the bot informs the user.



### Currency Mode

* After clicking "💱 Currencies", the user is shown a list of currencies:

  ```
  💱 Choose a currency:
  [Доллар] [Евро]
  [Юань]   [Тенге]
  ```
* After choosing a currency, the bot fetches the **latest exchange rate** from the `currency` table.
* The user receives a message like:

  ```
  💱 Доллар → 89.12 ₽
  ```


