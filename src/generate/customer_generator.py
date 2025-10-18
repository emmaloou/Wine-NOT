
import argparse
import csv
import random
from pathlib import Path
from faker import Faker

def random_date_format(dt, rng):
    style = rng.choice(["iso", "eu", "us"])
    if style == "iso":
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    elif style == "eu":
        return dt.strftime("%d/%m/%Y %H:%M")
    else:
        return dt.strftime("%m-%d-%Y %H:%M:%S")

def sanitize_email_name(name: str) -> str:
    s = name.lower().replace(" ", ".").replace("'", "")
    s = "".join(ch for ch in s if ch.isalnum() or ch == ".")
    return s

def main():
    ap = argparse.ArgumentParser(description="Generate customers.csv with mixed date formats and ~5% duplicates.")
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--dup_ratio", type=float, default=0.05)
    ap.add_argument("--out", type=Path, default=Path("customers.csv"))
    args = ap.parse_args()

    fake = Faker()
    Faker.seed(42)
    rng = random.Random(42)

    rows = []
    for i in range(1, args.n + 1):
        name = fake.name()
        email_local = sanitize_email_name(name) + str(rng.randint(1, 999))
        email = email_local + "@example.com"
        reg_date = fake.date_time_between(start_date="-3y", end_date="now")
        country = rng.choice(["France", "Italy", "Spain", "USA", "Portugal", "Germany", "Belgium"])
        city = fake.city()

        rows.append({
            "customer_id": i,
            "customer_name": name,
            "customer_email": email,
            "password": fake.password(length=12),
            "registration_date": random_date_format(reg_date, rng),
            "country": country,
            "city": city,
        })

    dup_count = max(1, int(args.dup_ratio * len(rows)))
    dups = rng.choices(rows, k=dup_count)
    all_rows = rows + dups
    rng.shuffle(all_rows)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Wrote {len(all_rows)} rows to {args.out} (including {dup_count} duplicates).")

if __name__ == "__main__":
    main()
