# PayLabs x Alibaba - Payment Gateway Integration

## Project Overview

This is a **hackathon project** that implements a Python-based payment gateway integration for **PayLabs Indonesia**. The project provides tools to create and query payment transactions across multiple Indonesian payment methods, including QRIS, Virtual Accounts, Credit Cards, E-Wallets, and PayLater services.

## Repository Structure

```
paylabsxalibaba/
├── create/                      # Payment creation module
│   ├── main.py                  # Main entry point for creating payments
│   ├── imports.py               # Shared imports
│   ├── signature.py             # Request signature generation
│   ├── timestamp.py             # Timestamp generation (WIB/WITA/WIT timezone)
│   ├── qris.py                  # QRIS payment creation
│   ├── va.py                    # Virtual Account payment creation
│   ├── cc.py                    # Credit Card payment creation
│   ├── emoney.py                # E-Wallet payment creation
│   ├── ec.py                    # Installment/DD payment creation (Kredivo, Indodana, Atome)
│   ├── seeding.py               # Bulk transaction seeder for testing
│   ├── product.csv              # Sample product data (50 F&B items)
│   ├── .env                     # Environment configuration
│   └── public_key.pem           # Public key for authentication
│
├── query/                       # Payment query module
│   ├── main.py                  # Main entry point for querying payments
│   ├── imports.py               # Shared imports
│   ├── signature.py             # Request signature generation
│   ├── timestamp.py             # Timestamp generation
│   └── product.csv              # Sample product data
│
├── .gitignore                   # Git ignore rules
└── CONTEXT.md                   # This file
```

## Core Technologies

- **Language**: Python 3.11+
- **Key Dependencies**:
  - `cryptography` - RSA signature generation
  - `requests` - HTTP client for API calls
  - `pandas` - Product data handling
  - `python-dotenv` - Environment variable management

## Payment Methods Supported

### 1. QRIS (Quick Response Code Indonesian Standard)
- **File**: `create/qris.py`
- **Endpoint**: `/payment/v2.3/qris/create`
- **API**: `create_qris_payment()`

### 2. Virtual Accounts (VA)
- **File**: `create/va.py`
- **Endpoint**: `/payment/v2.3/va/create`
- **API**: `create_va_payment()`
- **Supported Banks**: SinarmasVA, MaybankVA, DanamonVA, BNCVA, BCAVA, INAVA, BNIVA, PermataVA, MuamalatVA, BSIVA, BRIVA, MandiriVA, CIMBVA, NobuVA, KaltimtaraVA, BTNVA

### 3. Credit Cards
- **File**: `create/cc.py`
- **Endpoint**: `/payment/v2.3/cc/create`
- **API**: `create_cc_payment()`

### 4. E-Wallets
- **File**: `create/emoney.py`
- **Endpoint**: `/payment/v2.3/ewallet/create`
- **API**: `create_emoney_payment()`
- **Supported**: DANABALANCE, SHOPEEBALANCE, LINKAJABALANCE, OVOBALANCE, GOPAYBALANCE

### 5. Installment/PayLater (Direct Debit)
- **File**: `create/ec.py`
- **Endpoint**: `/payment/v2.3/dd/create`
- **API**: `create_dd_payment()`
- **Supported**: Kredivo, Indodana, Atome

## Authentication & Security

### Request Signing
All API requests are authenticated using **RSA-SHA256 signatures**:

1. **Signature String**: `{METHOD}:{ENDPOINT}:{SHA256_BODY}:{TIMESTAMP}`
2. **Signing**: RSA private key signs the signature string
3. **Headers Required**:
   - `X-TIMESTAMP` - ISO-8601 timestamp with timezone offset
   - `X-SIGNATURE` - Base64-encoded RSA signature
   - `X-PARTNER-ID` - Merchant ID
   - `X-REQUEST-ID` - Unique request identifier (UUID format)

