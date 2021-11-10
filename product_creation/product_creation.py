from toolkit.managers import OpenCartManager
import requests
import pandas as pd
import selenium as sel
import time
import random

FILENAME = input("Insert filename:")
CATALOG_ID = "menu-catalog"
PRODUCTS_XPATH = '//*[@id="collapse2"]/li[3]/a'
PGECP_CHARACTERISTICS_CSS_SELECTOR = ".navigation-bar.list-controls.js-onpage-nav ul li a"


# Import dataset, must be xlsx file with the following columns ['code', 'product', 'plafon']
df_for_creation = pd.read_excel(FILENAME)


# Initialize manager object
opencart_manager = OpenCartManager()
opencart_manager.get_logged_in()

# Iterate over dataset of newprods
for index, row in df_for_creation.iterrows():
    code = row["code"]
    product = row["product"]
    plafon = row["plafon"]

    time.sleep(random.uniform(3, 4))

    # Navigate to product creation
    opencart_manager.navigate_backend_to(menu_item_id=CATALOG_ID, submenu_item_xpath=PRODUCTS_XPATH)
    time.sleep(random.uniform(5, 10))
    # Initialize product creation
    opencart_manager.PRODMAKE_begin_make_new()
    time.sleep(random.uniform(5, 10))

    # Scrape PGECP for prices
    opencart_manager.open_new_tab_and_switch_focus()
    opencart_manager.PGECP_search_query(product)
    time.sleep(random.uniform(4, 6))
    list_of_results = opencart_manager.PGECP_get_search_results()
    for i in range(len(list_of_results)):
        print(f"{i}. {list_of_results[i][0]}")

    # Which result is it ?
    intended_result_index = input("Which number is it (select the index from above and hit enter, any other input"
                                  "will count as no result in PGECP")

    try:
        intended_result_index = int(intended_result_index)
    except ValueError:
        print("No result in PGECP")

    if intended_result_index in range(len(list_of_results)):
        intended_product_link = list_of_results[intended_result_index][1]
        product_data = opencart_manager.PGECP_get_result_product_data(intended_product_link)
        opencart_manager.driver.get(intended_product_link)
        characteristics_ele = opencart_manager.driver.find_elements_by_css_selector(PGECP_CHARACTERISTICS_CSS_SELECTOR)[1]
        time.sleep(random.uniform(0,1))
        characteristics_ele.click()
        print(product_data)
        a = input("pause to see")
        #opencart_manager.decide_final_price()

    # fill general data
    opencart_manager.PRODMAKE_insert_datum()
    opencart_manager.PRODMAKE_insert_datum()


    # decide price
    opencart_manager.decide_final_price()

    # fill data
    opencart_manager.PRODMAKE_insert_datum()

    # fill data