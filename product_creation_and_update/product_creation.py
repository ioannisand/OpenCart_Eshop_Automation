from toolkit.managers import OpenCartManager
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import requests
import pandas as pd
import selenium as sel
import time
import random
import os
from dotenv import load_dotenv
import datetime

load_dotenv()

# IMPORTING PARAMETERS FROM ENVIRONMENT AND INITIALIZING AUTOMATED ONES
FILENAME = input("insert filename: ")
MANUFACTURER = input("insert manufacturer name:  ")
DAY = datetime.datetime.now().strftime("%d")
MONTH = datetime.datetime.now().strftime("%m")
YEAR = 21
POSOSTO = 1.3392
USERNAME = os.getenv("USERNAMEE")
PASSWORD = os.getenv("PASSWORD")
LOGIN_URL = os.getenv("LOGIN_URL")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")
PHOTOS_FILEPATH = os.getenv("PHOTOS_FILEPATH")
CATALOG_ELEMENT_ID = os.getenv("CATALOG_ELEMENT_ID")
PRODUCTS_ELEMENT_XPATH = '//*[@id="collapse2"]/li[2]/a'
PGECP_CHARACTERISTICS_ELEMENT_CSS_SELECTOR = os.getenv("PGECP_CHARACTERISTICS_ELEMENT_CSS_SELECTOR")
NAME_GENDATA_ELEMENT_ID = os.getenv("NAME_GENDATA_ELEMENT_ID")
PAGENAME_GENDATA_ELEMENT_ID = os.getenv("PAGENAME_GENDATA_ELEMENT_ID")
MODEL_DATA_ELEMENT_ID = os.getenv("MODEL_DATA_ELEMENT_ID")
SKU_DATA_ELEMENT_ID = os.getenv("SKU_DATA_ELEMENT_ID")
EAN_DATA_ELEMENT_ID = os.getenv("EAN_DATA_ELEMENT_ID")
ISBN_DATA_ELEMENT_ID = os.getenv("ISBN_DATA_ELEMENT_ID")
PRICE_DATA_ELEMENT_ID = os.getenv("PRICE_DATA_ELEMENT_ID")
TAX_CLASS_DATA_ELEMENT_ID = os.getenv("TAX_CLASS_DATA_ELEMENT_ID")
QUANTITY_DATA_ELEMENT_ID = os.getenv("QUANTITY_DATA_ELEMENT_ID")
SKIP_BATCH_DATA_ELEMENT_ID = os.getenv("SKIP_BATCH_DATA_ELEMENT_ID")
DAYS_TO_DELIVERY_DATA_ELEMENT_ID = os.getenv("DAYS_TO_DELIVERY_DATA_ELEMENT_ID")
WEIGHT_ELEMENT_ID = os.getenv("WEIGHT_ELEMENT_ID")
PGECP_MAIN_PAGE_URL = os.getenv("PGECP_MAIN_PAGE_URL")
idno = int(input("insert the number codes start counting from:"))

# Import dataset, must be xlsx file with the following columns ['code', 'product', 'plafon']
df_for_creation = pd.read_excel(FILENAME).iloc[:, :]


# Initialize manager object
opencart_manager = OpenCartManager(chromedriver_path=CHROMEDRIVER_PATH,
                                   username=USERNAME,
                                   password=PASSWORD,
                                   login_url=LOGIN_URL,
                                   image_filepath=PHOTOS_FILEPATH)
opencart_manager.get_logged_in()

# Navigate to product creation
time.sleep(1)
opencart_manager.navigate_backend_to(menu_item_id=CATALOG_ELEMENT_ID, submenu_item_xpath=PRODUCTS_ELEMENT_XPATH)
time.sleep(random.uniform(2, 5))

