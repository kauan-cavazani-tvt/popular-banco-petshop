from faker import Faker
from utils.utils import clean_phone_number
from config.probabilities import getConfig
from datetime import datetime, timedelta
import random

class FakeDataGenerator:
    def __init__(self):
        self.faker = Faker("pt_BR")

    def generate_customer(self):
        """Gera dados falsos para um cliente."""
        return {
            "name": self.faker.name(),
            "email": self.faker.email(),
            "phone": clean_phone_number(self.faker.phone_number())
        }
    
    def generate_pet(self, breed_ids, size_ids, customer_id):
        """Gera dados falsos para um pet."""

        return {
            "name": self.faker.first_name(),
            "date_birth": self.faker.date_of_birth(minimum_age=0, maximum_age=20).strftime("%Y-%m-%d"),
            "breed_id": random.choice(breed_ids)["ID"],
            "size_id": random.choice(size_ids)["ID"],
            "customer_id": customer_id["ID"]
        }
    
    def generate_address(self, city_ids):
        """Gera dados falsos para um endereço."""

        complements = [
            None,
            f"Apto {self.faker.building_number()}",
            f"Bloco {self.faker.building_number()}",
            f"Casa {self.faker.building_number()}",
            f"Conjunto {self.faker.building_number()}"
        ]

        return {
            "postal_code": self.faker.postcode()[:8],
            "street": self.faker.street_name(),
            "number": self.faker.building_number(),
            "complement": random.choice(complements),
            "neighborhood": self.faker.bairro(),
            "city_id": random.choice(city_ids)["ID"],
            "address_type_id": 1
        }
    
    def generate_order(self, customer_id, address_id):
        """Gera dados falsos para um pedido."""

        start_date_str = getConfig("start_date")
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")

        end_date_str = getConfig("end_date")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        status_order_probabilities = getConfig("status_order_probabilities")

        status = random.choices(
            list(status_order_probabilities.keys()), 
            weights=list(status_order_probabilities.values())
        )[0]

        return {
            "customer_id": customer_id,
            "order_date": self.faker.date_time_between(start_date=start_date, end_date=end_date).strftime("%Y-%m-%d %H:%M:%S"),
            "status_id": status,
            "address_id": address_id
        }
    
    def generate_order_item(self, product_id, order_id):
        """Gera dados falsos de associação entre produto e pedido."""

        quantity_order_items_probabilities = getConfig("quantity_order_items_probabilities")

        quantity = random.choices(
            list(quantity_order_items_probabilities.keys()), 
            weights=list(quantity_order_items_probabilities.values())
        )[0]

        return {
            "order_id": order_id,
            "product_id": product_id,
            "quantity": quantity
        }
    
    def generate_request(self, service_id, pet_id, address_id):
        """Gera dados falsos de solicitação."""

        start_date_str = getConfig("start_date")
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        
        end_date_str = getConfig("end_date")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        status_request_probabilities = getConfig("status_request_probabilities")

        status = random.choices(
            list(status_request_probabilities.keys()), 
            weights=list(status_request_probabilities.values())
        )[0]

        request_date = self.faker.date_time_between(start_date=start_date, end_date=end_date)
        request_datetime = datetime.strptime(request_date.strftime("%Y-%m-%d"), "%Y-%m-%d")

        # Calcule o intervalo de tempo para adicionar à request_date
        min_days = 1
        max_days = 30 
        days_to_add = random.randint(min_days, max_days)
        service_date = request_datetime + timedelta(days=days_to_add)

        # Gerar uma hora aleatória entre 9h e 18h
        service_hour = random.randint(9, 18)
        service_minute = random.randint(0, 59)
        service_second = random.randint(0, 59)

        # Ajustar a hora da service_date para o intervalo entre 9h e 18h
        service_date = service_date.replace(hour=service_hour, minute=service_minute, second=service_second)

        return {
            "service_id": service_id,
            "pet_id": pet_id,
            "request_date": request_date.strftime("%Y-%m-%d %H:%M:%S"),
            "status_id": status,
            "service_date": service_date.strftime("%Y-%m-%d %H:%M:%S"),
            "address_id": address_id
        }