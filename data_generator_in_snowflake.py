import pandas as pd
import random
from faker import Faker
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from dotenv import load_dotenv
import os
import string

load_dotenv()

try:
    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        role=os.getenv("SNOWFLAKE_ROLE"),
    )

    def generate_customers(customers: int, seed: int = 42) -> pd.DataFrame:
        random.seed(seed)
        fake = Faker('fr_FR')
        Faker.seed(seed)

        rows = []
        for cid in range(1, customers + 1):
            name = fake.name()
            email = f"{fake.user_name()}@gmail.com" if random.random() > 0.1 else None
            address = fake.street_address() if random.random() > 0.1 else None
            city = fake.city()
            password = fake.password(length=12)

            rows.append(
                {
                    "customer_id": cid,
                    "customer_name": name,
                    "customer_email": email,
                    "password": password,
                    "address": address,
                    "city": city
                }
            )

        df = pd.DataFrame(rows)
        return df

    customers_df = generate_customers(customers=50, seed=42)

    table_name_customers = "CUSTOMERS"
    write_pandas(
        conn,
        customers_df,
        table_name_customers,
        auto_create_table=True,
        overwrite=False,
    )

    def generate_wines(wines: int = 500, seed: int = 42) -> pd.DataFrame:
        random.seed(seed)
        fake = Faker('fr_FR')
        Faker.seed(seed)

        colors = ['white', 'red', 'orange']
        sweetness_levels = ['dry', 'off-dry', 'sweet']
        bottle_sizes = [0.375, 0.75, 1.5]
        grapes_list = [
            'Merlot', 'Grenache', 'Viognier', 'Pinot Gris', 'Tempranillo', 'Albarino', 'Chardonnay',
            'Semillon', 'Riesling', 'Pinot Noir', 'Rkatsiteli', 'Sangiovese', 'Syrah', 'Nebbiolo',
            'Chenin Blanc', 'Gewurztraminer', 'Sauvignon Blanc', 'Cabernet Sauvignon', 'Muscadet',
            'Zinfandel', 'Malbec'
        ]

        country_data = {
            'France': {
                'regions': ['Rhone', 'Bordeaux', 'Loire', 'Alsace', 'Provence', 'Jura', 'Champagne', 'Languedoc', 'Beaujolais', 'Burgundy'],
                'appellations': {
                    'Rhone': ['Crozes-Hermitage', 'Hermitage', 'Cote-Rotie', 'Chateauneuf-du-Pape'],
                    'Bordeaux': ['Saint-Emilion', 'Pomerol', 'Graves', 'Medoc', 'Pauillac'],
                    'Loire': ['Vouvray', 'Muscadet', 'Sancerre', 'Chinon'],
                    'Alsace': ['Alsace AOC'],
                    'Provence': ["Coteaux d'Aix", 'Cotes de Provence'],
                    'Jura': ['Arbois'],
                    'Champagne': ['Champagne AOC'],
                    'Languedoc': ['Corbieres', 'Minervois', 'Faugeres'],
                    'Beaujolais': ['Fleurie', 'Moulin-a-Vent', 'Beaujolais-Villages'],
                    'Burgundy': ['Maconnais', 'Cote de Beaune', 'Cote de Nuits']
                },
                'region_codes': {
                    'Rhone': 'RHO', 'Bordeaux': 'BOR', 'Loire': 'LOI', 'Alsace': 'ALS',
                    'Provence': 'PRO', 'Jura': 'JUR', 'Champagne': 'CHA', 'Languedoc': 'LAN',
                    'Beaujolais': 'BEA', 'Burgundy': 'BUR'
                }
            },
            'Georgia': {
                'regions': ['Kakheti'],
                'appellations': {'Kakheti': ['Kakheti PDO']},
                'region_codes': {'Kakheti': 'KAK'}
            },
            'Italy': {
                'regions': ['Tuscany', 'Sicily', 'Piedmont', 'Veneto'],
                'appellations': {
                    'Tuscany': ['Brunello di Montalcino', 'Chianti Classico', 'Bolgheri'],
                    'Sicily': ['Etna', "Nero d'Avola IGT"],
                    'Piedmont': ['Langhe', 'Barbaresco', 'Barolo'],
                    'Veneto': ['Prosecco', 'Valpolicella', 'Soave']
                },
                'region_codes': {
                    'Tuscany': 'TUS', 'Sicily': 'SIC', 'Piedmont': 'PIE', 'Veneto': 'VEN'
                }
            },
            'Spain': {
                'regions': ['Rioja', 'Ribera del Duero', 'Rias Baixas'],
                'appellations': {
                    'Rioja': ['Rioja DOCa'],
                    'Ribera del Duero': ['Ribera del Duero DO'],
                    'Rias Baixas': ['Rias Baixas DO']
                },
                'region_codes': {
                    'Rioja': 'RIO', 'Ribera del Duero': 'RIB', 'Rias Baixas': 'RIA'
                }
            }
        }

        rows = []
        for wid in range(1, wines + 1):
            country = random.choice(list(country_data.keys()))
            regions = country_data[country]['regions']
            region = random.choice(regions)
            appellations = country_data[country]['appellations'][region]
            appellation = random.choice(appellations)
            region_code = country_data[country]['region_codes'][region]

            vintage = random.randint(1980, 2025)
            num_grapes = random.randint(1, 3)
            grapes = ', '.join(random.sample(grapes_list, num_grapes))

            alcohol_percent = round(random.uniform(11.0, 16.0), 1)
            bottle_size_l = random.choice(bottle_sizes)
            sweetness = random.choice(sweetness_levels)
            tannin = random.randint(1, 5)
            acidity = random.randint(1, 5)
            rating = round(random.uniform(80.0, 100.0), 1)
            price_eur = round(random.uniform(5.0, 100.0), 2)
            producer = random.choice(['Maison', 'Chateau', 'Domaine', 'Bodegas', 'Cantina', 'Winery', 'Estate', 'Marani']) + ' ' + fake.last_name()
            stock_quantity = random.randint(0, 250)

            id_padded = f"{wid:04d}"
            random_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
            reference = f"WN-{vintage}-{region_code}-{id_padded}-{random_code}"

            rows.append({
                "id": wid,
                "reference": reference,
                "color": random.choice(colors),
                "country": country,
                "region": region,
                "appellation": appellation,
                "vintage": vintage,
                "grapes": grapes,
                "alcohol_percent": alcohol_percent,
                "bottle_size_l": bottle_size_l,
                "sweetness": sweetness,
                "tannin": tannin,
                "acidity": acidity,
                "rating": rating,
                "price_eur": price_eur,
                "producer": producer,
                "stock_quantity": stock_quantity
            })

        df = pd.DataFrame(rows)
        return df

    wines_df = generate_wines(wines=500, seed=42)

    table_name_wines = "WINES"
    write_pandas(
        conn,
        wines_df,
        table_name_wines,
        auto_create_table=True,
        overwrite=False,
    )

    fake = Faker('fr_FR')
    random.seed(42)
    rows = []
    customer_ids = list(customers_df["customer_id"])
    wine_ids = list(wines_df["id"])
    for oid in range(1, 101):
        rows.append({
            "order_id": oid,
            "wine_id": random.choice(wine_ids),
            "customer_id": random.choice(customer_ids),
            "order_date": fake.date_time_between(start_date="-1y", end_date="now"),
            "status": random.choice(["pending", "shipped", "delivered"]),
            "quantity": random.randint(1, 10)
        })

    orders_df = pd.DataFrame(rows)

    table_name_orders = "ORDERS"
    write_pandas(
        conn,
        orders_df,
        table_name_orders,
        auto_create_table=True,
        overwrite=False,
    )

    print(f"Inserted {len(customers_df)} customers into {table_name_customers}")
    print(f"Inserted {len(orders_df)} orders into {table_name_orders}")
    print(f"Inserted {len(wines_df)} wines into {table_name_wines}")

except ImportError as e:
    print(f"Error: {e}. Please ensure required packages are installed with '/opt/miniconda3/bin/pip install pandas faker snowflake-connector-python python-dotenv' and try again.")
finally:
    if 'conn' in locals():
        conn.close()
