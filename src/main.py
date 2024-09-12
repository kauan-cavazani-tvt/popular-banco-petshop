from service.generator import DataGenerator
from config.probabilities import getConfig
import time

def main():
    num_customer = getConfig("number_customer")
    
    generator = DataGenerator()

    # Medir o tempo de execução da função 'generate_and_insert_customers'
    start_time = time.time()
    generator.generate_and_insert_customers(num_customer)
    end_time = time.time()
    print(f"generate_and_insert_customers: {end_time - start_time:.2f} seconds")

    # Medir o tempo de execução da função 'generate_and_insert_address'
    start_time = time.time()
    generator.generate_and_insert_address(num_customer)
    end_time = time.time()
    print(f"generate_and_insert_address: {end_time - start_time:.2f} seconds")

    # Medir o tempo de execução da função 'generate_and_insert_pets'
    start_time = time.time()
    generator.generate_and_insert_pets()
    end_time = time.time()
    print(f"generate_and_insert_pets: {end_time - start_time:.2f} seconds")

    # Medir o tempo de execução da função 'generate_and_insert_customer_address'
    start_time = time.time()
    generator.generate_and_insert_customer_address()
    end_time = time.time()
    print(f"generate_and_insert_customer_address: {end_time - start_time:.2f} seconds")

    # Medir o tempo de execução da função 'generate_and_insert_order'
    start_time = time.time()
    generator.generate_and_insert_order()
    end_time = time.time()
    print(f"generate_and_insert_order: {end_time - start_time:.2f} seconds")

    # Medir o tempo de execução da função 'generate_and_insert_order_item'
    start_time = time.time()
    generator.generate_and_insert_order_item()
    end_time = time.time()
    print(f"generate_and_insert_order_item: {end_time - start_time:.2f} seconds")

    # Medir o tempo de execução da função 'generate_and_insert_request'
    start_time = time.time()
    generator.generate_and_insert_request()
    end_time = time.time()
    print(f"generate_and_insert_request: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()