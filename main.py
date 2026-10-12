import json
from playwright.sync_api import sync_playwright

def scrape_minfin_banks():
    # Валюти для збору: USD, EUR, PLN
    currencies = ["usd", "eur", "pln"]
    results = {}

    with sync_playwright() as p:
        # Запуск браузера у фоновому режимі
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        for curr in currencies:
            url = f"https://minfin.com.ua/ua/currency/banks/{curr}/"
            try:
                # Перехід на сторінку конкретної валюти в банках
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                
                # Очікування завантаження динамічної таблиці з банками та курсами
                page.wait_for_selector("table tbody tr", timeout=15000)
                
                banks_data = []
                rows = page.query_selector_all("table tbody tr")

                for row in rows:
                    cols = row.query_selector_all("td")
                    # Перевіряємо наявність колонок (назва банку, купівля, продаж)
                    if len(cols) >= 3:
                        bank_name = cols[0].inner_text().strip().split("\n")[0]
                        buy_rate = cols[1].inner_text().strip().replace("\n", " ")
                        sell_rate = cols[2].inner_text().strip().replace("\n", " ")

                        if bank_name and buy_rate and sell_rate:
                            banks_data.append({
                                "bank": bank_name,
                                "buy": buy_rate,
                                "sell": sell_rate
                            })

                results[curr.upper()] = {
                    "currency": curr.upper(),
                    "banks_count": len(banks_data),
                    "rates": banks_data
                }

            except Exception as e:
                print(f"Помилка при обробці {curr.upper()}: {e}")

        browser.close()

    # Збереження зібраних даних у структурований JSON-файл
    with open("minfin_banks_rates.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print("Збір даних завершено. Результат збережено у 'minfin_banks_rates.json'")

if __name__ == "__main__":
    scrape_minfin_banks()