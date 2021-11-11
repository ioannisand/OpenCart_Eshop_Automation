import shutil

from selenium.webdriver import ChromeOptions, Chrome
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import requests
import time
import os
import pandas as pd
from dotenv import load_dotenv


load_dotenv()


def lista_comparison(day_today, month_today, day_last_update, month_last_update, manufacturer):
    ''' Returns a dictionary of dataframes containing the products that were up during the last update of the
     manufacturer's stock, the products whose price changed since last update, all the common products between the two
     lists regardless of price and all the products existing only in the new list. The input is 2 files put in the same
     working directory as the script that calls this function, named
     "availability_{INSERT_DAY_OF_MONTH}_{INSERT_NR_OF_MONTH}_{INSERT_MANUFACTURER_NAME}.xlsx" '''
    # importing the data
    df_last_update = pd.read_excel(f"availability_{day_last_update}_{month_last_update}_{manufacturer}.xlsx", dtype=str)
    df_today = pd.read_excel(f"availability_{day_today}_{month_today}_{manufacturer}.xlsx", dtype=str)
    names_last_update = df_last_update.iloc[:, 1].values
    names_today = df_today.iloc[:, 1].values

    # initializing lists to fill each dataframe
    lista_deact_names = []
    lista_common_names = []
    lista_new_product_names = []

    # first filtering
    for name in names_last_update:
        if name not in names_today:
            lista_deact_names.append(name)

        elif name in names_today:
            lista_common_names.append(name)

    for name in names_today:
        if name not in lista_common_names:
            lista_new_product_names.append(name)

    # second filtering(changed prices)
    lista_changed_prices_names = []
    for name in lista_common_names:
        old_plafon = df_last_update[df_last_update["product"] == name].plafon.values[0]
        new_plafon = df_today[df_today["product"] == name].plafon.values[0]
        if old_plafon != new_plafon:
            lista_changed_prices_names.append(name)

    # making dataframes to return
    # dataframe to deact
    lista_deact_codes = [df_last_update[df_last_update["product"] == name].code.values[0] \
                         for name in lista_deact_names]
    lista_deact_plafons = [df_last_update[df_last_update["product"] == name].plafon.values[0] \
                         for name in lista_deact_names]
    df_deact = pd.DataFrame({"code": pd.Series(lista_deact_codes),
                             "product": pd.Series(lista_deact_names),
                             "plafon": pd.Series(lista_deact_plafons)})

    # dataframe with changed prices
    lista_changed_prices_codes = [df_today[df_today["product"] == name].code.values[0] \
                                  for name in lista_changed_prices_names]
    lista_changed_prices_plafons = [df_today[df_today["product"] == name].plafon.values[0] \
                                    for name in lista_changed_prices_names]
    df_changed_prices = pd.DataFrame({"code": pd.Series(lista_changed_prices_codes),
                                      "product": pd.Series(lista_changed_prices_names),
                                      "plafon": pd.Series(lista_changed_prices_plafons)})
    # dataframe with all common
    lista_common_codes = [df_today[df_today["product"] == name].code.values[0] \
                          for name in lista_common_names]
    lista_common_plafons = [df_today[df_today["product"] == name].plafon.values[0] \
                            for name in lista_common_names]
    df_common = pd.DataFrame({"code": pd.Series(lista_common_codes),
                              "product": pd.Series(lista_common_names),
                              "plafon": pd.Series(lista_common_plafons)})

    # dataframe with new
    lista_new_product_codes = [df_today[df_today["product"] == name].code.values[0] \
                               for name in lista_new_product_names]
    lista_new_product_plafons = [df_today[df_today["product"] == name].plafon.values[0] \
                                 for name in lista_new_product_names]
    df_lista_new_product = pd.DataFrame({"code": pd.Series(lista_new_product_codes),
                                         "product": pd.Series(lista_new_product_names),
                                         "plafon": pd.Series(lista_new_product_plafons)})
    # final dictionary to return
    return_dict = {"df_deact": df_deact,
                   "df_changed_prices": df_changed_prices,
                   "df_common": df_common,
                   "df_new": df_lista_new_product}

    return return_dict


