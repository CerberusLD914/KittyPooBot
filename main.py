import os
import json
import time
import re

import undetected_chromedriver as uc

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

from Login import login


class KittyPooBot:
    def __init__(self):
        self.bot_json_path = "bot.json"

        self.profile_path = os.path.join(os.getcwd(), "chrome_profile")
        os.makedirs(self.profile_path, exist_ok=True)

        options = uc.ChromeOptions()
        options.add_argument(f"--user-data-dir={self.profile_path}")
        options.add_argument("--profile-directory=Default")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--headless=new")

        self.driver = uc.Chrome(
            options=options,
            version_main=146,
            use_subprocess=True
        )

        self.wait = WebDriverWait(self.driver, 30)

    # =========================
    # UTILIDADES
    # =========================

    def clear_console(self):
        os.system("cls" if os.name == "nt" else "clear")

    def render_status(self, lines):
        self.clear_console()
        print("=" * 86)
        print(" " * 33 + "KITTY POO BOT")
        print("=" * 86)
        for line in lines:
            print(line)
        print("=" * 86)

    def format_num(self, n):
        try:
            n = int(n)
        except Exception:
            return str(n)

        if n >= 1_000_000:
            return f"{n / 1_000_000:.2f}M"
        if n >= 1_000:
            return f"{n / 1_000:.2f}K"
        return str(n)

    def format_seconds(self, seconds):
        if seconds is None or seconds == float("inf"):
            return "∞"

        seconds = max(0, int(seconds))
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60

        if h > 0:
            return f"{h}h {m}m {s}s"
        if m > 0:
            return f"{m}m {s}s"
        return f"{s}s"

    def parse_compact_number(self, text):
        """
        Soporta:
        640        -> 640
        5.000      -> 5000
        35.000     -> 35000
        255.000    -> 255000
        1.1k       -> 1100
        1.2k       -> 1200
        2m         -> 2000000
        8 pcs      -> 8
        """
        if not text:
            return 0

        value = text.strip().lower()
        value = value.replace("💩", "").replace("🪙", "")
        value = value.replace("pcs", "").replace("/h", "")
        value = value.replace(" ", "")

        if value.endswith("k") or value.endswith("m"):
            suffix = value[-1]
            number_part = value[:-1].replace(",", ".")

            try:
                number = float(number_part)
            except Exception:
                digits = "".join(ch for ch in number_part if ch.isdigit())
                number = float(digits) if digits else 0.0

            if suffix == "k":
                return int(number * 1_000)
            if suffix == "m":
                return int(number * 1_000_000)

        if re.fullmatch(r"[\d\.]+", value):
            return int(value.replace(".", ""))

        digits = "".join(ch for ch in value if ch.isdigit())
        return int(digits) if digits else 0

    def safe_click(self, element):
        try:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                element
            )
            time.sleep(0.2)
            element.click()
            return True
        except Exception:
            try:
                ActionChains(self.driver).move_to_element(element).click().perform()
                return True
            except Exception:
                try:
                    self.driver.execute_script("arguments[0].click();", element)
                    return True
                except Exception:
                    return False

    # =========================
    # APERTURA
    # =========================

    def load_bot_json(self):
        if not os.path.exists(self.bot_json_path):
            raise FileNotFoundError(f"No existe el archivo {self.bot_json_path}")

        with open(self.bot_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError("bot.json no contiene un JSON válido.")

        return data

    def get_iframe_src(self):
        data = self.load_bot_json()
        iframe_src = data.get("iframe_src")

        if not iframe_src:
            raise ValueError("No se encontró 'iframe_src' en bot.json")

        iframe_src = iframe_src.strip()

        if not iframe_src.startswith("http"):
            raise ValueError(f"iframe_src no parece una URL válida: {iframe_src}")

        return iframe_src

    def open_game(self):
        iframe_src = self.get_iframe_src()

        self.driver.get(iframe_src)
        time.sleep(5)

        current_url = self.driver.current_url
        if current_url.startswith("about:blank") or current_url.startswith("data:"):
            self.driver.get(iframe_src)
            time.sleep(5)

        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        return iframe_src

    def wait_game_ready(self):
        try:
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "cat-profile-bar"))
            )
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "cat-poop-counter-text"))
            )
            return True
        except TimeoutException:
            return False

    # =========================
    # STATS DEL MENÚ PRINCIPAL
    # =========================

    def get_poo_stats(self):
        try:
            container = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "cat-poop-counter-text"))
            )

            poo_actual_text = container.find_element(
                By.CLASS_NAME, "cat-poop-number"
            ).text.strip()

            poo_rate_text = container.find_element(
                By.CLASS_NAME, "cat-poop-rate-num"
            ).text.strip()

            poo_actual = self.parse_compact_number(poo_actual_text)
            poo_rate_h = self.parse_compact_number(poo_rate_text)

            return {
                "poo_acumulado": poo_actual,
                "poo_rate_h": poo_rate_h
            }

        except Exception:
            return None

    def get_account_stats(self):
        try:
            profile_bar = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "cat-profile-bar"))
            )

            stat_values = profile_bar.find_elements(
                By.CLASS_NAME, "cat-profile-stat-value"
            )

            if len(stat_values) < 2:
                raise ValueError(
                    f"Se esperaban al menos 2 stats, encontrados: {len(stat_values)}"
                )

            coins_text = stat_values[0].text.strip()
            poo_total_text = stat_values[1].text.strip()

            coins_total = self.parse_compact_number(coins_text)
            poo_total = self.parse_compact_number(poo_total_text)

            return {
                "coins_total": coins_total,
                "poo_total": poo_total
            }

        except Exception:
            return None

    def refresh_main_stats(self):
        result = {
            "poo_acumulado": 0,
            "poo_rate_h": 0,
            "coins_total": 0,
            "poo_total": 0
        }

        poo_stats = self.get_poo_stats()
        account_stats = self.get_account_stats()

        if poo_stats:
            result.update(poo_stats)

        if account_stats:
            result.update(account_stats)

        return result

    # =========================
    # ACCIONES PRINCIPALES
    # =========================

    def CollectPoo(self):
        try:
            litter_img = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "img.cat-litter-img"))
            )
            return self.safe_click(litter_img)
        except Exception:
            return False

    def ReturnMainMenu(self):
        """
        Volver desde páginas internas al menú principal.
        En mercado el botón correcto usa mk-rug.
        """
        selectors = [
            "div.mk-rug[role='button']",
            "div.wd-rug[role='button']",
        ]

        for selector in selectors:
            try:
                btn = WebDriverWait(self.driver, 4).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                if self.safe_click(btn):
                    time.sleep(1.0)
                    # Confirmar que regresó al menú principal
                    if self.is_main_menu():
                        return True
            except Exception:
                continue

        # Intento extra por JS buscando cualquier botón de regreso visible
        try:
            clicked = self.driver.execute_script("""
                const selectors = ["div.mk-rug[role='button']", "div.wd-rug[role='button']"];
                for (const sel of selectors) {
                    const el = document.querySelector(sel);
                    if (el) {
                        el.click();
                        return true;
                    }
                }
                return false;
            """)
            if clicked:
                time.sleep(1.0)
                return self.is_main_menu()
        except Exception:
            pass

        return False

    def OpenMarket(self):
        try:
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "cat-action-item"))
            )

            buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.cat-action-item")
            for btn in buttons:
                try:
                    label = btn.find_element(By.CLASS_NAME, "cat-action-label").text.strip().lower()
                    if label == "mercado":
                        if self.safe_click(btn):
                            self.wait.until(
                                EC.presence_of_element_located((By.CLASS_NAME, "mk-list"))
                            )
                            return True
                except Exception:
                    continue

            return False
        except Exception:
            return False

    def is_main_menu(self):
        try:
            self.driver.find_element(By.CLASS_NAME, "cat-profile-bar")
            self.driver.find_element(By.CLASS_NAME, "cat-poop-counter-text")
            self.driver.find_element(By.CSS_SELECTOR, "button.cat-action-item")
            return True
        except Exception:
            return False

    def ensure_main_menu(self):
        if self.is_main_menu():
            return True

        for _ in range(3):
            if self.ReturnMainMenu():
                time.sleep(1.0)
                if self.is_main_menu():
                    return True

        return self.is_main_menu()

    # =========================
    # MERCADO
    # =========================

    def parse_market_items(self):
        items_data = []

        try:
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "mk-list"))
            )

            mk_items = self.driver.find_elements(By.CSS_SELECTOR, "div.mk-list div.mk-item")

            for idx, item in enumerate(mk_items):
                try:
                    name = item.find_element(By.CLASS_NAME, "mk-item-name").text.strip()

                    hourly_text = item.find_element(By.CLASS_NAME, "mk-item-hourly").text.strip()
                    hourly = self.parse_compact_number(hourly_text)

                    cost_text = item.find_element(
                        By.CSS_SELECTOR, ".mk-item-cost span"
                    ).text.strip()
                    cost = self.parse_compact_number(cost_text)

                    owned_text = item.find_element(By.CLASS_NAME, "mk-item-owned").text.strip()
                    owned = self.parse_compact_number(owned_text)

                    buy_btn = item.find_element(By.CLASS_NAME, "mk-buy-btn")
                    buy_text = buy_btn.text.strip().lower()

                    can_buy = "insuficiente" not in buy_text

                    items_data.append({
                        "index": idx,
                        "name": name,
                        "hourly": hourly,
                        "cost": cost,
                        "owned": owned,
                        "can_buy": can_buy,
                        "roi_hours": (cost / hourly) if hourly > 0 else float("inf"),
                    })
                except Exception:
                    continue

            return items_data

        except Exception:
            return []

    def choose_best_upgrade(self, items, poo_total_balance, poo_rate_h):
        """
        La compra se decide usando POO TOTAL.
        No entraremos al mercado hasta que toque revisar.
        """
        if not items:
            return None

        enriched = []

        for item in items:
            missing = max(0, item["cost"] - poo_total_balance)

            if poo_total_balance >= item["cost"]:
                wait_seconds = 0
            else:
                if poo_rate_h <= 0:
                    wait_seconds = float("inf")
                else:
                    wait_seconds = (missing / poo_rate_h) * 3600

            score = (
                round(item["roi_hours"], 6),
                0 if wait_seconds == 0 else 1,
                wait_seconds,
                item["cost"]
            )

            copy_item = dict(item)
            copy_item["missing_poo"] = missing
            copy_item["wait_seconds"] = wait_seconds
            copy_item["efficiency"] = (item["hourly"] / item["cost"]) if item["cost"] > 0 else 0
            copy_item["score"] = score
            enriched.append(copy_item)

        enriched.sort(key=lambda x: x["score"])
        return enriched[0]

    def buy_cat_by_index(self, idx):
        try:
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "mk-list")))
            items = self.driver.find_elements(By.CSS_SELECTOR, "div.mk-list div.mk-item")

            if idx >= len(items):
                return False

            item = items[idx]
            buy_btn = item.find_element(By.CLASS_NAME, "mk-buy-btn")

            if "insuficiente" in buy_btn.text.strip().lower():
                return False

            if not self.safe_click(buy_btn):
                return False

            confirm_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button.mk-modal-btn.mk-modal-btn-green")
                )
            )
            if not self.safe_click(confirm_btn):
                return False

            ok_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button.mk-modal-btn.mk-modal-btn-dark.mk-modal-btn-full")
                )
            )
            if not self.safe_click(ok_btn):
                return False

            time.sleep(1.0)
            return True

        except Exception:
            return False

    # =========================
    # SOPORTE DEL LOOP
    # =========================

    def collect_and_refresh(self):
        """
        Recolecta la caja para mover Poo actual a Poo total.
        """
        if not self.ensure_main_menu():
            return {
                "poo_acumulado": 0,
                "poo_rate_h": 0,
                "coins_total": 0,
                "poo_total": 0
            }

        before = self.refresh_main_stats()

        if before["poo_acumulado"] > 0:
            self.CollectPoo()
            time.sleep(1.2)

        after = self.refresh_main_stats()
        return after

    def countdown_on_main_menu(self, seconds, best=None, base_stats=None):
        """
        Espera en menú principal con contador descendente real.
        No analiza mercado aquí.
        """
        if base_stats is None:
            base_stats = self.refresh_main_stats()

        for remaining in range(int(seconds), -1, -1):
            self.ensure_main_menu()

            stats = self.refresh_main_stats()

            lines = [
                f"Poo actual         : {self.format_num(stats['poo_acumulado'])}",
                f"Poo total          : {self.format_num(stats['poo_total'])}",
                f"Poo por hora       : {self.format_num(stats['poo_rate_h'])}",
                f"Coins total        : {self.format_num(stats['coins_total'])}",
                ""
            ]

            if best:
                lines.extend([
                    f"Objetivo actual    : {best['name']}",
                    f"Costo objetivo     : {self.format_num(best['cost'])}",
                    f"Ganancia/h         : +{self.format_num(best['hourly'])}",
                    f"Falta aprox.       : {self.format_num(max(0, best['cost'] - stats['poo_total']))}",
                    ""
                ])

            lines.extend([
                "Estado             : Esperando próximo análisis",
                f"Próximo refresh    : {remaining}s"
            ])

            self.render_status(lines)

            if remaining > 0:
                time.sleep(1)

    # =========================
    # LOOP PRINCIPAL
    # =========================

    def main_loop(self):
        next_market_check_at = 0
        cached_best = None

        while True:
            # Siempre trabajar desde menú principal
            stats = self.collect_and_refresh()

            poo_actual = stats["poo_acumulado"]
            poo_rate_h = stats["poo_rate_h"]
            coins_total = stats["coins_total"]
            poo_total = stats["poo_total"]

            now = time.time()

            # Si aún no toca revisar mercado, esperar sin entrar
            if now < next_market_check_at:
                remaining = int(next_market_check_at - now)
                self.countdown_on_main_menu(
                    remaining,
                    best=cached_best,
                    base_stats=stats
                )
                continue

            # Toca revisar mercado
            self.render_status([
                f"Poo actual         : {self.format_num(poo_actual)}",
                f"Poo total          : {self.format_num(poo_total)}",
                f"Poo por hora       : {self.format_num(poo_rate_h)}",
                f"Coins total        : {self.format_num(coins_total)}",
                "",
                "Estado             : Analizando mercado..."
            ])

            if not self.ensure_main_menu():
                self.render_status([
                    "Estado             : No se pudo volver al menú principal",
                    "Acción             : Reintentando en 5s"
                ])
                time.sleep(5)
                continue

            market_ok = self.OpenMarket()
            if not market_ok:
                self.render_status([
                    f"Poo total          : {self.format_num(poo_total)}",
                    f"Poo por hora       : {self.format_num(poo_rate_h)}",
                    "",
                    "Estado             : No se pudo abrir Mercado",
                    "Acción             : Reintentando en 5s"
                ])
                time.sleep(5)
                continue

            time.sleep(1.0)

            items = self.parse_market_items()
            best = self.choose_best_upgrade(items, poo_total, poo_rate_h)
            cached_best = best

            if not best:
                self.render_status([
                    f"Poo total          : {self.format_num(poo_total)}",
                    f"Poo por hora       : {self.format_num(poo_rate_h)}",
                    "",
                    "Estado             : Mercado vacío o no legible",
                    "Acción             : Volviendo al menú principal"
                ])
                self.ReturnMainMenu()
                time.sleep(1.5)
                next_market_check_at = time.time() + 15
                continue

            panel_market = [
                f"Poo actual         : {self.format_num(poo_actual)}",
                f"Poo total          : {self.format_num(poo_total)}",
                f"Poo por hora       : {self.format_num(poo_rate_h)}",
                f"Coins total        : {self.format_num(coins_total)}",
                "",
                f"Próxima compra     : {best['name']}",
                f"Costo              : {self.format_num(best['cost'])}",
                f"Ganancia/h         : +{self.format_num(best['hourly'])}",
                f"Tienes             : {best['owned']}",
                f"ROI                : {best['roi_hours']:.2f} h",
                f"Falta              : {self.format_num(best['missing_poo'])}",
                f"Tiempo estimado    : {self.format_seconds(best['wait_seconds'])}",
                ""
            ]

            # No puede comprar ahora -> salir del mercado y programar próximo análisis
            if not best["can_buy"] or best["wait_seconds"] > 0:
                wait_seconds = int(best["wait_seconds"])
                wait_seconds = max(wait_seconds, 5)
                wait_seconds = min(wait_seconds, 60)

                panel_market.extend([
                    "Estado             : Aún no conviene/comprable",
                    "Acción             : Volviendo al menú principal",
                    f"Próximo refresh    : {wait_seconds}s"
                ])

                self.render_status(panel_market)

                returned = self.ReturnMainMenu()
                time.sleep(1.0)

                if not returned:
                    self.render_status(panel_market + ["", "Aviso              : No logró volver, reintentando..."])
                    self.ensure_main_menu()

                next_market_check_at = time.time() + wait_seconds
                continue

            # Sí puede comprar
            bought = self.buy_cat_by_index(best["index"])

            if bought:
                panel_market.append(f"Estado             : Comprado {best['name']}")
            else:
                panel_market.append(f"Estado             : Falló compra de {best['name']}")

            panel_market.append("Acción             : Regresando al menú principal")
            self.render_status(panel_market)

            time.sleep(1.5)
            returned = self.ReturnMainMenu()
            time.sleep(1.0)

            if not returned:
                self.ensure_main_menu()

            # Tras comprar, conviene revisar pronto otra vez
            next_market_check_at = time.time() + 5

    def close(self):
        try:
            self.driver.quit()
        except Exception:
            pass


def main():
    bot = None
    try:
        login()

        bot = KittyPooBot()
        bot.open_game()

        if not bot.wait_game_ready():
            raise Exception("El juego no cargó correctamente.")

        bot.main_loop()

    except KeyboardInterrupt:
        print("\n[INFO] Bot detenido manualmente.")
    except Exception as e:
        print(f"[ERROR GENERAL] {e}")
    finally:
        if bot:
            bot.close()


if __name__ == "__main__":
    main()