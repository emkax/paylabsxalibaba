from imports import *
from timestamp import generate_timestamp
from signature import generate_signature


def create_cc_payment(
    merchant_id: str,
    private_key_pem: str,
    amount: float,
    product_info: List[Dict[str, Any]],
    product_name: str,
    redirect_url: str = "http://google.com",
    base_url: str = "https://sit-pay.paylabs.co.id",
    endpoint: str = "/payment/v2.3/cc/create",
    timestamp: str = None,
):

    if not timestamp:
        timestamp = generate_timestamp()

    request_id = "REQ-" + str(uuid.uuid4())
    merchant_trade_no = f"TRX-{uuid.uuid4().hex[:27]}"

    payload = {
        "merchantId": merchant_id,
        "merchantTradeNo": merchant_trade_no,
        "requestId": request_id,
        "paymentType": "CreditCard",
        "amount": f"{float(amount):.2f}",
        "productName": product_name[:100],
        "productInfo": product_info,
        "paymentParams": {
            "redirectUrl": redirect_url,
        },
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