from toolkit.managers import OpenCartManager
import requests
import pandas as pd
import selenium as sel
import time
import random

FILENAME = input("Insert filename:")

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

    time.sleep(random.uniform(5,10))

    # Navigate to product creation
    opencart_manager.navigate_backend_to(menu_item_num=2, submenu_item_num=3)
    time.sleep(random.uniform(3, 4))
    # Initialize product creation
    opencart_manager.PRODMAKE_begin_make_new()


    # Scrape PGECP for prices
    opencart_manager.open_new_tab_and_switch_focus()
    opencart_manager.PGECP_search_query()
    opencart_manager.PGECP_get_search_results()

    # Which result is it ?
    opencart_manager.PGECP_get_result_product_data()
    opencart_manager.driver.get()
    opencart_manager.driver.scroll_to_chars()
    opencart_manager.decide_final_price()

    # fill general data
    opencart_manager.PRODMAKE_insert_datum()
    opencart_manager.PRODMAKE_insert_datum()

    # decide price
    opencart_manager.decide_final_price()

    # fill data
    opencart_manager.PRODMAKE_insert_datum()

    #