# Iterate over dataset of newprods
for index, row in df_for_creation.iterrows():
    idno += 1
    code = row["code"]
    product = row["product"]
    plafon = row["plafon"]

    time.sleep(random.uniform(1, 2))

    # Initialize product creation
    opencart_manager.PRODMAKE_begin_make_new()
    time.sleep(random.uniform(1, 3))


    # product_data_to_insert
    name = product
    model = f"GAT-OPB{DAY}{MONTH}{idno}"
    sku = f"OPB{DAY}{MONTH}{idno}{MANUFACTURER}"
    ean = code
    isbn = os.getenv("ISBN_DATA")
    price = (plafon * POSOSTO)
    tax_class_index = 1
    quantity = 0
    skip_batch_index = 0
    days_to_delivery_index = 0
    weight = 1.5

    # fill new product data
    # insert page name
    opencart_manager.PRODMAKE_insert_datum(input_element_id=NAME_GENDATA_ELEMENT_ID, datum=product)
    # insert meta name
    opencart_manager.PRODMAKE_insert_datum(input_element_id=PAGENAME_GENDATA_ELEMENT_ID, datum=product)
    # change tab to data
    opencart_manager.PRODMAKE_select_tab(1)
    time.sleep(random.uniform(0.5, 1.5))
    # insert model
    opencart_manager.PRODMAKE_insert_datum(input_element_id=MODEL_DATA_ELEMENT_ID, datum=model)
    # insert sku
    opencart_manager.PRODMAKE_insert_datum(input_element_id=SKU_DATA_ELEMENT_ID, datum=sku)
    # insert ean
    opencart_manager.PRODMAKE_insert_datum(input_element_id=EAN_DATA_ELEMENT_ID, datum=ean)
    # insert isbn
    # opencart_manager.PRODMAKE_insert_datum(input_element_id=ISBN_DATA_ELEMENT_ID, datum=isbn)
    # insert price
    opencart_manager.PRODMAKE_insert_datum(input_element_id=PRICE_DATA_ELEMENT_ID, datum=price)
    # select tax class
    opencart_manager.PRODMAKE_select_datum(select_element_id=TAX_CLASS_DATA_ELEMENT_ID, datum_index=tax_class_index)
    # insert quantity
    opencart_manager.PRODMAKE_insert_datum(input_element_id=QUANTITY_DATA_ELEMENT_ID, datum=quantity)
    # toggle skip batch ele
    opencart_manager.PRODMAKE_select_datum(select_element_id=SKIP_BATCH_DATA_ELEMENT_ID, datum_index=skip_batch_index)
    # select days to delivery class
    opencart_manager.PRODMAKE_select_datum(select_element_id=DAYS_TO_DELIVERY_DATA_ELEMENT_ID, datum_index=days_to_delivery_index)
    # insert weight
    opencart_manager.PRODMAKE_insert_datum(input_element_id=WEIGHT_ELEMENT_ID, datum=weight)
    # switch to gen tab



    # Scrape PGECP for data
    opencart_manager.open_new_tab_and_switch_focus(initial_url=PGECP_MAIN_PAGE_URL)
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

    # branch for when it matches one of the results....
    if intended_result_index in range(len(list_of_results)):
        intended_product_link = list_of_results[intended_result_index][1]
        product_data = opencart_manager.PGECP_get_result_product_data(intended_product_link)
        image_address = product_data["PGECP_image_url"]
        time.sleep(random.uniform(0.5, 1.5))
        opencart_manager.driver.get(intended_product_link)
        # catch
        try:
            gamimena_cookies_ele = opencart_manager.driver.find_element_by_id("accept-essential")
            gamimena_cookies_ele.click()
        except (NoSuchElementException, ElementClickInterceptedException):
            pass
        characteristics_ele = opencart_manager.driver.find_elements_by_css_selector(PGECP_CHARACTERISTICS_ELEMENT_CSS_SELECTOR)[1]
        time.sleep(random.uniform(0, 1))
        characteristics_ele.click()
        opencart_manager.get_image_from_address(image_address=image_address, storage_path=PHOTOS_FILEPATH, imagename=sku)
    # .... or when it doesn't
    else:
        opencart_manager.driver.close()
        opencart_manager.driver.switch_to.window(opencart_manager.driver.window_handles[0])

    opencart_manager.driver.switch_to.window(opencart_manager.driver.window_handles[0])
    opencart_manager.PRODMAKE_select_tab(tab_index=0)
    product_got_created_prompt = input("If the product was created successfully, leave only first tab open and press "
                                       "any key to continue to next item")