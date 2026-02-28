from imports import *
from timestamp import generate_timestamp
from signature import generate_signature



def create_qris_payment(
    merchant_id: str,
    private_key_pem: str,
    amount: float,
    product_name: str,
    product_info: List[Dict[str, Any]],
    base_url: str = "https://sit-pay.paylabs.co.id",
    endpoint: str = "/payment/v2.3/qris/create",
    tz_offset: int = 7,
    timestamp: str = None,
):

    if not timestamp:
        timestamp = generate_timestamp(tz_offset)

    request_id = "REQ-" + str(uuid.uuid4())
    merchant_trade_no = f"TRX-{uuid.uuid4().hex[:27]}"

    payload = {
        "merchantId": merchant_id,
        "merchantTradeNo": merchant_trade_no,
        "requestId": request_id,
        "paymentType": "QRIS",
        "amount": f"{float(amount):.2f}",
        "productName": product_name[:100],
        "productInfo": product_info,
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