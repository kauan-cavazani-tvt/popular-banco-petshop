from faker import Faker
from utils.utils import clean_phone_number
from datetime import date, datetime, timedelta
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

        status_probabilities = {
            2: 0.8,
            3: 0.2
        }

        status = random.choices(
            list(status_probabilities.keys()), 
            weights=list(status_probabilities.values())
        )[0]

        return {
            "customer_id": customer_id,
            "order_date": self.faker.date_between(start_date=datetime(2023, 1, 1), end_date=datetime(2023, 12, 31)).strftime("%Y-%m-%d %H:%M:%S"),
            "status_id": status,
            "address_id": address_id
        }
    
    def generate_order_item(self, product_id, order_id):
        """Gera dados falsos de associação entre produto e pedido."""

        quantity_probabilities = {
            1: 0.6,
            2: 0.5,
            3: 0.3,
            4: 0.2,
            5: 0.1
        }

        quantity = random.choices(
            list(quantity_probabilities.keys()), 
            weights=list(quantity_probabilities.values())
        )[0]

        return {
            "order_id": order_id,
            "product_id": product_id,
            "quantity": quantity
        }
    
    def generate_request(self, service_id, pet_id, address_id):
        """Gera dados falsos de solicitação."""

        status_probabilities = {
            6: 0.8,
            7: 0.2
        }

        status = random.choices(
            list(status_probabilities.keys()), 
            weights=list(status_probabilities.values())
        )[0]

        request_date = self.faker.date_between(start_date=date(2023, 1, 1), end_date=date(2023, 12, 31))
        request_datetime = datetime.strptime(request_date.strftime("%Y-%m-%d"), "%Y-%m-%d")

        # Calcule o intervalo de tempo para adicionar à request_date
        min_days = 1
        max_days = 30 
        days_to_add = random.randint(min_days, max_days)
        service_date = request_datetime + timedelta(days=days_to_add)

        return {
            "service_id": service_id,
            "pet_id": pet_id,
            "request_date": request_date.strftime("%Y-%m-%d %H:%M:%S"),
            "status_id": status,
            "service_date": service_date.strftime("%Y-%m-%d %H:%M:%S"),
            "address_id": address_id
        }