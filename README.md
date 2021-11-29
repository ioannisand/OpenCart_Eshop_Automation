# OpenCart_Eshop_Automation
Overview:
  During my work as a web developer and eshop manager at an eshop built on Opencart, the most time consuming and boring part 
  of the job was to update the availability and prices of the products of some of  the suppliers, based on their corresponding values, 
  taking into consideration the competition, in a popular greek ecommerce platform (will be referred to as PGECP), and create new products when needed. 
  Most of the work was done through the opencart backend interface (mostly through the quick edit extension module), and the platform developed 
  by the PGECP company. 
  Due to lack of direct access to the database, as well as lack of api endpoints for some of the suppliers, this was done completely manually.
  This project is a collection of tools that mostly utilize the selenium and requests libraries of python to automate the majority of the aforementioned taks.
  Initially, it was a collection of 2-3 scripts doing exactly what needed to be done, but this led to reduced customizability and need to rewrite much of the 
  code each time changes needed to be done in the work process. To avoid this, 2 manager classes were created to handle opencart backend interface and the 
  PGECP management platform respectivelly( those can be found in /toolkit/managers.py ), whose methods are used to navigate and work through their respective environments,
  using webdrivers, as both platforms have web browser interfaces.