class OpenCartManager():
    ''' Upon creation of an instance of this class, an selenium.webdriver.Chrome object is created as an attribute,
    which will be referred to as driver from now on. This class utilizes the driver and its methods, as well as some
     to perform a variety of tasks, mostly navigating the Opencart Backend Interface, collecting data from it, updating some values(using some of the
    extensions installed, more on that on the README file) and scraping a popular commercial platform for data on the
    corresponding products. The login url and credentials for the Opencart Backend Interface should be provided on a
    file named .env, put directly in the working directory'''


    # configuration of the Chrome Webdriver in such a way as to hide selenium from some of the potential bot detection algorithms
    prefs = {"credentials_enable_service": False,
             "profile.password_manager_enabled": False}
    options = ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option("prefs", prefs)

    def __init__(self):
        self.driver = Chrome(executable_path=os.getenv("CHROMEDRIVER_PATH"), options=self.options)
        self.username = os.getenv("USERNAMEE")
        self.password = os.getenv("PASSWORD")
        self.login_url = os.getenv("LOGIN_URL")
        self.driver.maximize_window()
        self.error_occured = []
        self.one_res_different_prod = []
        self.not_found = []
        self.de_activate_multiple_results = []
        self.de_activated_reports = []
        self.update_multiple_results = []
        self.update_reports = []
        self.mismatches = []


    def get_logged_in(self):
        ''' Navigates the current tab of the driver to the login page of the Correspinding OpenCart'''
        login_url = self.login_url
        username = self.username
        password = self.password
        print(f"getting {login_url}")
        self.driver.get(url=login_url)
        # logging in
        username_ele = self.driver.find_element_by_name("username")
        username_ele.send_keys(username)
        password_ele = self.driver.find_element_by_name("password")
        password_ele.send_keys(password)
        time.sleep(1)
        password_ele.send_keys(Keys.ENTER)

    def navigate_backend_to(self, menu_item_id, submenu_item_xpath=None):
        ''' Once logged in to the Opencart backend interface, navigates the driver
        the specified menu item and sub item'''
        menu_item_ele = self.driver.find_element_by_id(menu_item_id)
        menu_item_ele.click()
        time.sleep(1)
        if submenu_item_xpath != None:
            submenu_item_ele = self.driver.find_element_by_xpath(submenu_item_xpath)
            submenu_item_ele.click()

    def decide_final_price(self, lowest_price_limit, current_price, PGECP_price_list, target_placement):
        ''' Returns the final decided price of the product, taking into consideration the lowest price limit, the
        competition's prices, and the places the ESHOP is aiming for, in fallback order'''
        list_of_target_prices = PGECP_price_list[target_placement - 1:]
        min_return_price = lowest_price_limit
        current_price = round(current_price, 2)
        if len(list_of_target_prices) == 0:
            return lowest_price_limit * 1.06

        # iterate through the competition prices
        for i in len(list_of_target_prices):
            price = list_of_target_prices[i]

            # The store is already in the first place
            if current_price == price:

                try:
                    next_price = list_of_target_prices[i + 1]
                    difference_from_next_shop = next_price - current_price
                    if difference_from_next_shop > 0.1 and next_price - 0.1 > min_return_price:
                        return next_price - 0.1
                    elif current_price >= min_return_price:
                        return current_price
                    else:
                        return min_return_price
                except IndexError:
                    if price >= min_return_price:
                        return min_return_price
            # the target price is below the shop's price
            elif current_price > price:
                if price - 0.1 >= lowest_price_limit:
                    return price - 0.1
                else:
                    continue

    def open_new_tab_and_switch_focus(self, initial_url=os.getenv("PGECP_MAIN_PAGE_URL")):
        ''' Opens a new chrome tab using the self.driver and switches the focus to it, navigates to the specified url'''
        scriptstring = "window.open('" + initial_url + "');"
        print(scriptstring)
        self.driver.execute_script(scriptstring)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.get(initial_url)

    def close_tab_and_switch_focus_to_first(self,):
        ''' Closes the current chrome tab of the self.driver and switches the focus to the first tab'''
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    def QE_search_by(self, query, field):
        ''' Once on the QE tab, searches for a product by the EAN search field'''

        field = field.upper()
        field_names = {"EAN": "filter_ean",
                       "MODEL": "filter_model",
                       "NAME": "filter_name",
                       "MPN": "filter_mpn"}
        search_ele = self.driver.find_element_by_name(field_names[field])
        search_ele.send_keys(Keys.CONTROL + "a")
        search_ele.send_keys(Keys.BACKSPACE)
        search_ele.send_keys(str(query))
        search_ele.send_keys(Keys.ENTER)
        time.sleep(1)
        search_ele.send_keys(Keys.CONTROL + "a")
        search_ele.send_keys(Keys.BACKSPACE)

    def QE_count_results(self):
        ''' Returns the number of results found after the search of a query in Opencart'''
        rows_eles = self.driver.find_elements_by_css_selector("#dT tbody tr")
        if len(rows_eles) == 1:
            if rows_eles[0].find_element_by_css_selector("td").text == "No matching products found":
                return 0
        return len(rows_eles)

    def QE_target_field(self, row_index, element_identifier, type_of_identification="css_selector"):
        ''' Returns the specified td element that corresponds to a cell in the QE search results panel'''
        target_row_ele = self.driver.find_elements_by_css_selector("#dT tbody tr")[row_index]
        if type_of_identification == "css_selector":
            target_td_ele = target_row_ele.find_element_by_css_selector(element_identifier)
            return target_td_ele
        elif type_of_identification == "name":
            target_td_ele = target_row_ele.find_element_by_name(element_identifier)
            return target_td_ele
        else:
            print("Please specify a valid way of element identification")

    def QE_get_target_element_text(self, targetted_element):
        return targetted_element.text

    def QE_get_price_without_special_from_td_ele(self, targetted_td_element):
        '''Returns the price contained in the targetted element, not including its special price'''
        grossprice_eles = targetted_td_element.find_elements_by_css_selector("s")
        if len(grossprice_eles) == 0:
            return float(targetted_td_element.text)
        elif len(grossprice_eles) == 1:
            return float(grossprice_eles[-1].text)

    def QE_update_text_input_field_from_td_ele(self, targetted_td_element, new_value):
        '''Updates the value of the target td element, provided it is an element that contains a text value'''
        targetted_td_element.click()
        time.sleep(1)
        text_input_ele = self.driver.find_element_by_css_selector(".editable-input .form-control.input-sm")
        text_input_ele.send_keys(Keys.CONTROL +"a")
        text_input_ele.send_keys(Keys.BACKSPACE)
        text_input_ele.send_keys(new_value)
        confirm_update_ele = \
        self.driver.find_elements_by_css_selector(".control-group.form-group div .editable-buttons")[-1]
        confirm_update_ele.click()

    def QE_update_select_input_field_from_td_ele(self, targetted_td_ele, option_number):
        '''Updates the value of the target td element, provided it is an element that contains a text value'''
        targetted_td_ele.click()
        time.sleep(1)
        select_input_ele = self.driver.find_element_by_css_selector(".editable-input select")
        select_input_ele.click()
        option_ele = select_input_ele.find_elements_by_css_selector("option")[option_number]
        option_ele.click()
        confirm_update_ele = \
        self.driver.find_elements_by_css_selector(".control-group.form-group div .editable-buttons")[-1]
        confirm_update_ele.click()

    def QE_get_frontend_price_from_view(self, targetted_element):
        ''' Returns the frontend price of the product corresponding to the product of the targetted td elements'''
        site_link_ele = targetted_element.find_element_by_css_selector(
            ".btn-group.btn-group-flex .btn.btn-default.btn-xs.view")
        site_link_ele.click()
        self.driver.switch_to.window(self.driver.window_handles[1])
        time.sleep(0.5)
        site_price = self.driver.find_element_by_css_selector(".product-price").text
        site_price_float = float(site_price.replace(",", "", 1).replace("€", "", 1))
        time.sleep(3)
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        return site_price_float

    def PGECP_search_query(self, query):
        ''' Using the self.driver, that should already be navigated to the PGECP main page, searches said PGECP
         for the given query'''
        search_ele = self.driver.find_element_by_id("search-bar-input")
        search_ele.send_keys(Keys.CONTROL + "a")
        search_ele.send_keys(Keys.BACKSPACE)
        search_ele.send_keys(query + Keys.ENTER)
        try:
            gamimena_cookies_ele = self.driver.find_element_by_id("accept-essential")
            gamimena_cookies_ele.click()
        except NoSuchElementException:
            pass

    def PGECP_get_search_results(self):
        ''' Using the self.driver, that should already be on the results page of the PGECP, gathers the names and links
        of all the resulting products and returns list of tuples containing tuples of size 2, name and link'''
        product_card_eles = self.driver.find_elements_by_css_selector("#sku-list li .card-content h2 a")
        product_list = []
        for product_card_ele in product_card_eles:
            product_name = product_card_ele.text
            product_link = product_card_ele.get_attribute('href')
            product_list.append((product_name, product_link))
        return product_list

    def PGECP_get_result_product_data(self, link):
        ''' Provided the link the page of a product in the PGECP, sends out a request (using the python requests library
        and returns the data regarding that product (name, list of prices)'''
        response = requests.get(url=link).text
        soup = BeautifulSoup(response, "html.parser")
        PGECP_name = soup.select_one("#sku-details .sku-title .page-title").text
        PGECP_price_elements_list = soup.select(".dominant-price")
        PGECP_prices = []
        PGECP_image_url = "https:" + soup.select_one(".section.content .image a img", href=True)['src']
        for price in PGECP_price_elements_list:
            price = float(price.text.replace(".", "", 1).replace(",", ".", 1).replace(" €", "", 1))
            PGECP_prices.append(price)
        return {"PGECP_name": PGECP_name,"PGECP_pricelist": PGECP_prices, "PGECP_image_url": PGECP_image_url}



    def PRODMAKE_begin_make_new(self):
        ''' Once on the products page of Opencart Backend Interface, begins the cration of the new product'''
        make_new_product_button_ele = self.driver.find_elements_by_css_selector\
            (".page-header .container-fluid div a")[-1]
        make_new_product_button_ele.click()

    def PRODMAKE_select_tab(self, tab_index):
        ''' Once on the product creation page, clicks on the tab of product creation that corresponds to the
        index given'''
        tab_of_choice_ele = self.driver.find_element_by_css_selector(".nav.nav-tabs li a")[tab_index]
        tab_of_choice_ele.click()

    def PRODMAKE_insert_datum(self, input_element_id, datum):
        ''' On the opencart product creation page, in the general or data tab, inserts given data in the
        specified input element of the page(specified by id)'''
        input_ele = self.driver.find_element_by_id(input_element_id)
        input_ele.send_keys(datum)

    def PRODMAKE_select_datum(self, select_element_id, datum_index):
        ''' Once the opencart data tab, selects the appropriate option(given by index) of the specified select field
        element(specified by id)'''

    def get_image_from_address(self, image_address, storage_path, imagename):
        ''' Given the image adddress of a product, download it and store it in the specified path'''
        response = requests.get(image_address, stream=True)
        response.raw.decode_content = True
        filepath = f"{storage_path}/{imagename}.jpeg"
        with open(filepath, "wb") as file:
            shutil.copyfileobj(response.raw, file)



