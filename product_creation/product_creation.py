from toolkit.managers import OpenCartManager
import requests
import pandas as pd
import selenium as sel
import time
import random

FILENAME = input("Insert filename:")



CATALOG_ELEMENT_ID = "menu-catalog"
PRODUCTS_ELEMENT_XPATH = '//*[@id="collapse2"]/li[3]/a'
PGECP_CHARACTERISTICS_ELEMENT_CSS_SELECTOR = ".navigation-bar.list-controls.js-onpage-nav ul li a"
MODEL_DATA_ELEMENT_ID =
SKU_DATA_ELEMENT_ID =
EAN_DATA_ELEMENT_ID =
ISBN_DATA_ELEMENT_ID =
PRICE_DATA_ELEMENT_ID =
TAX_CLASS_DATA_ELEMENT_ID =
QUANTITY_DATA_ELEMENT_ID
SKIP_BATCH_ELEMENT_ID
DAYS_TO_DELIVERY_ELEMENT_ID
WEIGHT_ELEMENT_ID


# Import dataset, must be xlsx file with the following columns ['code', 'product', 'plafon']
df_for_creation = pd.read_excel(FILENAME)


# Initialize manager object
opencart_manager = OpenCartManager()
opencart_manager.get_logged_in()

# Navigate to product creation
opencart_manager.navigate_backend_to(menu_item_id=CATALOG_ID, submenu_item_xpath=PRODUCTS_XPATH)
time.sleep(random.uniform(5, 10))

# Iterate over dataset of newprods
for index, row in df_for_creation.iterrows():
    code = row["code"]
    product = row["product"]
    plafon = row["plafon"]

    time.sleep(random.uniform(3, 4))

    # Initialize product creation
    opencart_manager.PRODMAKE_begin_make_new()
    time.sleep(random.uniform(5, 10))


    # product_data_to_insert


    # fill new product data
    opencart_manager.PRODMAKE_insert_datum()
    opencart_manager.PRODMAKE_insert_datum()
    opencart_manager.PRODMAKE_select_tab()

    opencart_manager.PRODMAKE_insert_datum()
    opencart_manager.PRODMAKE_insert_datum()
    opencart_manager

    # Scrape PGECP for data
    opencart_manager.open_new_tab_and_switch_focus()
    opencart_manager.PGECP_search_query(product)
    time.sleep(random.uniform(4, 6))
    list_of_results = opencart_manager.PGECP_get_search_results()
    print(f"{product}\nLIST OF PGECP RESULTS:\n")
    for i in range(len(list_of_results)):
        print(f"{i}. {list_of_results[i][0]}")

    # Which result is it ?
    intended_result_index = input("Which number is it (select the index from above and hit enter, any other input"
                                  "will count as no result in PGECP\n")

    # try to find the given index in the resultlist
    try:
        intended_result_index = int(intended_result_index)
        a = list_of_results[intended_result_index]
    # catch other input (mistakes or when its none of the results or when there are no results)
    except (ValueError, IndexError):
        intended_result_index = "KAPPA"
        print("None of the results matched the, continue search manually through the internet")

    # branch for when to
    if intended_result_index in range(len(list_of_results)):
        intended_product_link = list_of_results[intended_result_index][1]
        product_data = opencart_manager.PGECP_get_result_product_data(intended_product_link)
        opencart_manager.driver.get(intended_product_link)
        characteristics_ele = opencart_manager.driver.find_elements_by_css_selector(PGECP_CHARACTERISTICS_CSS_SELECTOR)[1]
        time.sleep(random.uniform(0,1))
        characteristics_ele.click()


        a = input("pause to see")