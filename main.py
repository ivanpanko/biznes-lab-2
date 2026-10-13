
import json
from playwright.sync_api import sync_playwright


def scrape_minfin_banks():
    currencies = ["usd", "eur", "pln"]
    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            
        )
        page = context.new_page()

        for curr in currencies:
            url = f"https://minfin.com.ua/ua/currency/banks/{curr}/"

            try:
                page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=60000
                )

                page.wait_for_selector(
                    "table tbody tr",
                    timeout=15000
                )

                banks_data = []
                rows = page.query_selector_all("table tbody tr")

                for row in rows:
                    cols = row.query_selector_all("td")

                    if len(cols) < 3:
                        continue

                    bank_name = (
                        cols[0].inner_text()
                        .strip()
                        .split("\n")[0]
                    )

                    cash_rates = (
                        cols[1].inner_text()
                        .strip()
                        .replace("\n", " ")
                    )

                    card_rates = (
                        cols[2].inner_text()
                        .strip()
                        .replace("\n", " ")
                    )

                    def split_rates(value):
                        parts = [part.strip() for part in value.split("/")]

                        if len(parts) != 2:
                            parts = [value.strip(), "-"]

                        buy, sell = parts

                        invalid_values = {"", "-", "—", "–"}

                        if buy in invalid_values:
                            buy = None

                        if sell in invalid_values:
                            sell = None

                        return buy, sell

                    cash_buy, cash_sell = split_rates(cash_rates)
                    card_buy, card_sell = split_rates(card_rates)

                    bank_data = {"bank": bank_name}

                    if cash_buy is not None:
                        bank_data["cash_buy"] = cash_buy

                    if cash_sell is not None:
                        bank_data["cash_sell"] = cash_sell

                    if card_buy is not None:
                        bank_data["card_buy"] = card_buy

                    if card_sell is not None:
                        bank_data["card_sell"] = card_sell

                    if bank_name and len(bank_data) > 1:
                        banks_data.append(bank_data)

                results[curr.upper()] = {
                    "currency": curr.upper(),
                    "banks_count": len(banks_data),
                    "rates": banks_data
                }

            except Exception as e:
                print(f"Помилка при обробці {curr.upper()}: {e}")

        browser.close()

    with open("minfin_banks_rates.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print(
        "Збір даних завершено. "
        "Результат збережено у 'minfin_banks_rates.json'"
    )


if __name__ == "__main__":
    scrape_minfin_banks()
