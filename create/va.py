from imports import *
from timestamp import generate_timestamp
from signature import generate_signature


VA_BANK = [
    "SinarmasVA",
    "MaybankVA",
    "DanamonVA",
    "BNCVA",
    "BCAVA",
    "INAVA",
    "BNIVA",
    "PermataVA",
    "MuamalatVA",
    "BSIVA",
    "BRIVA",
    "MandiriVA",
    "CIMBVA",
    "NobuVA",
    "KaltimtaraVA",
    "BTNVA",
]


def create_va_payment(
    merchant_id: str,
    private_key_pem: str,
    amount: float,
    product_name: str,
    product_info: List[Dict[str, Any]],
    payment_type: str = None,
    payer: str = "dummy",
    base_url: str = "https://sit-pay.paylabs.co.id",
    endpoint: str = "/payment/v2.3/va/create",
    timestamp: str = None,
):

    if not timestamp:
        timestamp = generate_timestamp()

    if not payment_type:
        payment_type = random.choice(VA_BANK)

    request_id = "REQ-" + str(uuid.uuid4())
    merchant_trade_no = f"TRX-{uuid.uuid4().hex[:27]}"

    payload = {
        "merchantId": merchant_id,
        "merchantTradeNo": merchant_trade_no,
        "requestId": request_id,
        "paymentType": payment_type,
        "amount": f"{float(amount):.2f}",
        "productName": product_name[:100],
        "productInfo": product_info,
        "payer": payer,
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