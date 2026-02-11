import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from calculator_page import CalculatorPage


class TestCalculator:
    @pytest.fixture(scope="class")
    def driver(self):
        """Configuration du driver Chrome pour les tests"""
        chrome_options = Options()
        # Configuration pour environnement CI/CD
        if os.getenv("CI"):
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(10)
        yield driver
        driver.quit()

    def test_page_loads(self, driver):
        """Test 1: Verifier que la page se charge correctement"""
        page = CalculatorPage(driver)
        page.load_page()

        # Verifier le titre
        assert "Calculatrice Simple" in driver.title
        # Verifier la presence des elements principaux
        assert driver.find_element(By.ID, "num1").is_displayed()
        assert driver.find_element(By.ID, "num2").is_displayed()
        assert driver.find_element(By.ID, "operation").is_displayed()
        assert driver.find_element(By.ID, "calculate").is_displayed()

    def test_addition(self, driver):
        """Test 2: Tester l'addition"""
        page = CalculatorPage(driver)
        page.load_page()

        page.enter_first_number(10)
        page.enter_second_number(5)
        page.select_operation("add")
        page.click_calculate()

        assert "Résultat: 15" in page.get_result()

    def test_division_by_zero(self, driver):
        """Test 3: Tester la division par zero"""
        page = CalculatorPage(driver)
        page.load_page()

        page.clear_numbers()
        page.enter_first_number(10)
        page.enter_second_number(0)
        page.select_operation("divide")
        page.click_calculate()

        assert "Erreur: Division par zéro" in page.get_result()

    def test_all_operations(self, driver):
        """Test 4: Tester toutes les operations"""
        page = CalculatorPage(driver)
        page.load_page()

        operations = [
            ("add", "8", "2", "10"),
            ("subtract", "8", "2", "6"),
            ("multiply", "8", "2", "16"),
            ("divide", "8", "2", "4"),
        ]

        for op, num1, num2, expected in operations:
            page.clear_numbers()
            page.enter_first_number(num1)
            page.enter_second_number(num2)
            page.select_operation(op)
            page.click_calculate()

            assert f"Résultat: {expected}" in page.get_result()
            time.sleep(1)

    def test_page_load_time(self, driver):
        """Test 5: Mesurer le temps de chargement de la page"""
        page = CalculatorPage(driver)
        start_time = time.time()

        page.load_page()

        # Attendre que la page soit completement chargee
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "calculator"))
        )

        load_time = time.time() - start_time
        print(f"Temps de chargement: {load_time:.2f} secondes")

        # Verifier que le chargement prend moins de 3 secondes
        assert load_time < 3.0, f"Page trop lente a charger: {load_time:.2f}s"

    def test_decimal_numbers(self, driver):
        """Test 6: Tester avec des nombres decimaux"""
        page = CalculatorPage(driver)
        page.load_page()

        page.clear_numbers()
        page.enter_first_number(10.5)
        page.enter_second_number(2.5)
        page.select_operation("add")
        page.click_calculate()

        assert "Résultat: 13" in page.get_result()

    def test_negative_numbers(self, driver):
        """Test 7: Tester avec des nombres negatifs"""
        page = CalculatorPage(driver)
        page.load_page()

        page.clear_numbers()
        page.enter_first_number(-8)
        page.enter_second_number(-2)
        page.select_operation("multiply")
        page.click_calculate()

        assert "Résultat: 16" in page.get_result()

    def test_ui_colors_and_sizes(self, driver):
        """Test 8: Tester des proprietes visuelles (couleurs/tailles)"""
        page = CalculatorPage(driver)
        page.load_page()

        container = driver.find_element(By.CLASS_NAME, "container")
        input_num1 = driver.find_element(By.ID, "num1")
        button = driver.find_element(By.ID, "calculate")

        # Verifier la largeur max du container (definie dans style.css)
        max_width = container.value_of_css_property("max-width")
        assert max_width == "400px"

        # Verifier une taille de police commune aux champs et bouton
        assert input_num1.value_of_css_property("font-size") == "16px"
        assert button.value_of_css_property("font-size") == "16px"

        # Verifier que le bouton est visible et a une taille non nulle
        assert button.is_displayed()
        assert button.size["width"] > 0
        assert button.size["height"] > 0


if __name__ == "__main__":
    pytest.main(["-v", "--html=report.html", "--self-contained-html"])
