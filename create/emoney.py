from imports import *
from timestamp import generate_timestamp
from signature import generate_signature


BALANCE_TYPES = [
    "DANABALANCE",
    "SHOPEEBALANCE",
    "LINKAJABALANCE",
    "OVOBALANCE",
    "GOPAYBALANCE",
]


def create_emoney_payment(
    merchant_id: str,
    private_key_pem: str,
    amount: float,
    product_name: str,
    product_info: List[Dict[str, Any]],
    payment_type: str = None,
    phone_number: str = None,
    redirect_url: str = "http://google.com",
    notify_url: str = None,
    base_url: str = "https://sit-pay.paylabs.co.id",
    endpoint: str = "/payment/v2.3/ewallet/create",
    timestamp: str = None,
):

    if not timestamp:
        timestamp = generate_timestamp()

    if not payment_type:
        payment_type = random.choice(BALANCE_TYPES)

    request_id = "REQ-" + str(uuid.uuid4())
    merchant_trade_no = f"TRX-{uuid.uuid4().hex[:27]}"

    # Build paymentParams based on payment type
    payment_params = {"redirectUrl": redirect_url}
    if payment_type == "OVOBALANCE" and phone_number:
        payment_params["phoneNumber"] = phone_number

    payload = {
        "merchantId": merchant_id,
        "merchantTradeNo": merchant_trade_no,
        "requestId": request_id,
        "paymentType": payment_type,
        "amount": f"{float(amount):.2f}",
        "productName": product_name[:100],
        "productInfo": product_info,
        "paymentParams": payment_params,
    }

    if notify_url:
        payload["notifyUrl"] = notify_url

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