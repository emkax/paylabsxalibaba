"""
PayLabs Payment Gateway API Client

This module handles communication with the PayLabs Payment Gateway API,
including signature generation, transaction ingestion, and data synchronization.
"""
import base64
import hashlib
import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from dotenv import load_dotenv

load_dotenv()


class PayLabsClient:
    """
    Client for interacting with PayLabs Payment Gateway API
    """

    def __init__(
        self,
        merchant_id: str = None,
        private_key_path: str = None,
        base_url: str = None
    ):
        self.merchant_id = merchant_id or os.getenv("PAYLABS_MERCHANT_ID", "010614")
        self.base_url = base_url or os.getenv("PAYLABS_API_URL", "https://api-sit.paylabs.co.id")

        # Load private key
        if private_key_path:
            self.private_key_pem = self._load_private_key(private_key_path)
        else:
            # Default path from .env
            key_path = os.getenv("PAYLABS_PRIVATE_KEY_PATH", "private_key.pem")
            self.private_key_pem = self._load_private_key(key_path)

        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "X-Merchant-ID": self.merchant_id
        })

    def _load_private_key(self, key_path: str) -> str:
        """Load private key from file"""
        # Try absolute path first, then relative to backend directory
        if os.path.isabs(key_path):
            path = Path(key_path)
        else:
            path = Path(__file__).parent.parent / key_path

        with open(path, "r") as f:
            return f.read()

    def generate_timestamp(self, tz_offset: int = 7) -> str:
        """
        Generate ISO-8601 timestamp with timezone offset
        Default: +07:00 (WIB - Western Indonesian Time)
        """
        tz = timezone(timedelta(hours=tz_offset))
        dt = datetime.now(tz)
        timestamp = dt.strftime("%Y-%m-%dT%H:%M:%S%z")
        return timestamp[:-2] + ":" + timestamp[-2:]

    def generate_signature(
        self,
        method: str,
        endpoint: str,
        body: str,
        timestamp: str
    ) -> str:
        """
        Generate signature for PayLabs API request

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            body: Request body as string
            timestamp: ISO-8601 timestamp

        Returns:
            Base64-encoded signature
        """
        # Create string to sign
        body_hash = hashlib.sha256(body.encode()).hexdigest()
        string_to_sign = f"{method}:{endpoint}:{body_hash}:{timestamp}"

        # Sign with private key
        private_key = serialization.load_pem_private_key(
            self.private_key_pem.encode(),
            password=None,
        )

        signature = base64.b64encode(
            private_key.sign(
                string_to_sign.encode(),
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
        ).decode()

        return signature

    def _make_request(
        self,
        method: str,
        endpoint: str,
        body: Optional[Dict] = None
    ) -> requests.Response:
        """
        Make authenticated request to PayLabs API
        """
        url = f"{self.base_url}{endpoint}"
        timestamp = self.generate_timestamp()
        body_str = json.dumps(body) if body else ""

        # Generate signature
        signature = self.generate_signature(method, endpoint, body_str, timestamp)

        # Add authentication headers
        headers = {
            "X-Timestamp": timestamp,
            "X-Signature": signature
        }

        # Make request
        if method.upper() == "GET":
            response = self.session.get(url, headers=headers)
        elif method.upper() == "POST":
            response = self.session.post(url, json=body, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        return response

    def get_transactions(
        self,
        start_date: str,
        end_date: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Fetch transactions from PayLabs API

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            limit: Maximum number of transactions to fetch
            offset: Pagination offset

        Returns:
            List of transaction dictionaries
        """
        endpoint = "/v1/transactions"
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "limit": limit,
            "offset": offset
        }

        # Add params to endpoint URL
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        full_endpoint = f"{endpoint}?{query_string}"

        response = self._make_request("GET", full_endpoint)

        if response.status_code == 200:
            data = response.json()
            return data.get("transactions", [])
        else:
            raise Exception(f"PayLabs API error: {response.status_code} - {response.text}")

    def get_transaction_detail(self, transaction_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific transaction

        Args:
            transaction_id: PayLabs transaction ID

        Returns:
            Transaction details dictionary
        """
        endpoint = f"/v1/transactions/{transaction_id}"
        response = self._make_request("GET", endpoint)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"PayLabs API error: {response.status_code} - {response.text}")

    def get_merchant_info(self) -> Dict[str, Any]:
        """
        Get merchant account information

        Returns:
            Merchant info dictionary
        """
        endpoint = "/v1/merchant/info"
        response = self._make_request("GET", endpoint)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"PayLabs API error: {response.status_code} - {response.text}")


# Convenience function for creating client
def create_paylabs_client() -> PayLabsClient:
    """Create a new PayLabs client instance"""
    return PayLabsClient()
