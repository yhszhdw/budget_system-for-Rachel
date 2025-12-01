from datetime import datetime
import pandas as pd
from typing import List, Dict, Any, Optional


class Asset:
    """Represents a single asset in the system."""

    ASSET_TYPES = ["Real Estate", "Vehicle", "Investment", "Other"]

    _COUNTER = 1  # incremental ID counter

    @classmethod
    def _generate_id(cls, asset_type: str) -> str:
        """
        Generate ID like A001R:
        - A + 3-digit counter
        - last letter = asset type initial (upper-case)
        """
        prefix = "A"
        number = f"{cls._COUNTER:03d}"
        type_initial = asset_type[0].upper()  # R, V, I, O

        cls._COUNTER += 1
        return f"{prefix}{number}{type_initial}"

    def __init__(
        self,
        name: str,
        asset_type: str,
        current_value: float,
        owner: str,
        date_acquired: Optional[str] = None
    ):
        # validation
        if asset_type not in Asset.ASSET_TYPES:
            raise ValueError(f"Invalid asset type. Must be one of {Asset.ASSET_TYPES}")

        if current_value < 0:
            raise ValueError("Asset value cannot be negative.")

        # generate ID with type suffix
        self.asset_id = Asset._generate_id(asset_type)

        self.name = name
        self.asset_type = asset_type
        self.owner = owner              # now ANY string is allowed
        self._current_value = current_value

        self.date_acquired = (
            date_acquired if date_acquired else datetime.now().strftime("%Y-%m-%d")
        )
        self.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # property
    @property
    def current_value(self):
        return self._current_value

    @current_value.setter
    def current_value(self, new_value: float):
        if new_value < 0:
            raise ValueError("Asset value cannot be negative.")
        self._current_value = new_value
        self.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # export
    def to_dict(self) -> Dict[str, Any]:
        return {
            "Asset ID": self.asset_id,
            "Name": self.name,
            "Type": self.asset_type,
            "Owner": self.owner,
            "Value": self.current_value,
            "Date Acquired": self.date_acquired,
            "Last Updated": self.last_updated,
        }

    def __str__(self):
        return (f"Asset(ID={self.asset_id}, Name='{self.name}', Type='{self.asset_type}', ")
   

class PropertyRegistry:
    """Store and manage Asset objects."""

    def __init__(self):
        self.assets: List[Asset] = []

    # ----- helpers -----
    def _find_asset(self, asset_id: str) -> Optional[Asset]:
        """Return asset by ID."""
        for asset in self.assets:
            if asset.asset_id == asset_id:
                return asset
        return None

    def _find_index(self, asset_id: str) -> Optional[int]:
        """Return index of asset in list."""
        for i, asset in enumerate(self.assets):
            if asset.asset_id == asset_id:
                return i
        return None

    # ----- core operations -----
    def add_asset(self, asset: Asset) -> None:
        """Add asset to registry."""
        if self._find_asset(asset.asset_id) is not None:
            print(f"Warning: duplicate asset ID {asset.asset_id}.")
        self.assets.append(asset)
        print(f"Asset added: {asset.name} (ID: {asset.asset_id})")

    def delete_asset(self, asset_id: str) -> bool:
        """Delete asset by ID."""
        idx = self._find_index(asset_id)
        if idx is not None:
            asset = self.assets.pop(idx)
            print(f"Asset deleted: {asset.name} (ID: {asset_id})")
            return True
        print(f"Error: asset ID {asset_id} not found.")
        return False

    def update_asset_value(self, asset_id: str, new_value: float) -> bool:
        """Update only the value of an asset."""
        asset = self._find_asset(asset_id)
        if asset is None:
            print(f"Error: asset ID {asset_id} not found.")
            return False

        try:
            asset.current_value = new_value
            print(f"Value updated: {asset_id} → {new_value}")
            return True
        except ValueError as e:
            print(f"Update failed: {e}")
            return False

    # ----- export & filter -----
    def filter_assets(self,asset_type: Optional[str] = None,owner: Optional[str] = None) -> pd.DataFrame:
        """Return filtered assets as DataFrame."""
        rows: List[Dict] = []
        for asset in self.assets:
            match_type = (asset_type is None) or (asset.asset_type == asset_type)
            match_owner = (owner is None) or (asset.owner == owner)
            if match_type and match_owner:
                rows.append(asset.to_dict())
        return self._format_dataframe(rows)

    def to_dataframe(self) -> pd.DataFrame:
        """Return all assets as DataFrame."""
        data = [asset.to_dict() for asset in self.assets]
        return self._format_dataframe(data)

    def _format_dataframe(self, data: List[Dict]) -> pd.DataFrame:
        """Format DataFrame with numeric value + display column."""
        df = pd.DataFrame(data)
        if not df.empty:
            df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
            df["Value_Display"] = df["Value"].map(
                lambda x: f"${x:,.2f}" if pd.notna(x) else ""
            )
        return df

    def __len__(self) -> int:
        return len(self.assets)

    def __iter__(self):
        return iter(self.assets)