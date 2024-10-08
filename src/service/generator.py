from service.database import Database
from lib.faker import FakeDataGenerator
from config.probabilities import getConfig
from utils.utils import classify_product, get_products_for_customer, get_allowed_services, get_period_and_probabilities, select_product_id, get_product_type
import random
import re

class DataGenerator:
    def __init__(self):
        self.db = Database()
        self.fake_data = FakeDataGenerator()

    def generate_and_insert_customers(self, num_records):
        """Gera e insere dados de clientes no banco de dados."""
        self.db.open_conn()

        customer_data = []
        for _ in range(num_records):
            fake_customer = self.fake_data.generate_customer()
            customer_data.append(fake_customer)

        columns = ["NAME", "EMAIL", "PHONE"]
        self.db.insert("CUSTOMER", columns, customer_data)
        self.db.close_conn()

    def generate_and_insert_pets(self):
        """Gera e insere dados de pets no banco de dados."""
        self.db.open_conn()

        breed_ids = self.db.search(table_name="BREED", columns=["ID", "SPECIE_ID"])
        size_ids = self.db.search(table_name="SIZE", columns=["ID"])
        customer_ids = self.db.search(table_name="CUSTOMER", columns=["ID"])

        # Maior probabilidade de ser um cachorro ou um gato
        specie_probabilities = getConfig("specie_probabilities")
        quantity_pets_probabilities = getConfig("quantity_pets_probabilities")

        pet_data = []
        for customer_id in customer_ids:
            num_pets = random.choices(
                list(quantity_pets_probabilities.keys()), 
                weights=list(quantity_pets_probabilities.values())
            )[0]

            for _ in range(int(num_pets)):
                specie_id = random.choices(
                    list(specie_probabilities.keys()), 
                    weights=list(specie_probabilities.values())
                )[0]

                breed_ids_per_species = [breed for breed in breed_ids if breed["SPECIE_ID"] == int(specie_id)]
                
                fake_pet = self.fake_data.generate_pet(breed_ids_per_species, size_ids, customer_id)
                pet_data.append(fake_pet)

        columns = ["NAME", "DATE_BIRTH", "BREED_ID", "SIZE_ID", "CUSTOMER_ID"]
        self.db.insert("PET", columns, pet_data)
        self.db.close_conn()

    def generate_and_insert_address(self, num_records):
        """Gera e insere dados de endereços no banco de dados."""
        self.db.open_conn()

        # Busca os ids dos estados onde tem loja
        state_ids = self.db.search(
            table_name="ADDRESS a",
            columns=["DISTINCT c.STATE_ID"],
            join="JOIN city c ON a.CITY_ID = c.ID",
            where="a.ADDRESS_TYPE_ID = 2"
        )

        state_store_ids = [state['STATE_ID'] for state in state_ids]

        # Buscando cidades dos estados onde existe loja
        city_ids = self.db.search(
            table_name="CITY c", 
            columns=["c.ID", "c.STATE_ID"],
            join="JOIN STATE s ON c.STATE_ID = s.ID"
        )

        state_probabilities = getConfig("state_probabilities")
        city_probabilities = getConfig("city_probabilities")
        city_store_ids = [city for city in city_ids if city["STATE_ID"] in state_store_ids]
        city_ids = [city for city in city_ids if city["STATE_ID"] not in state_store_ids]
        
        address_data = []
        for _ in range(num_records):
            state = random.choices(
                list(state_probabilities.keys()), 
                weights=list(state_probabilities.values())
            )[0]

            if state != "other" and int(state) == 25:
                city_id = random.choices(
                    list(city_probabilities.keys()), 
                    weights=list(city_probabilities.values())
                )[0]

                list_city_ids = city_ids if state == "other" else [city for city in city_store_ids if city["ID"] == int(city_id)]
            else:
                list_city_ids = city_ids if state == "other" else [city for city in city_store_ids if city["STATE_ID"] == int(state)]

            fake_address = self.fake_data.generate_address(list_city_ids)
            address_data.append(fake_address)

        columns = ["POSTAL_CODE", "STREET", "NUMBER", "COMPLEMENT", "NEIGHBORHOOD", "CITY_ID", "ADDRESS_TYPE_ID"]
        self.db.insert("ADDRESS", columns, address_data)
        self.db.close_conn()

    def generate_and_insert_customer_address(self):
        """Gera e insere dados de associação entre cliente e endereço, garantindo que cada cliente tenha um endereço único e que todos os endereços sejam associados a clientes."""
        self.db.open_conn()

        # Obter todos os IDs de clientes e endereços
        customer_ids = self.db.search(table_name="CUSTOMER", columns=["ID"])
        address_ids = self.db.search(table_name="ADDRESS", columns=["ID"], where="ADDRESS_TYPE_ID = %s", where_params=("1",))

        # Verificar se o número de endereços é suficiente para os clientes
        if len(address_ids) < len(customer_ids):
            raise ValueError("Número de endereços insuficiente para o número de clientes")

        # Embaralhar os endereços e atribuir um endereço único a cada cliente
        random.shuffle(address_ids)
        customer_address_data = [(customer_id["ID"], address_ids[i]["ID"]) for i, customer_id in enumerate(customer_ids)]

        # Inserir os dados na tabela CUSTOMER_ADDRESS
        columns = ["CUSTOMER_ID", "ADDRESS_ID"]
        self.db.insert("CUSTOMER_ADDRESS", columns, customer_address_data)

        self.db.close_conn()

    def generate_and_insert_order(self):
        """Gera e insere pedidos no banco de dados."""

        self.db.open_conn()

        # Busca os ids dos estados onde tem loja
        state_ids = self.db.search(
            table_name="ADDRESS a",
            columns=["DISTINCT c.STATE_ID"],
            join="JOIN city c ON a.CITY_ID = c.ID",
            where="a.ADDRESS_TYPE_ID = 2"
        )

        state_ids = [state['STATE_ID'] for state in state_ids]

        # Busca os ids dos clientes que moram nos estados onde existe loja 
        customer_address_ids = self.db.search(
            table_name="CUSTOMER_ADDRESS ca",
            columns=["ca.CUSTOMER_ID", "ca.ADDRESS_ID"],
            join="JOIN ADDRESS a ON ca.ADDRESS_ID = a.ID JOIN CITY c ON a.CITY_ID = c.ID",
        )

        active_inactive_customer_probabilities = getConfig("active_customer_order_probabilities")
        range_of_orders_per_customer = getConfig("range_of_orders_per_customer")

        order_data = []
        for customer_address in customer_address_ids:
            type_customer = random.choices(
                list(active_inactive_customer_probabilities.keys()), 
                weights=list(active_inactive_customer_probabilities.values())
            )[0]

            range_orders_str = range_of_orders_per_customer[type_customer]
            numbers = re.findall(r'\d+', range_orders_str)
            range_orders = tuple(map(int, numbers))

            num_orders = random.randint(range_orders[0], range_orders[1])
            for _ in range(num_orders):
                fake_order = self.fake_data.generate_order(customer_address["CUSTOMER_ID"], customer_address["ADDRESS_ID"])
                order_data.append(fake_order)

        columns = ["CUSTOMER_ID", "ORDER_DATE", "STATUS_ID", "ADDRESS_ID"]
        self.db.insert("CUSTOMER_ORDER", columns, order_data)
        self.db.close_conn()

    def generate_and_insert_order_item(self):
        """Gera e insere itens do pedido no banco de dados."""

        self.db.open_conn()

        city_probabilities = getConfig("city_probabilities")

        (warm_period_start, warm_period_end), (cold_period_start, cold_period_end), product_warm_probabilities, product_cold_probabilities = get_period_and_probabilities()

        orders = self.db.search(
            table_name="CUSTOMER_ORDER co",
            columns=["co.ID", "co.ORDER_DATE", "co.CUSTOMER_ID", "a.CITY_ID", "ct.STATE_ID"],
            join="JOIN address a ON a.ID = co.ADDRESS_ID JOIN city ct ON ct.ID = a.CITY_ID"
        )

        state_ids = [order["STATE_ID"] for order in orders]

        stores = self.db.search(
            table_name="STORE s",
            columns=["s.ID", "a.CITY_ID", "c.STATE_ID"],
            join="JOIN address a ON a.ID = s.ADDRESS_ID JOIN city c ON c.ID = a.CITY_ID",
            where="c.STATE_ID IN (%s)",
            where_params=state_ids
        )

        state_ids_from_stores = list(set(store["STATE_ID"] for store in stores))

        products = self.db.search(
            table_name="PRODUCT p",
            columns=["p.ID", "p.NAME", "p.DESCRIPTION", "p.SKU", "p.STORE_ID"]
        )

        species_per_customer = self.db.search(
            table_name="PET p",
            columns=["p.CUSTOMER_ID", "s.NAME"],
            join="JOIN BREED b ON b.ID = p.BREED_ID JOIN SPECIE s ON s.ID = b.SPECIE_ID"
        )

        species_dict = {}

        for specie in species_per_customer:
            customer_id = specie["CUSTOMER_ID"]
            specie_name = specie["NAME"]

            if customer_id not in species_dict:
                species_dict[customer_id] = []
            
            species_dict[customer_id].append(specie_name)

        products_by_store = {}
        for product in products:
            if product["STORE_ID"] not in products_by_store:
                products_by_store[product["STORE_ID"]] = []
            products_by_store[product["STORE_ID"]].append(product)

        quantity_probabilities = getConfig("quantity_order_item_probabilities")

        order_item_data = []
        for order in orders:
            quantity_range_str = random.choices(
                list(quantity_probabilities.keys()), 
                weights=list(quantity_probabilities.values())
            )[0]

            if order["STATE_ID"] in state_ids_from_stores:
                numbers = re.findall(r'\d+', quantity_range_str)
                quantity_range = tuple(map(int, numbers))
                quantity = random.randint(quantity_range[0], quantity_range[1])
            else:
                quantity = random.randint(1, 3)

            # Busca as lojas do mesmo estado do pedido
            if order["STATE_ID"] == 25:
                city_id = random.choices(
                    list(city_probabilities.keys()), 
                    weights=list(city_probabilities.values())
                )[0]
                stores_in_same_state = [store for store in stores if store["CITY_ID"] == int(city_id)]
            else:
                stores_in_same_state = [store for store in stores if store["STATE_ID"] == order["STATE_ID"]]

            store_id = random.choice(stores_in_same_state)["ID"] if stores_in_same_state else random.choice(stores)["ID"]

            products_of_store = products_by_store.get(store_id, [])

            # Classifica os produtos por espécie
            classified_products_per_specie = classify_product(products_of_store)

            # Busca as espécies do cliente
            specie_of_customer = species_dict.get(order["CUSTOMER_ID"], [])

            # Separa os produtos que o cliente pode comprar com base na espécie do seu animal
            products_for_customer = get_products_for_customer(classified_products_per_specie, specie_of_customer)

            for _ in range(quantity):
                product_type = get_product_type(order["ORDER_DATE"], [warm_period_start, warm_period_end], [cold_period_start, cold_period_end], product_warm_probabilities, product_cold_probabilities)
                product_id = select_product_id(product_type, products_for_customer, products_of_store)

                fake_order_item = self.fake_data.generate_order_item(product_id, order["ID"])
                order_item_data.append(fake_order_item) 

        columns = ["ORDER_ID", "PRODUCT_ID", "QUANTITY"]
        self.db.insert("ORDER_ITEM", columns, order_item_data)
        self.db.close_conn()

    def generate_and_insert_request(self):
        """Gera e insere solicitações de serviços no banco de dados."""

        self.db.open_conn()

        pets = self.db.search(
            table_name="PET p",
            columns=["p.ID", "b.SPECIE_ID", "ca.ADDRESS_ID", "a.CITY_ID"],
            join="JOIN CUSTOMER_ADDRESS ca ON ca.CUSTOMER_ID = p.CUSTOMER_ID JOIN ADDRESS a ON a.ID = ca.ADDRESS_ID JOIN BREED b ON b.ID = p.BREED_ID",
            where="b.SPECIE_ID != %s",
            where_params=(3,)
        )

        services = self.db.search(
            table_name="SERVICE s",
            columns=["s.ID", "ss.STORE_ID", "a.CITY_ID", "st.ADDRESS_ID"],
            join="JOIN STORE_SERVICE ss ON ss.SERVICE_ID = s.ID JOIN STORE st ON st.ID = ss.STORE_ID JOIN ADDRESS a ON a.ID = st.ADDRESS_ID"
        )

        active_inactive_customer_probabilities = getConfig("active_customer_request_probabilities")
        range_of_requests_per_customer = getConfig("range_of_requests_per_customer")

        request_data = []
        for pet in pets:
            type_customer = random.choices(
                list(active_inactive_customer_probabilities.keys()), 
                weights=list(active_inactive_customer_probabilities.values())
            )[0]

            range_requests_str = range_of_requests_per_customer[type_customer]
            numbers = re.findall(r'\d+', range_requests_str)
            range_requests = tuple(map(int, numbers))

            num_requests = random.randint(range_requests[0], range_requests[1])
            
            services_filter = [service for service in services if service["CITY_ID"] == pet["CITY_ID"]]
            
            if not services_filter:
                services_filter = services

            for _ in range(num_requests):
                allowed_services = get_allowed_services(pet["SPECIE_ID"], services_filter)
                if allowed_services:
                    random_service = random.choice(allowed_services)
                    service_id = random_service["ID"]
                    address_id = random_service["ADDRESS_ID"]
                    
                    fake_request = self.fake_data.generate_request(service_id, pet["ID"], address_id)
                    request_data.append(fake_request)

        columns = ["SERVICE_ID", "PET_ID", "REQUEST_DATE", "STATUS_ID", "SERVICE_DATE", "ADDRESS_ID"]
        self.db.insert("REQUEST", columns, request_data)
        self.db.close_conn()