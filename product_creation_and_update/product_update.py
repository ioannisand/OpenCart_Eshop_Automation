from toolkit.managers import OpenCartManager, lista_comparison
import pandas as pd
import os
import datetime
import time
import random
from dotenv import load_dotenv

load_dotenv()

# INITIALIZING PARAMETERS
TODAY_FILENAME = input("Insert todays filename:\n")
LAST_UPDATE_FILENAME = input("Insert last update's filename:\n")
DAY = datetime.datetime.now().day
MONTH = datetime.datetime.now().month
MANUFACTURER = input("Insert manufacturer name:\n")
USERNAME = os.getenv("USERNAMEE")
PASSWORD = os.getenv("PASSWORD")
LOGIN_URL = os.getenv("LOGIN_URL")
CHROMEDRIVER_PATH = str(os.getenv("CHROMEDRIVER_PATH"))
CATALOG_ELEMENT_ID = os.getenv("CATALOG_ELEMENT_ID")
PRODUCTS_QE_XPATH = '//*[@id="collapse2"]/li[4]/a'
QE_NAME_ELEMENT_CSS_SELECTOR = os.getenv("QE_NAME_ELEMENT_CSS_SELECTOR")
QE_ACTIVITY_STATUS_CSS_SELECTOR = os.getenv("QE_ACTIVITY_STATUS_CSS_SELECTOR")
QE_PRICE_CSS_SELECTOR = os.getenv("QE_PRICE_CSS_SELECTOR")


# IMPORTING DATA
last_update_dataframe = pd.read_excel(LAST_UPDATE_FILENAME)
today_dataframe = pd.read_excel(TODAY_FILENAME)

# COMPARING LISTS
comparison_results = lista_comparison(df_last_update=last_update_dataframe, df_today=today_dataframe)

# INITIALIZE DATA CONTAINERS
df_deact = comparison_results["df_deact"]
df_common = comparison_results["df_common"]
df_new = comparison_results["df_new"]
mult_res = []
lista_notfound = []


# INITIALIZE OPENCART MANAGER OBJECT
opencart_manager = OpenCartManager(username=USERNAME,
                                   password=PASSWORD,
                                   login_url=LOGIN_URL,
                                   chromedriver_path=CHROMEDRIVER_PATH
                                   )

opencart_manager.get_logged_in()
time.sleep(random.uniform(1.5, 2.5))
opencart_manager.navigate_backend_to(menu_item_id=CATALOG_ELEMENT_ID, submenu_item_xpath=PRODUCTS_QE_XPATH)
time.sleep(random.uniform(20, 25))

# DEACTIVATION OF PRODUCTS THAT WENT OUT OF MANUFACTURER STOCK
# iterate through the rows

for index, row in comparison_results["df_deact"].iterrows():
    try:
        # row data
        code = row["code"]
        product = row["product"]
        plafon = row["plafon"]

        # search by name
        opencart_manager.QE_search_by(query=product, field="NAME")
        time.sleep(random.uniform(1.5, 2.5))
        # count results
        res_count = opencart_manager.QE_count_results()

        if res_count == 0:
            # if nothing was fund, check again
            res_count = opencart_manager.QE_count_results()
            time.sleep(random.uniform(1.5, 2.5))
        # Branch depending on the number of results
        if res_count == 0:
            lista_notfound.append((code, product, plafon))

        elif res_count == 1:
            name_ele = opencart_manager.QE_target_field(row_index=0, element_identifier=QE_NAME_ELEMENT_CSS_SELECTOR)
            first_result_name = name_ele.text
            if product == first_result_name:
                # DEACTIVATE
                activity_status_ele = opencart_manager.QE_target_field(row_index=0, element_identifier=QE_ACTIVITY_STATUS_CSS_SELECTOR)
                opencart_manager.QE_update_select_input_field_from_td_ele(targetted_td_ele=activity_status_ele, option_number=0)
                time.sleep(random.uniform(3, 3.5))
        elif res_count > 1:
            # move to deactivate multiple results
            mult_res.append((code, product, plafon, "deactivate"))
    except:
        print(f"{product} errored out")

# UPDATE EXISTING PRODUCTS
# iterate through rows
for index, row in df_common.iterrows():
    try:
        # row data
        code = row["code"]
        product = row["product"]
        plafon = row["plafon"]

        # search by name
        opencart_manager.QE_search_by(query=product, field="NAME")
        time.sleep(random.uniform(1.5, 2.5))
        # count results
        res_count = opencart_manager.QE_count_results()
        if res_count == 0:
            # if nothing was found check again
            res_count = opencart_manager.QE_count_results()
            time.sleep(random.uniform(1.5, 2.5))
        # branch depending on number of results
        if res_count == 0:
            lista_notfound.append((code, product, plafon))

        elif res_count == 1:

            first_result_name_ele = opencart_manager.QE_target_field(row_index=0, element_identifier=QE_NAME_ELEMENT_CSS_SELECTOR)
            first_result_name = first_result_name_ele.text
            if product == first_result_name:
                # Activate
                activity_status_ele = opencart_manager.QE_target_field(row_index=0, element_identifier=QE_ACTIVITY_STATUS_CSS_SELECTOR)
                opencart_manager.QE_update_select_input_field_from_td_ele(targetted_td_ele=activity_status_ele,
                                                                          option_number=1)
                time.sleep(2)
                # Update Price
                new_price = str(plafon * 1.08)
                price_ele = opencart_manager.QE_target_field(row_index=0, element_identifier=QE_PRICE_CSS_SELECTOR)
                opencart_manager.QE_update_text_input_field_from_td_ele(targetted_td_element=price_ele, new_value=new_price)
                time.sleep(random.uniform(2.5, 3.5))
        elif res_count > 1:
            # move to deactivate mult_res
            mult_res.append((code, product, plafon, "update"))
    except:
        print(f"{product} errored out")

time.sleep(random.uniform(1.5, 2.5))
# STORE NEW AND NOTFOUND PRODUCTS IN A SINGLE DATAFRAME FOR CREATION

df_multiple_results = pd.DataFrame(mult_res, columns=["code", "product", "plafon", "origin"])
df_notfound = pd.DataFrame(lista_notfound, columns=["code", "product", "plafon"])
df_creation = df_new.append(df_notfound)

os.mkdir(f"REPORTS_{DAY}_{MONTH}_{MANUFACTURER}")
df_deact.to_excel(f"REPORTS_{DAY}_{MONTH}_{MANUFACTURER}/deact_{DAY}_{MONTH}_{MANUFACTURER}.xlsx", index=False)
df_multiple_results.to_excel(f"REPORTS_{DAY}_{MONTH}_{MANUFACTURER}/multres_{DAY}_{MONTH}_{MANUFACTURER}.xlsx", index=False)
df_creation.to_excel(f"REPORTS_{DAY}_{MONTH}_{MANUFACTURER}/products_to_create_{DAY}_{MONTH}_{MANUFACTURER}.xlsx", index=False)