"""
ESL Gateway Client

HTTP client for communicating with the ESL web application API.
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@dataclass
class LabelReport:
    """Data reported by a discovered label device."""
    serial_number: str
    status: str = "online"  # "online", "offline", "error", "updating"
    battery_percent: Optional[int] = None
    rssi: Optional[int] = None
    firmware_version: Optional[str] = None
    
    def to_dict(self) -> dict:
        data = {
            "serialNumber": self.serial_number,
            "status": self.status,
        }
        if self.battery_percent is not None:
            data["batteryPercent"] = self.battery_percent
        if self.rssi is not None:
            data["rssi"] = self.rssi
        # firmware_version isn't in the API schema yet
        return data
        return data


@dataclass
class LabelUpdate:
    """An update to push to a label device."""
    label_id: str
    serial_number: str
    product_id: Optional[str]
    product: Optional[dict]
    
    @classmethod
    def from_dict(cls, data: dict) -> "LabelUpdate":
        return cls(
            label_id=data["labelId"],
            serial_number=data["serialNumber"],
            product_id=data.get("productId"),
            product=data.get("product"),
        )


@dataclass
class UpdateResult:
    """Result of pushing an update to a label."""
    label_id: str
    success: bool
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        # API expects labelSerialNumber, not labelId
        data = {"labelSerialNumber": self.label_id, "success": self.success}
        if self.error:
            data["error"] = self.error
        return data


@dataclass
class SyncResponse:
    """Response from the sync endpoint."""
    success: bool
    pending_labels: list = field(default_factory=list)
    labels_to_update: list = field(default_factory=list)
    error: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "SyncResponse":
        # Convert API response to our format
        pending = data.get("pendingLabels", [])
        to_update = data.get("labelsToUpdate", [])
        
        # Combine pending and to_update into unified update list
        updates = []
        for item in to_update:
            updates.append(LabelUpdate(
                label_id=item.get("serialNumber", ""),
                serial_number=item.get("serialNumber", ""),
                product_id=None,
                product=item.get("productData"),
            ))
        
        return cls(
            success=data.get("success", False),
            pending_labels=pending,
            labels_to_update=updates,
            error=data.get("error"),
        )
    
    @property
    def updates(self) -> list:
        """Get all updates that need to be pushed to labels."""
        return self.labels_to_update


@dataclass
class ClaimStatus:
    """Status of the gateway claim."""
    status: str  # "unclaimed", "claimed", "invalid"
    api_key: Optional[str] = None
    gateway_id: Optional[str] = None
    owner_id: Optional[str] = None
    name: Optional[str] = None
    message: Optional[str] = None
    
    @property
    def is_claimed(self) -> bool:
        return self.status == "claimed"
    
    @property
    def is_valid(self) -> bool:
        return self.status != "invalid"
    
    @classmethod
    def from_dict(cls, data: dict) -> "ClaimStatus":
        return cls(
            status=data.get("status", "invalid"),
            api_key=data.get("apiKey"),
            gateway_id=data.get("gatewayId"),
            owner_id=data.get("ownerId"),
            name=data.get("name"),
            message=data.get("message"),
        )


class GatewayUnclaimed(Exception):
    """Raised when the gateway has been unclaimed/deleted."""
    pass


class GatewayClient:
    """HTTP client for the ESL Gateway API."""
    
    def __init__(
        self,
        server_url: str,
        serial_number: str,
        api_key: Optional[str] = None,
        firmware_version: str = "1.0.0",
        config_path: Optional[Path] = None,
    ):
        self.server_url = server_url.rstrip("/")
        self.serial_number = serial_number
        self.api_key = api_key
        self.firmware_version = firmware_version
        self.config_path = config_path
        self.session = requests.Session()
        self.timeout = 30
        
    def _get_headers(self, authenticated: bool = True) -> dict:
        headers = {"Content-Type": "application/json"}
        if authenticated and self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def check_claim_status(self) -> ClaimStatus:
        """Check if this gateway has been claimed."""
        url = f"{self.server_url}/api/gateway/claim"
        params = {"serialNumber": self.serial_number}
        
        logger.info(f"Checking claim status for serial: {self.serial_number}")
        
        response = self.session.get(
            url,
            params=params,
            headers=self._get_headers(authenticated=False),
            timeout=self.timeout,
        )
        response.raise_for_status()
        
        data = response.json()
        status = ClaimStatus.from_dict(data)
        
        if status.is_claimed and status.api_key:
            logger.info(f"Gateway claimed! Name: {status.name}")
            self.api_key = status.api_key
            self._save_api_key()
        elif not status.is_valid:
            logger.error(f"Invalid serial number: {status.message}")
        else:
            logger.info("Gateway not yet claimed")
            
        return status
    
    def sync_labels(
        self,
        labels: list[LabelReport],
        ip_address: Optional[str] = None,
    ) -> SyncResponse:
        """Sync discovered labels with the server."""
        if not self.api_key:
            raise ValueError("Cannot sync without API key. Check claim status first.")
        
        url = f"{self.server_url}/api/gateway/sync"
        
        payload = {
            "firmwareVersion": self.firmware_version,
            "labels": [label.to_dict() for label in labels],
        }
        if ip_address:
            payload["ipAddress"] = ip_address
        
        logger.info(f"Syncing {len(labels)} labels with server")
        
        response = self.session.post(
            url,
            json=payload,
            headers=self._get_headers(),
            timeout=self.timeout,
        )
        
        # Handle 401 - gateway has been unclaimed/deleted
        if response.status_code == 401:
            logger.warning("API key rejected (401). Gateway may have been unclaimed.")
            self._clear_api_key()
            raise GatewayUnclaimed("Gateway has been unclaimed. API key cleared.")
        
        response.raise_for_status()
        
        data = response.json()
        sync_response = SyncResponse.from_dict(data)
        
        if sync_response.success:
            logger.info(
                f"Sync successful. Pending: {len(sync_response.pending_labels)}, "
                f"Updates to push: {len(sync_response.updates)}"
            )
        else:
            logger.error(f"Sync failed: {sync_response.error}")
            
        return sync_response
    
    def acknowledge_updates(self, results: list[UpdateResult]) -> dict:
        """Acknowledge that updates have been pushed to labels."""
        if not self.api_key:
            raise ValueError("Cannot acknowledge without API key.")
        
        url = f"{self.server_url}/api/gateway/sync"
        
        payload = {
            "results": [result.to_dict() for result in results],
        }
        
        logger.info(f"Acknowledging {len(results)} update results")
        
        response = self.session.put(
            url,
            json=payload,
            headers=self._get_headers(),
            timeout=self.timeout,
        )
        
        # Handle 401 - gateway has been unclaimed/deleted
        if response.status_code == 401:
            logger.warning("API key rejected (401). Gateway may have been unclaimed.")
            self._clear_api_key()
            raise GatewayUnclaimed("Gateway has been unclaimed. API key cleared.")
        
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("success"):
            logger.info(
                f"Acknowledgment processed. "
                f"Successful: {data.get('successful', 0)}, "
                f"Failed: {data.get('failed', 0)}"
            )
        
        return data
    
    def _clear_api_key(self) -> None:
        """Clear the API key from memory and config file."""
        self.api_key = None
        
        if not self.config_path:
            return
            
        try:
            if self.config_path.exists():
                config = json.loads(self.config_path.read_text())
                if "api_key" in config:
                    del config["api_key"]
                    self.config_path.write_text(json.dumps(config, indent=2))
                    logger.info(f"API key removed from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to clear API key: {e}")
    
    def _save_api_key(self) -> None:
        """Save the API key to the config file."""
        if not self.config_path or not self.api_key:
            return
            
        try:
            if self.config_path.exists():
                config = json.loads(self.config_path.read_text())
            else:
                config = {}
            
            config["api_key"] = self.api_key
            self.config_path.write_text(json.dumps(config, indent=2))
            logger.info(f"API key saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save API key: {e}")
    
    @classmethod
    def from_config(cls, config_path: Path) -> "GatewayClient":
        config = json.loads(config_path.read_text())
        return cls(
            server_url=config["server_url"],
            serial_number=config["serial_number"],
            api_key=config.get("api_key"),
            firmware_version=config.get("firmware_version", "1.0.0"),
            config_path=config_path,
        )


def load_config(config_path: Optional[Path] = None) -> dict:
    """Load configuration from file."""
    if config_path is None:
        config_path = Path(__file__).parent / "config.json"
    
    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}\n"
            "Copy config.example.json to config.json and edit it."
        )
    
    return json.loads(config_path.read_text())


def get_client(config_path: Optional[Path] = None) -> GatewayClient:
    """Get a configured gateway client."""
    if config_path is None:
        config_path = Path(__file__).parent / "config.json"
    return GatewayClient.from_config(config_path)
