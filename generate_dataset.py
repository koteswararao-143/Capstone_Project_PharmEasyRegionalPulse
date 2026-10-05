"""
Create the deterministic PharmEasy practice dataset.

The seed and generation rules are intentionally kept exactly as supplied
in the assignment brief.
"""
import random
import csv
from collections import defaultdict

rng = random.Random(2026)

REGIONS_ACTIVE = [
    "Hyderabad", "Warangal", "Vijayawada", "Visakhapatnam",
    "Guntur", "Nellore", "Tirupati", "Karimnagar", "Bengaluru",
]
REGION_ZERO_ORDERS = "Kurnool"
REGIONS_MASTER = REGIONS_ACTIVE + [REGION_ZERO_ORDERS]

STATE_OF = {
    "Hyderabad": "Telangana", "Warangal": "Telangana", "Karimnagar": "Telangana",
    "Vijayawada": "Andhra Pradesh", "Visakhapatnam": "Andhra Pradesh",
    "Guntur": "Andhra Pradesh", "Nellore": "Andhra Pradesh", "Tirupati": "Andhra Pradesh",
    "Kurnool": "Andhra Pradesh", "Bengaluru": "Karnataka",
}

TIER_OF = {
    "Hyderabad": "Tier-1", "Bengaluru": "Tier-1",
    "Vijayawada": "Tier-2", "Visakhapatnam": "Tier-2", "Warangal": "Tier-2",
    "Guntur": "Tier-2", "Nellore": "Tier-2", "Tirupati": "Tier-2",
    "Karimnagar": "Tier-3", "Kurnool": "Tier-3",
}

CATEGORIES = [
    "OTC Medicines", "Prescription Medicines", "Wellness & Nutrition",
    "Personal Care", "Medical Devices", "Lab Tests",
]
CAT_WEIGHTS = [0.30, 0.22, 0.18, 0.14, 0.10, 0.06]

PRODUCTS = {
    "OTC Medicines": ["Paracetamol 500mg", "Cetirizine 10mg", "ORS Sachet", "Cough Syrup 100ml", "Antacid Tablets"],
    "Prescription Medicines": ["Metformin 500mg", "Amlodipine 5mg", "Atorvastatin 10mg", "Azithromycin 500mg", "Insulin Pen"],
    "Wellness & Nutrition": ["Multivitamin Tablets", "Whey Protein 1kg", "Fish Oil Capsules", "Immunity Booster Syrup", "Calcium + D3 Tablets"],
    "Personal Care": ["Sunscreen SPF50", "Hand Sanitizer 500ml", "Face Wash", "Antiseptic Liquid", "Baby Diaper Pack"],
    "Medical Devices": ["Digital BP Monitor", "Pulse Oximeter", "Glucometer Kit", "Nebulizer", "Thermometer"],
    "Lab Tests": ["Full Body Checkup", "Thyroid Profile", "Vitamin D Test", "HbA1c Test", "Lipid Profile"],
}

UNIT_PRICE = {
    "OTC Medicines": (40, 220),
    "Prescription Medicines": (90, 650),
    "Wellness & Nutrition": (250, 1400),
    "Personal Care": (80, 550),
    "Medical Devices": (350, 3200),
    "Lab Tests": (400, 1800),
}

MONTHS = [("2026-04", 30), ("2026-05", 31), ("2026-06", 30)]

REGION_BASE_WEIGHT = {
    "Hyderabad": 22, "Bengaluru": 16, "Vijayawada": 13, "Visakhapatnam": 12,
    "Warangal": 9, "Guntur": 9, "Nellore": 8, "Tirupati": 7, "Karimnagar": 4,
}

REGION_MONTH_MULTIPLIER = {
    "2026-04": defaultdict(lambda: 1.00),
    "2026-05": defaultdict(lambda: 1.00),
    "2026-06": defaultdict(lambda: 1.00),
}
REGION_MONTH_MULTIPLIER["2026-05"]["Visakhapatnam"] = 0.45
REGION_MONTH_MULTIPLIER["2026-06"]["Visakhapatnam"] = 0.70
REGION_MONTH_MULTIPLIER["2026-06"]["Hyderabad"] = 1.35

TARGET_ORDERS_PER_MONTH = 700

base_rows = []
sequence = 1

for month, number_of_days in MONTHS:
    weights = [
        REGION_BASE_WEIGHT[name] * REGION_MONTH_MULTIPLIER[month][name]
        for name in REGIONS_ACTIVE
    ]

    for _ in range(TARGET_ORDERS_PER_MONTH):
        region = rng.choices(REGIONS_ACTIVE, weights=weights, k=1)[0]
        category = rng.choices(CATEGORIES, weights=CAT_WEIGHTS, k=1)[0]
        product = rng.choice(PRODUCTS[category])

        day = rng.randint(1, number_of_days)
        order_date = f"{month}-{day:02d}"

        quantity = rng.randint(1, 5)
        low, high = UNIT_PRICE[category]
        unit_price = round(rng.uniform(low, high), 2)
        sales = round(unit_price * quantity, 2)

        margin_rate = rng.uniform(0.08, 0.22)
        profit = round(sales * margin_rate, 2)

        base_rows.append({
            "order_id": f"PE{sequence:05d}",
            "order_date": order_date,
            "region": region,
            "category": category,
            "product": product,
            "quantity": quantity,
            "sales_inr": sales,
            "profit_inr": profit,
        })
        sequence += 1

working_rows = [row.copy() for row in base_rows]

for index in rng.sample(range(len(working_rows)), 94):
    working_rows[index]["profit_inr"] = ""

for index in rng.sample(range(len(working_rows)), 48):
    working_rows[index]["category"] = ""

messy_region_values = {
    "Hyderabad": [" hyderabad", "HYDERABAD ", "Hyderabad"],
    "Bengaluru": ["bengaluru ", " BENGALURU", "Bengaluru"],
    "Vijayawada": ["vijayawada", " Vijayawada ", "VIJAYAWADA"],
}

for index in rng.sample(range(len(working_rows)), 161):
    region = working_rows[index]["region"]
    if region in messy_region_values:
        working_rows[index]["region"] = rng.choice(messy_region_values[region])

duplicate_indexes = rng.sample(range(len(working_rows)), 59)
duplicates = [working_rows[index].copy() for index in duplicate_indexes]

raw_rows = working_rows + duplicates
rng.shuffle(raw_rows)

with open("pharmeasy_orders_raw.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=[
            "order_id", "order_date", "region", "category",
            "product", "quantity", "sales_inr", "profit_inr"
        ],
    )
    writer.writeheader()
    writer.writerows(raw_rows)

with open("regions_master.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["region", "state", "tier"])
    writer.writeheader()

    for region in REGIONS_MASTER:
        writer.writerow({
            "region": region,
            "state": STATE_OF[region],
            "tier": TIER_OF[region],
        })

assert len(raw_rows) == 2159
assert len(REGIONS_MASTER) == 10

print(
    f"Wrote pharmeasy_orders_raw.csv ({len(raw_rows)} rows) "
    f"and regions_master.csv ({len(REGIONS_MASTER)} rows)."
)
