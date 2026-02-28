from imports import *
from timestamp import generate_timestamp
from signature import generate_signature

PAYMENT_TYPE = ["Kredivo", "Indodana", "Atome"]


def create_dd_payment(
    merchant_id: str,
    private_key_pem: str,
    amount: float,
    product_name: str,
    product_info: List[Dict[str, Any]],
    phone_number: str = None,
    payment_type: str = None,
    base_url: str = "https://sit-pay.paylabs.co.id",
    endpoint: str = "/payment/v2.3/dd/create",
    timestamp: str = None,
):

    if not timestamp:
        timestamp = generate_timestamp()

    if not payment_type:
        payment_type = random.choice(PAYMENT_TYPE)

    if not phone_number:
        phone_number = "08" + "".join(
            str(random.randint(0, 9)) for _ in range(random.randint(9, 11))
        )


    request_id = "REQ-" + str(uuid.uuid4())
    merchant_trade_no = f"TRX-{uuid.uuid4().hex[:27]}"

    if payment_type == "Indodana":
        payment_params = {
            "redirectUrl": "http://google.com"
        }

    elif payment_type == "Kredivo":
        payment_params = {
            "phoneNumber": phone_number,
            "successUrl": "http://google.com",
            "failedUrl": "http://google.com"
        }

    elif payment_type == "Atome":
        payment_params = {
            "phoneNumber": phone_number,
            "successUrl": "http://google.com",
            "failedUrl": "http://google.com"
        }

    else:
        raise ValueError("Unsupported payment type")

    payload = {
        "merchantId": merchant_id,
        "merchantTradeNo": merchant_trade_no,
        "requestId": request_id,
        "paymentType": payment_type,
        "amount": f"{float(amount):.2f}",
        "productName": product_name[:100],
        "productInfo": product_info,
        "notifyUrl": "https://yourdomain.com/callback",
        "feeType": "BEN",
        "paymentParams": payment_params
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