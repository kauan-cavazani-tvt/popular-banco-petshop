import re
import random

def clean_phone_number(phone_number):
    """Remove caracteres não numéricos e retorna o telefone no formato DDD + número."""
    digits_only = re.sub(r'\D', '', phone_number)
    
    if len(digits_only) != 11:
        return generate_random_number_phone()
    
    return digits_only

def generate_random_number_phone():
    """Gera um número de telefone no formato DDD + número."""
    ddd = f"{random.randint(11, 99):02d}"  # Garante que o DDD tenha 2 dígitos
    number = f"{random.randint(100000000, 999999999):09d}"  # Garante que o número tenha 9 dígitos
    return f"{ddd}{number}"

def classify_product(products):
    categories = {
        'CACHORRO': 'CACHORRO',
        'CAES': 'CACHORRO',
        'CAO': 'CACHORRO',
        'DOG': 'CACHORRO',
        'GATOS': 'GATO',
        'GATO': 'GATO',
        'CAT': 'GATO',
        'PEIXES': 'PEIXE',
        'PEIXE': 'PEIXE',
        'FISH': 'PEIXE',
        'PASSARO': 'PASSARO',
        'BIRD': 'PASSARO',
        'HAMSTER': 'HAMSTER',
        'COELHO': 'COELHO'
    }
    
    classification = []

    for product in products:
        produto_classificado = 'Desconhecido'
        
        for keyword, animal in categories.items():
            if keyword in product['NAME'] or keyword in product['DESCRIPTION'] or keyword in product['SKU']:
                produto_classificado = animal
                break
        
        classification.append((product['ID'], produto_classificado))
    
    return classification

def get_products_for_customer(classified_products, species_of_customer):
    relevant_products = []

    for product_id, product_species in classified_products:
        if any(specie["NAME"].lower() == product_species.lower() for specie in species_of_customer):
            relevant_products.append(product_id)

    return relevant_products

def get_allowed_services(specie_id, services):
    # Cachorros e Gatos podem usar todos os serviços
    # Passaros, hamster e coelhos podem apenas solicitar consulta veterinária
    allowed_services_for_pets = {
        1: "all", 
        2: "all",  
        4: [4],
        5: [4],
        6: [4] 
    }

    if specie_id in allowed_services_for_pets:
        allowed_services = allowed_services_for_pets[specie_id]
        if allowed_services == "all":
            return services
        else:
            return [service for service in services if service["ID"] in allowed_services]

    return []