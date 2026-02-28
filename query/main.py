from imports import *
from timestamp import generate_timestamp
from signature import generate_signature

def load_private_key(base_dir: Path, key_env: str):
    key_path = base_dir / os.getenv(key_env)
    with open(key_path, "r") as f:
        return f.read()

def inquiry_qris(
    merchant_id,
    private_key_pem,
    merchant_trade_no,
    base_url="https://sit-pay.paylabs.co.indonesia",
    endpoint="/payment/v2.3/qris/query",
    timestamp=None
):
    if not timestamp:
        timestamp = generate_timestamp()

    request_id = "REQ-" + str(uuid.uuid4())

    payload = {
        "requestId": request_id,
        "merchantId": merchant_id,
        "merchantTradeNo": merchant_trade_no,
    }

    body = json.dumps(payload, separators=(",", ":"))

    signature = generate_signature(
        private_key_pem=private_key_pem,
        method="POST",
        endpoint=endpoint,
        body=body,
        timestamp=timestamp,
    )

    response = requests.post(
        f"{base_url}{endpoint}",
        headers={
            "Content-Type": "application/json;charset=utf-8",
            "X-TIMESTAMP": timestamp,
            "X-SIGNATURE": signature,
            "X-PARTNER-ID": merchant_id,
            "X-REQUEST-ID": request_id,
        },
        data=body,
        timeout=10,
    )

    return response

load_dotenv()
BASE_DIR = Path(__file__).parent

merchant_id = os.getenv("MID")
private_key_pem = load_private_key(BASE_DIR, "PRIVATE_KEY_PATH")

response = inquiry_qris(merchant_id="010614",private_key_pem=private_key_pem,merchant_trade_no="TRX-c203eab069084c408f5d4bc68a0")

print("Status Code:", response.status_code)
print("Response:", response.text)
