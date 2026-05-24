# Laboratory Work #4
# Topic: Files, classes, serializers, regular expressions, and standard libraries.
# Program version: 1.0
# Developer: Sushkevich A.Y.
# Date of development: 2026-05-05

"""CSV and pickle serializers for task 1."""

from __future__ import annotations

import csv
import pickle
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union

from .models import Candidate, ElectionTable

PathLike = Union[str, Path]


class BaseSerializer(ABC):
    """Abstract serializer interface."""

    @abstractmethod
    def save(self, table: ElectionTable, file_path: PathLike) -> None:
        """Save table to disk."""

    @abstractmethod
    def load(self, file_path: PathLike) -> ElectionTable:
        """Load table from disk."""


class CSVSerializer(BaseSerializer):
    """Serialize election data in CSV format."""

    def save(self, table: ElectionTable, file_path: PathLike) -> None:
        """Save table as CSV."""
        path = Path(file_path)
        with path.open("w", newline="", encoding="utf-8") as file_obj:
            writer = csv.writer(file_obj)
            writer.writerow(["surname", "votes"])
            for candidate in table:
                writer.writerow([candidate.surname, candidate.votes])

    def load(self, file_path: PathLike) -> ElectionTable:
        """Load table from CSV."""
        path = Path(file_path)
        candidates = []
        with path.open("r", newline="", encoding="utf-8") as file_obj:
            reader = csv.DictReader(file_obj)
            for row in reader:
                candidates.append(Candidate(row["surname"], int(row["votes"])))
        return ElectionTable(candidates)


class PickleSerializer(BaseSerializer):
    """Serialize election data in pickle format."""

    def save(self, table: ElectionTable, file_path: PathLike) -> None:
        """Save table as pickle."""
        path = Path(file_path)
        with path.open("wb") as file_obj:
            pickle.dump(table.to_dict(), file_obj, protocol=pickle.HIGHEST_PROTOCOL)

    def load(self, file_path: PathLike) -> ElectionTable:
        """Load table from pickle."""
        path = Path(file_path)
        with path.open("rb") as file_obj:
            data = pickle.load(file_obj)

        if not isinstance(data, dict):
            raise ValueError("Pickle file must contain a dictionary.")

        normalized = {str(key): int(value) for key, value in data.items()}
        return ElectionTable.from_dict(normalized)