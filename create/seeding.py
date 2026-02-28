from imports import *
from timestamp import generate_timestamp
from signature import generate_signature

from qris import create_qris_payment
from va import create_va_payment
from cc import create_cc_payment
from emoney import create_emoney_payment


def load_private_key(base_dir: Path, key_env: str):
    key_path = base_dir / os.getenv(key_env)
    with open(key_path, "r") as f:
        return f.read()

#CANNOT SPOOF TIMESTAMP!!!
def timestamp_month(year: int, month: int, tz_offset: int = 7) -> str:
    if not 1 <= month <= 12:
        raise ValueError("Month must be between 1 and 12")

    _, max_day = calendar.monthrange(year, month)
    day = random.randint(1, max_day)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    ms = random.randint(0, 999)

    tz = timezone(timedelta(hours=tz_offset))
    dt = datetime(year, month, day, hour, minute, second, tzinfo=tz)
    timestamp = dt.strftime("%Y-%m-%dT%H:%M:%S") + f".{ms:03d}" + dt.strftime("%z")
    return timestamp[:-2] + ":" + timestamp[-2:]


def load_random_products(product_path: Path, max_items: int = 8):
    df = pd.read_csv(product_path)
    n = random.randint(1, min(max_items, len(df)))
    sample = df.sample(n=n)
    return sample


def build_product_info(df_sample) -> tuple[list, float, str]:
    product_info = []
    for idx, row in df_sample.iterrows():
        product_info.append({
            "id": str(idx)[:10],
            "name": str(row["ProductName"])[:32],
            "price": f"{float(row['Price']):.2f}",
            "type": "FNB",
            "url": "https://yourdomain.com/product",
            "quantity": 1,
        })
    selected_product = df_sample["ProductName"].tolist()
    selected_amount = float(df_sample["Price"].sum())
    product_name = "FNB"
    return product_info, selected_amount, product_name


PAYMENT_METHODS = ["qris", "va", "cc", "emoney"]


def seed_transaction(
    merchant_id: str,
    private_key_pem: str,
    product_path: Path,
    year: int,
    month: int,
) -> dict:
    """Run a single seeded transaction with random method and products."""

    sample = load_random_products(product_path)
    product_info, amount, product_name = build_product_info(sample)
    timestamp = generate_timestamp()
    method = random.choice(PAYMENT_METHODS)

    common = dict(
        merchant_id=merchant_id,
        private_key_pem=private_key_pem,
        amount=amount,
        product_name=product_name,
        timestamp=timestamp,
    )

    try:
        if method == "qris":
            response = create_qris_payment(**common,product_info=product_info)

        elif method == "va":
            response = create_va_payment(**common, product_info=product_info)

        elif method == "cc":
            response = create_cc_payment(**common, product_info=product_info)

        elif method == "emoney":
            response = create_emoney_payment(**common, product_info=product_info)

        return {
            "method": method,
            "amount": amount,
            "timestamp": timestamp,
            "status_code": response.status_code,
            "response": response.text,
        }

    except Exception as e:
        return {
            "method": method,
            "amount": amount,
            "timestamp": timestamp,
            "status_code": None,
            "response": str(e),
        }


def run_seeding(
    n: int = 50,
    year: int = None,
    month: int = None,
    delay: float = 0.3,
):
    """
    Seed n transactions for the given year/month (defaults to current month).

    Args:
        n:      Number of transactions to seed
        year:   Target year  (default: current year)
        month:  Target month (default: current month)
        delay:  Seconds to wait between requests to avoid rate limiting
    """
    load_dotenv()
    BASE_DIR = Path(__file__).parent

    merchant_id = os.getenv("MID")
    private_key_pem = load_private_key(BASE_DIR, "PRIVATE_KEY_PATH")
    product_path = BASE_DIR / os.getenv("PRODUCT_PATH")

    now = datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month

    print(f"\n{'='*60}")
    print(f"  Seeding {n} transactions  |  {year}-{month:02d}")
    print(f"{'='*60}\n")

    results = []
    success = 0
    failed = 0

    for i in range(1, n + 1):
        result = seed_transaction(
            merchant_id=merchant_id,
            private_key_pem=private_key_pem,
            product_path=product_path,
            year=year,
            month=month,
        )
        results.append(result)

        status = "✓" if result["status_code"] == 200 else "✗"
        if result["status_code"] == 200:
            success += 1
        else:
            failed += 1

        print(
            f"[{i:>3}/{n}] {status} | {result['method']:<8} | "
            f"Rp {result['amount']:>12,.2f} | "
            f"HTTP {result['status_code']} | "
            f"{result['timestamp']}"
        )

        if i < n:
            time.sleep(delay)

    print(f"\n{'='*60}")
    print(f"  Done  |  ✓ {success} success  |  ✗ {failed} failed")
    print(f"{'='*60}\n")

    return results


if __name__ == "__main__":
    run_seeding(n=300)