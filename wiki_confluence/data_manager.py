"""
Data Manager for handling JSON file operations for the Wiki Confluence system.
This module provides utilities for reading and writing data to JSON files.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path


class DataManager:
    """Manages data persistence for the Wiki Confluence system using JSON files."""

    DATA_DIR = Path(__file__).parent / "generated_data"

    @classmethod
    def _get_file_path(cls, table_name: str) -> Path:
        """Get the file path for a given table name."""
        return cls.DATA_DIR / f"{table_name}.json"

    @classmethod
    def load_data(cls, table_name: str) -> Dict[str, Any]:
        """Load data from a JSON file."""
        file_path = cls._get_file_path(table_name)
        if not file_path.exists():
            return {}

        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @classmethod
    def save_data(cls, table_name: str, data: Dict[str, Any]) -> None:
        """Save data to a JSON file."""
        file_path = cls._get_file_path(table_name)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def get_next_id(cls, table_name: str) -> str:
        """Get the next available ID for a table."""
        data = cls.load_data(table_name)
        if not data:
            return "1"

        # Get numeric IDs and find the max
        numeric_ids = []
        for key in data.keys():
            try:
                numeric_ids.append(int(key))
            except ValueError:
                # If key is not numeric, extract numbers from it
                import re
                numbers = re.findall(r'\d+', key)
                if numbers:
                    numeric_ids.append(int(numbers[-1]))

        if numeric_ids:
            return str(max(numeric_ids) + 1)
        return "1"

    @classmethod
    def find_by_field(cls, table_name: str, field: str, value: Any) -> Optional[Dict[str, Any]]:
        """Find a record by a specific field value."""
        data = cls.load_data(table_name)
        for record_id, record in data.items():
            if record.get(field) == value:
                return record
        return None

    @classmethod
    def find_all_by_field(cls, table_name: str, field: str, value: Any) -> List[Dict[str, Any]]:
        """Find all records matching a specific field value."""
        data = cls.load_data(table_name)
        results = []
        for record_id, record in data.items():
            if record.get(field) == value:
                results.append(record)
        return results

    @classmethod
    def filter_records(cls, table_name: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter records by multiple field values."""
        data = cls.load_data(table_name)
        results = []

        for record_id, record in data.items():
            match = True
            for field, value in filters.items():
                if field not in record or record[field] != value:
                    match = False
                    break
            if match:
                results.append(record)

        return results

    @classmethod
    def create_record(cls, table_name: str, record_id: str, record_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record."""
        data = cls.load_data(table_name)

        # Check if ID already exists
        if record_id in data:
            raise ValueError(
                f"Record with ID {record_id} already exists in {table_name}")

        data[record_id] = record_data
        cls.save_data(table_name, data)
        return record_data

    @classmethod
    def update_record(cls, table_name: str, record_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing record."""
        data = cls.load_data(table_name)

        if record_id not in data:
            raise ValueError(
                f"Record with ID {record_id} not found in {table_name}")

        # Merge updates into existing record
        data[record_id].update(updates)
        cls.save_data(table_name, data)
        return data[record_id]

    @classmethod
    def delete_record(cls, table_name: str, record_id: str) -> bool:
        """Delete a record."""
        data = cls.load_data(table_name)

        if record_id not in data:
            raise ValueError(
                f"Record with ID {record_id} not found in {table_name}")

        del data[record_id]
        cls.save_data(table_name, data)
        return True

    @classmethod
    def get_record(cls, table_name: str, record_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific record by ID."""
        data = cls.load_data(table_name)
        return data.get(record_id)

    @classmethod
    def get_all_records(cls, table_name: str) -> Dict[str, Any]:
        """Get all records from a table."""
        return cls.load_data(table_name)

    @staticmethod
    def get_timestamp() -> str:
        """Get current timestamp in ISO format."""
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def find_record_id_by_field(cls, table_name: str, field: str, value: Any) -> Optional[str]:
        """Find a record ID by a specific field value."""
        data = cls.load_data(table_name)
        for record_id, record in data.items():
            if record.get(field) == value:
                return record_id
        return None
