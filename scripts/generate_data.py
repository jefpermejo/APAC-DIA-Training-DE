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
