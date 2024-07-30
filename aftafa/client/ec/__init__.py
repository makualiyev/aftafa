"""
We have 1C objects (документы, справочники, регистры накопления) with their table parts such as "Заказ клиента", 
"Реализация товаров и услуг", "Приобретение товаров и услуг" and etc. We download the data from this objects and
their table parts using the builtin report "Универсальный отчет" with pre set parameters.
Documents have their unique ID (GUID) and each table part entry in theory should have a unique row id (`ec_row_id`)
if nothing went wrong in accounting part and maintenance of the platform. But surprisingly these row IDs can be du-
plicated in the platform
"""
