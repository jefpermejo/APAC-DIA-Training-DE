# Generate synthetic raw data locally with controlled edge cases.
# Usage: python scripts/generate_data.py --seed 42 --out data_raw
import argparse, os, pathlib, random
from datetime import datetime, timedelta, date, timezone
import numpy as np
from faker import Faker
from mimesis import Person, Address
import rstr
import pyarrow as pa
import pyarrow.parquet as pq
import xlsxwriter

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--out', type=str, default='data_raw/samples')
    ap.add_argument('--scale', type=float, default=0.01)
    return ap.parse_args()

def ensure_dir(p): pathlib.Path(p).mkdir(parents=True, exist_ok=True)

def main():
    args = parse_args()
    random.seed(args.seed); np.random.seed(args.seed)
    out = pathlib.Path(args.out); ensure_dir(out)

    # Customer table generation
    TARGET_CUSTOMERS = 80000
    num_customers = int(TARGET_CUSTOMERS * args.scale)
    print(f"Generating {num_customers} customers...") 

    malformed_email_count = int(num_customers * 0.01)
    duplicate_nk_count = int(num_customers * 0.002)
    null_phone_count = int(num_customers * 0.01)
    null_address_count = int(num_customers * 0.01)
    duplicate_nks = [f'CUST-{rstr.rstr("A-Z0-9", 8)}' for _ in range(duplicate_nk_count)]

    fake = Faker('en_AU')
    customers_path = out/'customers.csv'
    with customers_path.open('w', encoding='utf-8') as f:
        f.write('customer_id,natural_key,first_name,last_name,email,phone,address_line1,address_line2,city,state_region,postcode,country_code,latitude,longitude,birth_date,join_ts,is_vip,gdpr_consent\n')
        for i in range(1, num_customers + 1):
            # Inject anomalies
            email = 'bad_email' if i <= malformed_email_count else fake.email()
            nk = duplicate_nks[i % duplicate_nk_count] if i <= duplicate_nk_count else 'CUST-' + rstr.rstr('A-Z0-9', 8)
            phone = '' if i <= null_phone_count else fake.phone_number().replace(',', ' ')
            address_line1 = '' if i <= null_address_count else fake.street_address().replace(',', ' ')
            lat = -44 + random.random()*10; lon = 112 + random.random()*40
            birth = date(1960,1,1) + timedelta(days=random.randint(0, 20000))
            join_ts = datetime(2024,1,1, tzinfo=timezone.utc) + timedelta(days=random.randint(0, 400), seconds=random.randint(0, 86399))
            f.write(f"{i},{nk},{fake.first_name()},{fake.last_name()},{email},{phone},{address_line1},,{fake.city().replace(',',' ')},{fake.state_abbr()},{fake.postcode()},AU,{lat:.6f},{lon:.6f},{birth.isoformat()},{join_ts.isoformat()}Z,{str(random.random()<0.15)},{str(random.random()>0.05)}\n")
    
    # Products table generation
    TARGET_PRODUCTS = 25000
    num_products = int(TARGET_PRODUCTS * args.scale)
    print(f"Generating {num_products} products...")

    malformed_price_count = int(num_products * 0.005)  # 0.5% invalid/missing prices
    null_discontinued_count = int(num_products * 0.1)  # 10% discontinued products with null discontinued_dt

    categories = ['Electronics', 'Clothing', 'Home', 'Toys', 'Food']
    subcategories = {
        'Electronics': ['Phones', 'Computers', 'Audio'],
        'Clothing': ['Men', 'Women', 'Kids'],
        'Home': ['Furniture', 'Kitchen', 'Decor'],
        'Toys': ['Outdoor', 'Board', 'Educational'],
        'Food': ['Snacks', 'Drinks', 'Pantry']
    }
    currencies = ['AUD', 'USD', 'EUR']

    products_path = out/'products.csv'
    with products_path.open('w', encoding='utf-8') as f:
        f.write('product_id,sku,name,category,subcategory,current_price,currency,introduced_dt,discontinued_dt,is_discontinued\n')
        for i in range(1, num_products + 1):
            sku = 'SKU-' + rstr.rstr('A-Z0-9', 6)
            category = random.choice(categories)
            subcategory = random.choice(subcategories[category])
            name = f"{category} {subcategory} {fake.word().capitalize()}"
            # Price anomaly injection
            if i <= malformed_price_count:
                price = '' if i % 2 == 0 else '-9999.99'  # missing or invalid
            else:
                price = f"{round(random.uniform(5, 2000), 4):.4f}"
            currency = random.choice(currencies)
            introduced_dt = date(2010,1,1) + timedelta(days=random.randint(0, 5000))
            is_discontinued = random.random() < 0.15
            introduced_dt_dt = datetime.combine(introduced_dt, datetime.min.time(), tzinfo=timezone.utc)
            discontinued_dt = '' if (is_discontinued and i <= null_discontinued_count) else (
                (introduced_dt_dt + timedelta(days=random.randint(30, 2000))).isoformat() + 'Z' if is_discontinued else ''
            )
            f.write(f"{i},{sku},{name},{category},{subcategory},{price},{currency},{introduced_dt_dt.isoformat()}Z,{discontinued_dt},{str(is_discontinued)}\n")

    # Stores table generation
    TARGET_STORES = 5000
    num_stores = int(TARGET_STORES * args.scale)
    print(f"Generating {num_stores} stores...")

    impossible_latlon_count = int(num_stores * 0.01)  # 1% impossible lat/lon
    duplicate_code_count = int(num_stores * 0.01)     # 1% duplicate store_codes
    channels = ['web', 'pos']
    regions = ['North', 'South', 'East', 'West', 'Central']
    states = ['NSW', 'VIC', 'QLD', 'WA', 'SA', 'TAS', 'ACT', 'NT']
    fake_store_codes = [f"STORE-{rstr.rstr('A-Z0-9', 6)}" for _ in range(duplicate_code_count)]

    stores_path = out/'stores.csv'
    with stores_path.open('w', encoding='utf-8') as f:
        f.write('store_id,store_code,name,channel,region,state,latitude,longitude,open_dt,close_dt\n')
        for i in range(1, num_stores + 1):
            # Duplicate store_code anomaly
            store_code = fake_store_codes[i % duplicate_code_count] if i <= duplicate_code_count else f"STORE-{rstr.rstr('A-Z0-9', 6)}"
            name = f"{fake.city()} {random.choice(['Mall', 'Outlet', 'Shop', 'Market'])}"
            channel = random.choice(channels)
            region = random.choice(regions)
            state = random.choice(states)
            # Impossible lat/lon anomaly
            if i <= impossible_latlon_count:
                latitude = random.choice([999, -999, 91, -91])
                longitude = random.choice([999, -999, 181, -181])
            else:
                latitude = -44 + random.random()*10
                longitude = 112 + random.random()*40
            open_dt = date(2010,1,1) + timedelta(days=random.randint(0, 5000))
            open_dt_dt = datetime.combine(open_dt, datetime.min.time(), tzinfo=timezone.utc)
            is_active = random.random() < 0.8
            close_dt = '' if is_active else (open_dt_dt + timedelta(days=random.randint(30, 3000))).isoformat() + 'Z'
            f.write(f"{i},{store_code},{name},{channel},{region},{state},{latitude},{longitude},{open_dt_dt.isoformat()}Z,{close_dt}\n")

    # Suppliers table generation
    TARGET_SUPPLIERS = 8000
    num_suppliers = int(TARGET_SUPPLIERS * args.scale)
    print(f"Generating {num_suppliers} suppliers...")

    suppliers_path = out/'suppliers.csv'
    with suppliers_path.open('w', encoding='utf-8') as f:
        f.write('supplier_id,supplier_code,name,country_code,lead_time_days,preferred\n')
        for i in range(1, num_suppliers + 1):
            supplier_code = f"SUP-{rstr.rstr('A-Z0-9', 6)}"
            name = fake.company()
            country_code = fake.country_code()
            lead_time_days = random.randint(2, 60)
            preferred = str(random.random() < 0.2)
            f.write(f"{i},{supplier_code},{name},{country_code},{lead_time_days},{preferred}\n")
        
'''
    # Shipments parquet sample
    tbl = pa.table({
        'shipment_id': pa.array(range(1, 10001), type=pa.int64()),
        'order_id': pa.array(range(1, 10001), type=pa.int64()),
        'carrier': pa.array(['AUSPOST']*10000, type=pa.string()),
        'shipped_at': pa.array([datetime(2024,1,1)+timedelta(days=i%90) for i in range(10000)], type=pa.timestamp('us')),
        'delivered_at': pa.array([datetime(2024,1,2)+timedelta(days=i%90) for i in range(10000)], type=pa.timestamp('us')),
        'ship_cost': pa.array([1995]*10000, type=pa.int64()).cast(pa.decimal128(12,2)),
    })
    pq.write_table(tbl, out/'shipments.parquet', compression='snappy')

    print(f"✅ Sample raw written to {out}. Expand to required volumes per /docs.")
'''
if __name__ == '__main__':
    main()
