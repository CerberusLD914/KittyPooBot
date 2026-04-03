import os
import time
import json
import undetected_chromedriver as uc

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class TelegramBrowser:
    def __init__(self):
        self.profile_path = os.path.abspath("chrome_profile")
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

        self.wait = WebDriverWait(self.driver, 25)

    def open(self):
        self.driver.get("https://web.telegram.org/k/")
        time.sleep(5)

    def close(self):
        try:
            self.driver.quit()
        except:
            pass

    def current_url(self):
        try:
            return self.driver.current_url
        except:
            return ""

    def print_current_page_info(self):
        try:
            print(f"🌐 URL actual: {self.current_url()}")
            print(f"📄 Título actual: {self.driver.title}")
        except:
            print("⚠️ No fue posible obtener información de la página actual.")

    def is_logged_in(self):
        try:
            self.driver.find_element(
                By.CSS_SELECTOR,
                "div.sidebar-header.main-search-sidebar-header"
            )
            self.driver.find_element(
                By.CSS_SELECTOR,
                "div.input-search.old-style input.input-search-input"
            )
            return True
        except:
            return False

    def find_login_button(self):
        try:
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for btn in buttons:
                try:
                    text = btn.text.strip().lower()
                    if "log in by phone number" in text:
                        return btn
                except:
                    pass
            return None
        except:
            return None

    def is_phone_page(self):
        try:
            subtitles = self.driver.find_elements(By.CSS_SELECTOR, "div.subtitle.text-center.i18n")
            for sub in subtitles:
                try:
                    text = (sub.text or "").strip().lower()
                    if "please confirm your country code" in text and "enter your phone number" in text:
                        return True
                except:
                    pass
            return False
        except:
            return False

    def click_login_by_phone(self):
        btn = self.find_login_button()
        if btn:
            print("⚠️ La sesión no está iniciada.")
            print("✅ Botón 'Log in by phone number' encontrado. Haciendo click...")
            self.driver.execute_script("arguments[0].click();", btn)
            return True
        return False

    def get_phone_input(self):
        selector = (
            "div.input-field-input[contenteditable='true']"
            "[dir='auto']"
            "[data-no-linebreaks='1']"
            "[inputmode='decimal']"
        )

        return self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )

    def get_phone_input_text(self):
        phone_input = self.get_phone_input()

        try:
            text = (phone_input.text or "").strip()
        except:
            text = ""

        if not text:
            try:
                text = self.driver.execute_script(
                    "return (arguments[0].innerText || arguments[0].textContent || '').trim();",
                    phone_input
                ) or ""
            except:
                text = ""

        return text.strip()

    def clear_contenteditable(self, element):
        self.driver.execute_script("arguments[0].focus();", element)
        time.sleep(0.3)

        try:
            element.send_keys(Keys.CONTROL, "a")
            time.sleep(0.2)
            element.send_keys(Keys.DELETE)
            time.sleep(0.3)
        except:
            pass

        try:
            self.driver.execute_script("""
                arguments[0].innerHTML = '';
                arguments[0].innerText = '';
                arguments[0].textContent = '';
                arguments[0].dispatchEvent(new Event('input', {bubbles:true}));
                arguments[0].dispatchEvent(new Event('change', {bubbles:true}));
            """, element)
        except:
            pass

        time.sleep(0.4)

    def set_phone_number(self):
        phone_input = self.get_phone_input()
        current_text = self.get_phone_input_text()

        print(f"ℹ️ Contenido actual del input del teléfono: '{current_text}'")

        has_plus55 = "+55" in current_text
        has_any_plus = "+" in current_text

        self.driver.execute_script("arguments[0].focus();", phone_input)
        time.sleep(0.5)

        if has_plus55:
            print("✅ El input ya contiene +55.")
            phone = input("Ingresa tu número SIN +55, solo lo que viene después: ").strip()
            phone = "".join(ch for ch in phone if ch.isdigit())

            try:
                phone_input.send_keys(phone)
            except:
                self.driver.execute_script("""
                    arguments[0].focus();
                    arguments[0].innerText = arguments[1];
                    arguments[0].dispatchEvent(new Event('input', {bubbles:true}));
                    arguments[0].dispatchEvent(new Event('change', {bubbles:true}));
                """, phone_input, f"+55{phone}")

            time.sleep(1)
            final_text = self.get_phone_input_text()
            print(f"✅ Número colocado: {final_text}")
            return

        if not has_any_plus:
            print("⚠️ El input no contiene ningún '+' visible.")
            phone = input("Ingresa el número COMPLETO con prefijo, por ejemplo +5511999999999: ").strip()

            self.clear_contenteditable(phone_input)
            self.driver.execute_script("arguments[0].focus();", phone_input)
            time.sleep(0.5)

            try:
                phone_input.send_keys(phone)
            except:
                self.driver.execute_script("""
                    arguments[0].focus();
                    arguments[0].innerText = arguments[1];
                    arguments[0].dispatchEvent(new Event('input', {bubbles:true}));
                    arguments[0].dispatchEvent(new Event('change', {bubbles:true}));
                """, phone_input, phone)

            time.sleep(1)
            final_text = self.get_phone_input_text()
            print(f"✅ Número colocado: {final_text}")
            return

        print("⚠️ El input tiene un '+' pero no es +55.")
        phone = input("Ingresa el número COMPLETO con prefijo, por ejemplo +5511999999999: ").strip()

        self.clear_contenteditable(phone_input)
        self.driver.execute_script("arguments[0].focus();", phone_input)
        time.sleep(0.5)

        try:
            phone_input.send_keys(phone)
        except:
            self.driver.execute_script("""
                arguments[0].focus();
                arguments[0].innerText = arguments[1];
                arguments[0].dispatchEvent(new Event('input', {bubbles:true}));
                arguments[0].dispatchEvent(new Event('change', {bubbles:true}));
            """, phone_input, phone)

        time.sleep(1)
        final_text = self.get_phone_input_text()
        print(f"✅ Número colocado: {final_text}")

    def click_next(self):
        buttons = self.driver.find_elements(By.TAG_NAME, "button")

        for btn in buttons:
            try:
                text = btn.text.strip().lower()
                if text == "next":
                    self.driver.execute_script("arguments[0].click();", btn)
                    print("✅ Click en Next")
                    return True
            except:
                pass

        raise TimeoutException("No se encontró el botón Next.")

    def get_code_input(self):
        selectors = [
            "div._wrap_87tyg_1 input",
            "input[autocomplete='one-time-code']",
            "input[inputmode='numeric']"
        ]

        for selector in selectors:
            try:
                return self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
            except:
                pass

        raise TimeoutException("No se encontró el input del código de confirmación.")

    def set_confirmation_code(self, code):
        code = "".join(ch for ch in code if ch.isdigit())

        code_input = self.get_code_input()
        self.driver.execute_script("arguments[0].focus();", code_input)
        time.sleep(0.5)

        try:
            code_input.clear()
        except:
            pass

        code_input.send_keys(code)
        print(f"✅ Código colocado: {code}")

    def ensure_correct_page_state(self):
        self.print_current_page_info()

        if self.is_logged_in():
            print("✅ La sesión ya está iniciada.")
            return True, "logged"

        btn = self.find_login_button()
        if btn:
            print("⚠️ Se detectó la pantalla inicial con botón de login por teléfono.")
            return True, "login_button"

        if self.is_phone_page():
            print("✅ Ya estás en la página donde se pone el número de teléfono.")
            return True, "phone_page"

        print("⚠️ No se reconoció claramente la pantalla actual.")
        return False, "unknown"

    def login_flow(self):
        while True:
            self.open()

            ok, state = self.ensure_correct_page_state()

            if state == "logged":
                return True

            if state == "login_button":
                clicked = self.click_login_by_phone()
                if not clicked:
                    print("❌ No se pudo hacer click en el botón de login.")
                    time.sleep(3)
                    continue

                print("⏳ Esperando 5 segundos a que cargue la pantalla del teléfono...")
                time.sleep(5)

            elif state == "phone_page":
                print("ℹ️ Ya estabas directamente en la pantalla del número de teléfono.")

            else:
                print("🔄 Recargando la página para intentar reconocer el estado...")
                self.driver.refresh()
                time.sleep(5)

                ok, state = self.ensure_correct_page_state()

                if state == "logged":
                    return True

                if state == "login_button":
                    clicked = self.click_login_by_phone()
                    if not clicked:
                        print("❌ No se pudo hacer click en el botón tras recargar. Reintentando...")
                        time.sleep(3)
                        continue
                    print("⏳ Esperando 5 segundos a que cargue la pantalla del teléfono...")
                    time.sleep(5)

                elif state != "phone_page":
                    print("❌ No fue posible identificar la pantalla correcta. Reintentando desde cero...")
                    time.sleep(3)
                    continue

            try:
                self.get_phone_input()
                print("✅ Input del teléfono detectado correctamente.")
            except:
                print("❌ No se detectó el input del teléfono. Reintentando...")
                time.sleep(3)
                continue

            self.set_phone_number()
            time.sleep(1)
            self.click_next()

            print("⏳ Esperando 3 segundos antes de pedir el código...")
            time.sleep(3)

            code = input("Ingresa el código de confirmación: ").strip()
            self.set_confirmation_code(code)

            print("⏳ Esperando validación del login...")
            time.sleep(6)

            if self.is_logged_in():
                print("✅ Se inició sesión correctamente.")
                return True

            print("❌ No se confirmó el inicio de sesión. Reintentando todo...")
            time.sleep(3)

    def open_golden_miner_bot(self):
        print("🤖 Abriendo Bot...")
        self.driver.get("https://web.telegram.org/k/#@KittyPooBot")
        time.sleep(5)
        self.driver.refresh()
        time.sleep(5)

    def click_start_button(self):
        print("🔎 Buscando botón Start...")

        selectors = [
            "div.new-message-bot-commands-view",
            "div.new-message-bot-commands.is-view",
        ]

        end_time = time.time() + 20
        while time.time() < end_time:
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for el in elements:
                        text = (el.text or "").strip().lower()
                        if text == "catpoo":
                            self.driver.execute_script("arguments[0].click();", el)
                            print("✅ Click en play")
                            time.sleep(3)
                            return True
                except:
                    pass
            time.sleep(1)

        print("⚠️ No se encontró el botón play.")
        return False

    def click_launch_if_popup_exists(self):
        print("🔎 Verificando si apareció popup de Launch...")

        end_time = time.time() + 12
        while time.time() < end_time:
            try:
                popups = self.driver.find_elements(By.CSS_SELECTOR, "div.popup-container")
                for popup in popups:
                    popup_text = (popup.text or "").strip().lower()
                    if "to launch this web app" in popup_text:
                        buttons = popup.find_elements(By.TAG_NAME, "button")
                        for btn in buttons:
                            btn_text = (btn.text or "").strip().lower()
                            if btn_text == "launch":
                                self.driver.execute_script("arguments[0].click();", btn)
                                print("✅ Click en Launch")
                                time.sleep(5)
                                return True
            except:
                pass
            time.sleep(1)

        print("ℹ️ No apareció popup de Launch.")
        return False

    def wait_for_webapp_open(self, timeout=25):
        print("⏳ Esperando a que la WebApp se abra...")

        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                iframe = self.driver.find_element(By.CSS_SELECTOR, "iframe.payment-verification, iframe[src*='tgWebApp']")
                src = iframe.get_attribute("src") or ""
                if src:
                    print("✅ WebApp detectada.")
                    print("ℹ️ Iframe detectado correctamente.")
                    return True
            except:
                pass
            time.sleep(1)

        print("⚠️ No se detectó la WebApp dentro del tiempo esperado.")
        return False

    def get_webapp_iframe_src(self):
        selectors = [
            "iframe.payment-verification",
            "iframe[src*='tgWebApp']",
            "iframe"
        ]

        for selector in selectors:
            try:
                iframes = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for iframe in iframes:
                    try:
                        src = iframe.get_attribute("src") or ""
                        if src and ("tgWebAppData=" in src or "tgWebAppVersion=" in src):
                            return src
                    except:
                        pass
            except:
                pass

        return None

    def save_webapp_url(self, file_path="golden_miner_webapp_url.txt"):
        print("💾 Intentando guardar la URL del iframe de la WebApp...")

        src = self.get_webapp_iframe_src()
        if not src:
            print("❌ No se encontró una URL válida del iframe.")
            return False

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(src)

            print(f"✅ URL guardada en: {os.path.abspath(file_path)}")
            print(f"🔗 URL detectada:\n{src}")
            return True
        except Exception as e:
            print(f"❌ Error guardando la URL: {e}")
            return False

    def save_webapp_iframe_html(self, file_path="golden_miner_iframe.html"):
        print("💾 Intentando guardar el iframe completo...")

        selectors = [
            "iframe.payment-verification",
            "iframe[src*='tgWebApp']",
            "iframe"
        ]

        for selector in selectors:
            try:
                iframes = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for iframe in iframes:
                    try:
                        src = iframe.get_attribute("src") or ""
                        iframe_class = iframe.get_attribute("class") or ""
                        sandbox = iframe.get_attribute("sandbox") or ""
                        allow = iframe.get_attribute("allow") or ""
                        style = iframe.get_attribute("style") or ""
                        allowfullscreen = iframe.get_attribute("allowfullscreen")

                        if src and ("tgWebAppData=" in src or "tgWebAppVersion=" in src):
                            iframe_html = (
                                f'<iframe src="{src}" '
                                f'sandbox="{sandbox}" '
                                f'allow="{allow}" '
                                f'class="{iframe_class}" '
                                f'allowfullscreen="{allowfullscreen if allowfullscreen is not None else ""}" '
                                f'style="{style}"></iframe>'
                            )

                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(iframe_html)

                            print(f"✅ Iframe completo guardado en: {os.path.abspath(file_path)}")
                            return True
                    except:
                        pass
            except:
                pass

        print("❌ No se pudo guardar el iframe completo.")
        return False

    def save_webapp_data_json(self, file_path="golden_miner_webapp_data.json"):
        print("💾 Guardando datos de la WebApp en JSON...")

        src = self.get_webapp_iframe_src()
        if not src:
            print("❌ No se encontró src del iframe.")
            return False

        data = {
            "bot": "KittyPooBot",
            "iframe_src": src,
            "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "telegram_url": self.current_url()
        }

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            print(f"✅ JSON guardado en: {os.path.abspath(file_path)}")
            return True
        except Exception as e:
            print(f"❌ Error guardando JSON: {e}")
            return False


def login():
    if os.path.exists("bot.json"):
        os.remove("bot.json")
    bot = TelegramBrowser()
    try:
        logged = bot.login_flow()

        if logged:
            bot.open_golden_miner_bot()
            bot.click_start_button()
            bot.click_launch_if_popup_exists()

            opened = bot.wait_for_webapp_open()

            if opened:
                # Guarda solo la URL del iframe
                # bot.save_webapp_url("golden_miner_webapp_url.txt")

                # Guarda un HTML parecido al que mostraste
                # bot.save_webapp_iframe_html("golden_miner_iframe.html")

                # Guarda también en JSON por si luego quieres reutilizarlo
                bot.save_webapp_data_json("bot.json")

        #input("Presiona ENTER para cerrar...")
    finally:
        bot.close()


#if __name__ == "__main__":
#    login()