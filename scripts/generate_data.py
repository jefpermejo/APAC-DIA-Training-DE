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

    # Orders Header fact table generation (partitioned)
    TARGET_ORDERS = 1000000
    num_orders = int(TARGET_ORDERS * args.scale)
    print(f"Generating {num_orders} orders header...")

    valid_customer_ids = list(range(1, int(80000 * args.scale) + 1))
    valid_store_ids = list(range(1, int(5000 * args.scale) + 1))

    start_date = date(2024, 1, 1)
    num_days = 90  # Spread orders over 90 days
    orders_per_day = num_orders // num_days
    remainder = num_orders % num_days

    channels = ['web', 'pos']
    payment_methods = ['card', 'cash', 'paypal', 'giftcard']
    currencies = ['AUD', 'USD', 'EUR']

    duplicate_count = int(num_orders * 0.0005)
    duplicate_order_ids = random.sample(range(1, num_orders+1), duplicate_count)

    invalid_fk_count = int(num_orders * 0.01)
    invalid_customer_ids = [-(i+1) for i in range(invalid_fk_count//2)]
    invalid_store_ids = [-(i+1) for i in range(invalid_fk_count//2)]

    order_id = 1
    for day in range(num_days):
        order_dt = start_date + timedelta(days=day)
        part_dir = out / f"orders/order_dt={order_dt.isoformat()}"
        ensure_dir(part_dir)
        part_path = part_dir / "part-1.csv"
        with part_path.open('w', encoding='utf-8') as f:
            f.write('order_id,order_ts,order_dt_local,customer_id,store_id,channel,payment_method,coupon_code,shipping_fee,currency\n')
            n_orders = orders_per_day + (1 if day < remainder else 0)
            for i in range(n_orders):
                # Duplicate order_id anomaly
                if order_id in duplicate_order_ids:
                    use_order_id = random.choice(duplicate_order_ids)
                else:
                    use_order_id = order_id

                # Foreign key anomaly
                if order_id <= invalid_fk_count:
                    customer_id = random.choice(invalid_customer_ids)
                    store_id = random.choice(invalid_store_ids)
                else:
                    customer_id = random.choice(valid_customer_ids)
                    store_id = random.choice(valid_store_ids)

                order_ts = datetime.combine(order_dt, datetime.min.time(), tzinfo=timezone.utc) + timedelta(seconds=random.randint(0, 86399))
                order_dt_local = order_dt.isoformat()
                channel = random.choice(channels)
                payment_method = random.choice(payment_methods)
                coupon_code = '' if random.random() > 0.2 else f"COUPON-{rstr.rstr('A-Z0-9', 6)}"
                shipping_fee = f"{round(np.random.normal(10, 5), 2):.2f}"
                currency = random.choice(currencies)
                f.write(f"{use_order_id},{order_ts.isoformat()}Z,{order_dt_local},{customer_id},{store_id},{channel},{payment_method},{coupon_code},{shipping_fee},{currency}\n")
                order_id += 1

    print(f"✅ Orders header written to partitioned directories in {out}/orders/")

    # Orders Lines fact table generation (partitioned)
    TARGET_ORDER_LINES = 4000000
    num_order_lines = int(TARGET_ORDER_LINES * args.scale)
    print(f"Generating {num_order_lines} order lines...")

    valid_product_ids = list(range(1, int(25000 * args.scale) + 1))
    invalid_product_count = int(num_order_lines * 0.01)
    invalid_product_ids = [-(i+1) for i in range(invalid_product_count)]

    # For partitioning, reuse order header partitioning
    order_line_id = 1
    line_number = 1
    order_lines_per_order = max(1, num_order_lines // num_orders)
    remainder_lines = num_order_lines % num_orders

    # For each order partition
    order_id = 1
    for day in range(num_days):
        order_dt = start_date + timedelta(days=day)
        part_dir = out / f"orders/order_dt={order_dt.isoformat()}"
        ensure_dir(part_dir)
        part_path = part_dir / "order_lines.csv"
        with part_path.open('w', encoding='utf-8') as f:
            f.write('order_id,line_number,product_id,qty,unit_price,line_discount_pct,tax_pct\n')
            n_orders = orders_per_day + (1 if day < remainder else 0)
            for i in range(n_orders):
                # For each order, generate lines
                n_lines = order_lines_per_order + (1 if order_id <= remainder_lines else 0)
                for ln in range(1, n_lines + 1):
                    # 1% invalid product_id
                    if order_line_id <= invalid_product_count:
                        product_id = random.choice(invalid_product_ids)
                    else:
                        product_id = random.choice(valid_product_ids)

                    # Rare negative qty or zero price
                    if random.random() < 0.002:
                        qty = -random.randint(1, 5)
                    else:
                        qty = random.randint(1, 10)
                    if random.random() < 0.002:
                        unit_price = 0.0
                    else:
                        unit_price = round(np.random.uniform(5, 2000), 4)

                    line_discount_pct = round(np.random.uniform(0, 0.5), 4)
                    tax_pct = round(np.random.uniform(0.05, 0.15), 4)
                    f.write(f"{order_id},{ln},{product_id},{qty},{unit_price:.4f},{line_discount_pct:.4f},{tax_pct:.4f}\n")
                    order_line_id += 1
                order_id += 1
    print(f"✅ Order lines written to partitioned directories in {out}/orders/ (order_lines.csv)")

    # Events table generation (JSONL, partitioned)
    TARGET_EVENTS = 2000000
    num_events = int(TARGET_EVENTS * args.scale)
    print(f"Generating {num_events} events...")

    event_types = ['page_view', 'add_to_cart', 'purchase', 'login', 'logout', 'search']
    malformed_count = int(num_events * 0.0005)
    missing_envelope_count = int(num_events * 0.0005)

    start_event_date = date(2024, 1, 1)
    num_event_days = 60
    events_per_day = num_events // num_event_days
    remainder_events = num_events % num_event_days

    event_id = 1
    for day in range(num_event_days):
        event_dt = start_event_date + timedelta(days=day)
        part_dir = out / f"events/event_dt={event_dt.isoformat()}"
        ensure_dir(part_dir)
        part_path = part_dir / f"events_{day+1}.jsonl"
        with part_path.open('w', encoding='utf-8') as f:
            n_events = events_per_day + (1 if day < remainder_events else 0)
            for i in range(n_events):
                # Malformed JSON anomaly
                if event_id <= malformed_count:
                    f.write('{"event_id": ' + str(event_id) + ', "event_ts": "MALFORMED"\n')
                # Missing envelope anomaly
                elif event_id <= malformed_count + missing_envelope_count:
                    payload = {"action": random.choice(event_types), "meta": {"info": fake.word()}}
                    f.write(f'{payload}\n')
                else:
                    envelope = {
                        "event_id": event_id,
                        "event_ts": (datetime.combine(event_dt, datetime.min.time(), tzinfo=timezone.utc) + timedelta(seconds=random.randint(0, 86399))).isoformat() + 'Z',
                        "event_type": random.choice(event_types),
                        "user_id": random.randint(1, 100000),
                        "session_id": f"SESS-{rstr.rstr('A-Z0-9', 10)}"
                    }
                    payload = {
                        "action": envelope["event_type"],
                        "meta": {"info": fake.word(), "amount": round(random.uniform(1, 500), 2)}
                    }
                    event_obj = {"envelope": envelope, "payload": payload}
                    import json
                    f.write(json.dumps(event_obj) + '\n')
                event_id += 1
    print(f"✅ Events written to partitioned directories in {out}/events/")

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
