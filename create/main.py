from imports import *
from timestamp import generate_timestamp
from signature import generate_signature


from qris import create_qris_payment
# from ec import create_dd_payment -> not working ignore
from va import create_va_payment
from cc import create_cc_payment
from emoney import create_emoney_payment

def load_private_key(base_dir: Path, key_env: str):
    key_path = base_dir / os.getenv(key_env)
    with open(key_path, "r") as f:
        return f.read()

def timestamp_month(year: int, month: int, tz_offset: int = 7) -> str:
    """
    Generate ISO-8601 timestamp with:
    - specified year and month
    - random valid day
    - random hour, minute, second
    - timezone offset (default +07:00)

    Example output:
    2026-03-17T14:23:51+07:00
    """

    # Validate month
    if not 1 <= month <= 12:
        raise ValueError("Month must be between 1 and 12")

    # Get correct number of days in month (handles leap year)
    _, max_day = calendar.monthrange(year, month)

    day = random.randint(1, max_day)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)

    tz = timezone(timedelta(hours=tz_offset))

    dt = datetime(year, month, day, hour, minute, second, tzinfo=tz)

    # Format to ISO-8601 with colon in timezone
    timestamp = dt.strftime("%Y-%m-%dT%H:%M:%S%z")
    return timestamp[:-2] + ":" + timestamp[-2:]

def load_random_products(product_path: Path, max_items=8):
    df = pd.read_csv(product_path)
    random_select_product = df.sample(n=random.randint(1, max_items))

    return random_select_product


load_dotenv()
BASE_DIR = Path(__file__).parent

merchant_id = os.getenv("MID")
private_key_pem = load_private_key(BASE_DIR, "PRIVATE_KEY_PATH")

product_path = BASE_DIR / os.getenv("PRODUCT_PATH")
random_select_product = load_random_products(product_path)
selected_product = random_select_product["ProductName"].tolist()
selected_amount = random_select_product["Price"].sum()
productInfo = []

for idx, row in random_select_product.iterrows():
    productInfo.append({
        "id": str(idx)[:10],
        "name": str(row["ProductName"])[:32],
        "price": f"{float(row['Price']):.2f}",
        "type": "FNB",
        "url": "https://yourdomain.com/product",
        "quantity": 1
    })

# response = create_qris_payment(
    # merchant_id=merchant_id,
    # private_key_pem=private_key_pem,
    # amount=selected_amount,
    # product_name="FNB",
    # product_info=productInfo
# )



# print("Status Code:", response.status_code)
# print("Response:", response.text)


# response = create_dd_payment(
#     merchant_id=merchant_id,
#     private_key_pem=private_key_pem,
#     amount=selected_amount,
#     product_name="FNB",
#     product_info=productInfo
# )



# print("Status Code:", response.status_code)
# print("Response:", response.text)

response = create_va_payment(
    merchant_id=merchant_id,
    private_key_pem=private_key_pem,
    amount=selected_amount,
    product_name="FNB",
    product_info=productInfo
)



print("Status Code:", response.status_code)
print("Response:", response.text)


# response = create_cc_payment(
    # merchant_id=merchant_id,
    # private_key_pem=private_key_pem,
    # amount=selected_amount,
    # product_name="FNB",
    # product_info=productInfo
# )

# print("Status Code:", response.status_code)
# print("Response:", response.text)

# response = create_emoney_payment(
#     merchant_id=merchant_id,
#     private_key_pem=private_key_pem,
#     amount=selected_amount,
#     product_name="FNB",
#     product_info=productInfo
# )

# print("Status Code:", response.status_code)
# print("Response:", response.text)