### Key Files
- `private_key.pem` - RSA private key (not committed to git)
- `public_key.pem` - RSA public key (not committed to git)

## Configuration

### Environment Variables (`.env`)
```
MID=010614                          # Merchant ID
PRIVATE_KEY_PATH=private_key.pem    # Private key file path
PUBLIC_KEY_PATH=public_key.pem      # Public key file path
PRODUCT_PATH=product.csv            # Product data file path
```

## API Base URLs

- **SIT (Staging)**: `https://sit-pay.paylabs.co.id`
- Note: Some query endpoints use `https://sit-pay.paylabs.co.indonesia` (may be a typo)

## Main Components

### Signature Generation (`signature.py`)
```python
def generate_signature(private_key_pem, method, endpoint, body, timestamp)
```
Generates RSA-SHA256 signature for request authentication.

### Timestamp Generation (`timestamp.py`)
```python
def generate_timestamp(tz_offset=7)
```
Generates ISO-8601 timestamp with milliseconds and timezone offset (default: UTC+7/WIB).

### Product Data
The `product.csv` contains **50 F&B (Food & Beverage) products** across categories:
- Burgers, Wraps, Pizza, Pasta, Rice dishes
- Snacks, Hotdogs, Sandwiches
- Beverages (milkshakes, coffee, tea, smoothies)
- Desserts (brownies, cheesecake, tiramisu, ice cream)
- Salads, Main Courses (steak, salmon, fish & chips)

## Usage Examples

### Create a Payment
```python
from create.main import *
from create.va import create_va_payment

response = create_va_payment(
    merchant_id="010614",
    private_key_pem="-----BEGIN RSA PRIVATE KEY-----...",
    amount=50000,
    product_name="FNB",
    product_info=[{"id": "1", "name": "Burger", "price": "50000", ...}]
)
```

### Bulk Transaction Seeding
The `seeding.py` module can generate hundreds of test transactions:
```python
from seeding import run_seeding
run_seeding(n=300)  # Creates 300 random transactions
```

### Query Payment Status
```python
from query.main import inquiry_qris

response = inquiry_qris(
    merchant_id="010614",
    private_key_pem="...",
    merchant_trade_no="TRX-..."
)
```

## Request/Response Format

### Create Payment Payload
```json
{
  "merchantId": "010614",
  "merchantTradeNo": "TRX-<uuid>",
  "requestId": "REQ-<uuid>",
  "paymentType": "QRIS|VA|CreditCard|...",
  "amount": "50000.00",
  "productName": "FNB",
  "productInfo": [
    {
      "id": "1",
      "name": "Product Name",
      "price": "50000.00",
      "type": "FNB",
      "url": "https://yourdomain.com/product",
      "quantity": 1
    }
  ]
}
```

## Recent Git History

| Commit | Message |
|--------|---------|
| b33576d | Merge branch 'master' |
| 20774b8 | Add: data query |
| bdf9f32 | Delete private_key.pem (security) |
| afc2850 | Base implementation |
| 42bf412 | Add: bulk seeding |

## Known Issues/Notes

1. **ec.py (Direct Debit)** is marked as "not working - ignore" in main.py
2. **Empty/Stub Files**: `cc_subscription.py`, `otc.py`, `dana_subscription.py` exist but are empty
3. **Duplicate Code**: `query/` module duplicates signature/timestamp utilities (could be refactored)
4. **URL Typo**: Query endpoint uses `.co.indonesia` instead of `.co.id`
5. **Private keys** are properly excluded from git (security best practice)

## Testing

The project includes a bulk seeder for stress testing:
- Runs 300+ transactions by default
- Random payment method selection
- Random product selection (1-8 items)
- Configurable year/month for timestamp testing
- Rate limiting delay (0.3s default between requests)

## Project Status

This appears to be an **active hackathon project** with:
- Core payment creation functionality implemented
- Query functionality for transaction status
- Bulk testing/seeding capabilities
- Multiple payment methods integrated