class PGECPmanager():
    ''' Similar to the Opencart Manager, but this one is for the PGECP's own eshop management interface'''
    # configuration of the Chrome Webdriver in such a way as to hide selenium from some of the potential bot detection algorithms
    prefs = {"credentials_enable_service": False,
             "profile.password_manager_enabled": False}
    options = ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option("prefs", prefs)

    def __init__(self, chromedriver_path):
        self.driver = Chrome(executable_path=chromedriver_path, options=self.options)
        self.username = os.getenv("USERNAME_PGCEP")
        self.password = os.getenv("PASSWORD_PGECP")
        self.login_url = os.getenv("LOGIN_URL_PGECP")
        self.driver.maximize_window()

    def log_in(self):
        ''' Logs in the PGECP eshop management interface'''
        login_url = self.login_url
        username = self.username
        password = self.password
        self.driver.get(login_url)
        # logging in
        login_button_ele = self.driver.find_element_by_css_selector(".login-btn.c-btn.c-btn-secondary")
        login_button_ele.click()
        username_ele = self.driver.find_element_by_id("user_username")
        username_ele.send_keys(username)
        password_ele = self.driver.find_element_by_id("user_password")
        password_ele.send_keys(password)
        time.sleep(1)
        password_ele.send_keys(Keys.ENTER)

    def choose_eshop(self, eshop_index):
        ''' chooses eshop in the PGECP management interface'''
        choose_eshop_ele = self.driver.find_element_by_id("change-shop")
        choose_eshop_ele.click()
        time.sleep(1)
        eshop_choice_ele = choose_eshop_ele.find_elements_by_css_selector("option")[eshop_index]
        eshop_choice_ele.click()

    def navigate_to(self, menu_item_index, submenu_item_index):
        ''' Utilizes self.driver to navigate the  PGECP management interface through choosing menu and submenu items
        in the left sidebar'''
        menu_item_ele = self.driver.find_elements_by_css_selector(".sidebar-content .nav-menu ul li section")\
        [menu_item_index]
        menu_item_ele.click()
        submenu_item_ele = self.driver.find_elements_by_css_selector(".menu-header .sub-menu-item a")[submenu_item_index]
        submenu_item_ele.click()

    def PRODUCTS_get_category_or_subcategory_count(self):
        ''' Once on the products appearing page of PGECP management interface, or on the page of a category, returns
        the count of categories or subcategories correspondingly'''
        return len(self.driver.find_elements_by_css_selector(".category-card"))

    def PRODUCTS_choose_sub_category_and_open_in_new_tab(self, category_index):
        ''' Once on the products appearing on PGECP page, chooses a category, or a subcategory'''
        category_card_ele = self.driver.find_elements_by_css_selector(".category-card")[category_index]
        category_link_ele = category_card_ele.find_element_by_css_selector(".card-container .card-link")
        href = category_link_ele.get_attribute("href")
        self.driver.execute_script(f"window.open({href});")
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def PRODUCTS_get_category_product_count(self,category_index):
        ''' Once on the products appearing on PGECP page, returns the product count of the category with selected index'''
        category_card_ele = self.driver.find_elements_by_css_selector(".category-card")[category_index]
        category_productcount_ele = category_card_ele.find_elements_by_css_selector\
        (".card-section.counter div .counter-lg")[category_index]
        return int(category_productcount_ele.text)

    def PRODUCTS_calculate_pages(self, product_count, products_per_page):
        ''' Returns the expected number of pages, given the count of products in a category'''
        return product_count // products_per_page

    def PRODUCTS_next_page(self):
        ''' Once on the products page, navigates to the next one'''
        next_page_ele = self.driver.find_element_by_css_selector(".product-page pagination .next a")
        next_page_ele.click()

    def PRODUCTS_get_productpage_data(self):
        ''' Once on the subcategory of the PGECP management interface, gathers all ids and PGECP links of the
        products in current page '''
        product_card_eles = self.driver.find_elements_by_css_selector(".product-card.card")
        product_page_list = []
        for product_card_ele in product_card_eles:
            product_id = product_card_ele.find_elements_by_css_selector\
            (".card-container .card-section.media .card-section-container a figure img").get_attribute("alt")
            PGECP_id = product_card_ele.find_elements_by_css_selector\
            (".card-container .card-section.actions .card-section-container a").get_attribute("href")
            product_page_list.append(product_id, PGECP_id)
        return product_page_list
