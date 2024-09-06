from service.database import Database
from lib.faker import FakeDataGenerator
from utils.utils import classify_product, get_products_for_customer, get_allowed_services
import random

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
        specie_probabilities = {
            1: 0.7,
            2: 0.7,
            3: 0.3,
            4: 0.3, 
            5: 0.2,
            6: 0.2 
        }

        quantity_pets_probabilities = {
            1: 0.8,
            2: 0.4,
            3: 0.2
        }

        pet_data = []
        for customer_id in customer_ids:
            num_pets = random.choices(
                list(quantity_pets_probabilities.keys()), 
                weights=list(quantity_pets_probabilities.values())
            )[0]

            for _ in range(num_pets):
                specie_id = random.choices(
                    list(specie_probabilities.keys()), 
                    weights=list(specie_probabilities.values())
                )[0]

                breed_ids_per_species = [breed for breed in breed_ids if breed["SPECIE_ID"] == specie_id]

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

        state_ids = [state['STATE_ID'] for state in state_ids]

        # Buscando cidades dos estados onde existe loja
        city_ids = self.db.search(
            table_name="CITY c", 
            columns=["c.ID"],
            join="JOIN STATE s ON c.STATE_ID = s.ID",
            where="s.ID IN (%s)",
            where_params=state_ids
        )
        
        address_data = []
        for _ in range(num_records):
            fake_address = self.fake_data.generate_address(city_ids)
            address_data.append(fake_address)

        columns = ["POSTAL_CODE", "STREET", "NUMBER", "COMPLEMENT", "NEIGHBORHOOD", "CITY_ID", "ADDRESS_TYPE_ID"]
        self.db.insert("ADDRESS", columns, address_data)
        self.db.close_conn()

    def generate_and_insert_customer_address(self):
        """Gera e insere dados de associação entre cliente e endereço."""
        self.db.open_conn()

        customer_ids = self.db.search(table_name="CUSTOMER", columns=["ID"])
        address_ids = self.db.search(table_name="ADDRESS", columns=["ID"], where="ADDRESS_TYPE_ID = %s", where_params=("1",))
        
        customer_address_data = []
        for customer_id in customer_ids:
            address_id = random.choice(address_ids)
            customer_address_data.append((customer_id["ID"], address_id["ID"]))

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
            where="c.STATE_ID IN (%s)",
            where_params=state_ids
        )

        order_data = []
        for customer_address in customer_address_ids:
            # 40% de chance de ser um cliente ativo e 60% de não ser ativo
            num_orders = random.randint(6, 20) if random.random() < 0.4 else random.randint(1, 5)
            for _ in range(num_orders):
                fake_order = self.fake_data.generate_order(customer_address["CUSTOMER_ID"], customer_address["ADDRESS_ID"])
                order_data.append(fake_order)

        columns = ["CUSTOMER_ID", "ORDER_DATE", "STATUS_ID", "ADDRESS_ID"]
        self.db.insert("CUSTOMER_ORDER", columns, order_data)
        self.db.close_conn()

    def generate_and_insert_order_item(self):
        """Gera e insere itens do pedido no banco de dados."""

        self.db.open_conn()

        orders = self.db.search(
            table_name="CUSTOMER_ORDER co",
            columns=["co.ID", "co.CUSTOMER_ID", "ct.STATE_ID"],
            join="JOIN address a ON a.ID = co.ADDRESS_ID JOIN city ct ON ct.ID = a.CITY_ID"
        )

        state_ids = [order["STATE_ID"] for order in orders]

        stores = self.db.search(
            table_name="STORE s",
            columns=["s.ID", "c.STATE_ID"],
            join="JOIN address a ON a.ID = s.ADDRESS_ID JOIN city c ON c.ID = a.CITY_ID",
            where="c.STATE_ID IN (%s)",
            where_params=state_ids
        )

        products = self.db.search(
            table_name="PRODUCT p",
            columns=["p.ID", "p.NAME", "p.DESCRIPTION", "p.SKU", "p.STORE_ID"]
        )

        species_per_customer = self.db.search(
            table_name="PET p",
            columns=["p.CUSTOMER_ID", "s.NAME"],
            join="JOIN BREED b ON b.ID = p.BREED_ID JOIN SPECIE s ON s.ID = b.SPECIE_ID"
        )

        quantity_probabilities = {
            (1, 3): 0.5,
            (4, 5): 0.3,
            (6, 7): 0.2,
            (8, 10): 0.1
        }

        order_item_data = []
        for order in orders:
            # Escolhe uma faixa de quantidade com base nas probabilidades
            quantity_range = random.choices(
                list(quantity_probabilities.keys()), 
                weights=list(quantity_probabilities.values())
            )[0]

            quantity = random.randint(quantity_range[0], quantity_range[1])

            # Busca as lojas do mesmo estado do pedido
            stores_in_same_state = [store for store in stores if store["STATE_ID"] == order["STATE_ID"]]
            store_id = random.choice(stores_in_same_state)["ID"]

            # Busca os produtos da loja selecionada
            products_of_store = [product for product in products if product["STORE_ID"] == store_id]

            # Classifica os produtos por espécie
            classified_products = classify_product(products_of_store)

            # Busca as espécies do cliente
            specie_of_customer = [specie for specie in species_per_customer if specie["CUSTOMER_ID"] == order["CUSTOMER_ID"]]

            # Separa os produtos que o cliente pode comprar com base na espécie do seu animal
            products_for_customer = get_products_for_customer(classified_products, specie_of_customer)

            for _ in range(quantity):
                if products_for_customer:
                    product_id = random.choice(products_for_customer)
                else:
                    product_id = random.choice(products_of_store)["ID"]
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
            columns=["s.ID", "ss.STORE_ID", "a.CITY_ID"],
            join="JOIN STORE_SERVICE ss ON ss.SERVICE_ID = s.ID JOIN STORE st ON st.ID = ss.STORE_ID JOIN ADDRESS a ON a.ID = st.ADDRESS_ID"
        )

        request_data = []
        for pet in pets:
            num_requests = random.randint(6, 20) if random.random() < 0.4 else random.randint(1, 5)
            
            services_same_city = [service for service in services if service["CITY_ID"] == pet["CITY_ID"]]
            
            if not services_same_city:
                continue 

            for _ in range(num_requests):
                allowed_services = get_allowed_services(pet["SPECIE_ID"], services_same_city)
                if allowed_services:
                    service_id = random.choice(allowed_services)["ID"]
                    
                    fake_request = self.fake_data.generate_request(service_id, pet["ID"], pet["ADDRESS_ID"])
                    request_data.append(fake_request)

        columns = ["SERVICE_ID", "PET_ID", "REQUEST_DATE", "STATUS_ID", "SERVICE_DATE", "ADDRESS_ID"]
        self.db.insert("REQUEST", columns, request_data)
        self.db.close_conn()