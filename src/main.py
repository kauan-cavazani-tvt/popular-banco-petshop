from service.generator import DataGenerator
from config.env import NUM_RECORDS_CUSTOMER

def main():
    generator = DataGenerator()
    generator.generate_and_insert_customers(NUM_RECORDS_CUSTOMER)
    generator.generate_and_insert_address(NUM_RECORDS_CUSTOMER)
    generator.generate_and_insert_pets()
    generator.generate_and_insert_customer_address()
    generator.generate_and_insert_order()
    generator.generate_and_insert_order_item()
    generator.generate_and_insert_request()

if __name__ == "__main__":
    main()