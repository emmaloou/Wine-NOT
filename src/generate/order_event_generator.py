
import argparse
import json
import random
import time
from datetime import datetime, timedelta
from pathlib import Path

def random_price_format(value, rng):
    style = rng.choice(["euro_symbol", "euro_suffix", "comma", "plain"])
    if style == "euro_symbol":
        return f"€{value:.2f}"
    elif style == "euro_suffix":
        return f"{value:.2f} EUR"
    elif style == "comma":
        return str(round(value, 2)).replace('.', ',')
    return f"{value:.2f}"

def random_date_format(dt, rng):
    style = rng.choice(["iso", "eu", "us"])
    if style == "iso":
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    elif style == "eu":
        return dt.strftime("%d/%m/%Y %H:%M")
    else:
        return dt.strftime("%m-%d-%Y %H:%M:%S")

def generate_order(order_idx, wine_max, cust_max, dt, rng):
    q = rng.randint(1, 6)
    unit = rng.uniform(5, 120)
    total = q * unit
    order_id = f"ORD-2025-{order_idx:06d}"
    return {
        "order_id": order_id,
        "wine_id": rng.randint(1, wine_max),
        "customer_id": rng.randint(1, cust_max),
        "quantity": q,
        "order_date": random_date_format(dt, rng),
        "total_price": random_price_format(total, rng),
        "status": rng.choice(["pending", "confirmed", "shipped", "delivered"]),
        "payment_method": rng.choice(["card", "paypal", "bank_transfer"]),
    }

def main():
    ap = argparse.ArgumentParser(description="Generate order events as JSONL with mixed date/price formats and ~5% duplicates.")
    ap.add_argument("--count", type=int, default=60, help="Number of unique events to generate")
    ap.add_argument("--dup_ratio", type=float, default=0.05, help="Fraction of duplicates to append")
    ap.add_argument("--wine_max", type=int, default=500)
    ap.add_argument("--cust_max", type=int, default=150)
    ap.add_argument("--out", type=Path, default=Path("orders_events.jsonl"))
    ap.add_argument("--sleep", type=float, default=0.0, help="Sleep seconds between events (for demo streaming)")
    args = ap.parse_args()

    rng = random.Random(42)
    base_dt = datetime.utcnow()

    unique = []
    for i in range(1, args.count + 1):
        evt = generate_order(i, args.wine_max, args.cust_max, base_dt + timedelta(seconds=i), rng)
        unique.append(evt)

    dup_count = max(1, int(args.dup_ratio * len(unique)))
    dups = rng.choices(unique, k=dup_count)
    events = unique + dups
    rng.shuffle(events)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
            if args.sleep > 0:
                time.sleep(args.sleep)

    # Optional CSV snapshot
    csv_path = args.out.with_suffix(".csv")
    import csv
    with csv_path.open("w", newline="", encoding="utf-8") as cf:
        writer = csv.DictWriter(cf, fieldnames=list(events[0].keys()))
        writer.writeheader()
        writer.writerows(events)

    print(f"Wrote {len(events)} events to {args.out} (including {dup_count} duplicates).")
    print(f"Also wrote CSV snapshot to {csv_path}.")

if __name__ == "__main__":
    main()
