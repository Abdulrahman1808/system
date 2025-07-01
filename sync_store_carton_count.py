import json
import math

STORE_PRODUCTS_PATH = 'mongodb_data/store_products.json'

def fix_nan(val):
    # Replace NaN (from Excel or pandas) with empty string
    if isinstance(val, float) and math.isnan(val):
        return ''
    if val == 'NaN' or val is None:
        return ''
    return val

def main():
    with open(STORE_PRODUCTS_PATH, 'r', encoding='utf-8') as f:
        products = json.load(f)

    for prod in products:
        # دمج quantity إلى carton_count
        if 'quantity' in prod:
            prod['carton_count'] = prod['quantity']
        # إصلاح NaN في flavor
        if 'flavor' in prod:
            prod['flavor'] = fix_nan(prod['flavor'])

    with open(STORE_PRODUCTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main() 