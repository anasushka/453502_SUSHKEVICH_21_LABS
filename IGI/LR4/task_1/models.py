# Laboratory Work #4
# Topic: Files, classes, serializers, regular expressions, and standard libraries.
# Program version: 1.0
# Developer: Sushkevich A.Y.
# Date of development: 2026-05-05

"""Domain models for the election table task."""

from __future__ import annotations

import math
import re
from datetime import datetime
from typing import Any, Dict, Iterable, Iterator, List, Optional


SURNAME_PATTERN = re.compile(r"^[A-Za-zА-Яа-яЁё\- ]+$")


class BaseEntity:
    """Base class with common attributes for lab entities."""

    app_name: str = "Laboratory Work #4"
    app_version: str = "1.0"
    total_voters: int = 2000

    def __init__(self) -> None:
        """Initialize dynamic attributes shared by descendants."""
        self.created_at = datetime.now()

    @classmethod
    def passing_threshold(cls) -> int:
        """Return the minimum number of votes required to pass."""
        return math.ceil(cls.total_voters / 3)


class ValidationMixin:
    """Mixin with reusable validation methods."""

    @staticmethod
    def validate_surname(value: str) -> str:
        """Validate and normalize surname."""
        if not isinstance(value, str):
            raise TypeError("Surname must be a string.")
        normalized = value.strip()
        if not normalized:
            raise ValueError("Surname cannot be empty.")
        if not SURNAME_PATTERN.fullmatch(normalized):
            raise ValueError("Surname can contain only letters, spaces and hyphens.")
        return normalized

    @staticmethod
    def validate_votes(value: int) -> int:
        """Validate vote count."""
        if not isinstance(value, int):
            raise TypeError("Votes must be an integer.")
        if value < 0:
            raise ValueError("Votes cannot be negative.")
        if value > BaseEntity.total_voters:
            raise ValueError(f"Votes cannot exceed {BaseEntity.total_voters}.")
        return value


class Candidate(BaseEntity, ValidationMixin):
    """A single candidate record."""

    def __init__(self, surname: str, votes: int) -> None:
        """Create candidate using super() and validated fields."""
        super().__init__()
        self.surname = self.validate_surname(surname)
        self._votes = 0
        self.votes = votes

    @property
    def votes(self) -> int:
        """Get vote count."""
        return self._votes

    @votes.setter
    def votes(self, value: int) -> None:
        """Set vote count with validation."""
        self._votes = self.validate_votes(value)

    @property
    def passed(self) -> bool:
        """Check whether the candidate passed the threshold."""
        return self.votes >= self.passing_threshold()

    @property
    def status(self) -> str:
        """Return human-readable election status."""
        return "passed" if self.passed else "runoff required"

    def to_dict(self) -> Dict[str, Any]:
        """Convert candidate to a serializable dictionary."""
        return {"surname": self.surname, "votes": self.votes}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Candidate":
        """Create candidate from a dictionary."""
        return cls(str(data["surname"]), int(data["votes"]))

    def __str__(self) -> str:
        """Return readable string representation."""
        return f"{self.surname:20} | votes: {self.votes:4d} | {self.status}"

    def __repr__(self) -> str:
        """Return unambiguous representation."""
        return f"Candidate(surname={self.surname!r}, votes={self.votes!r})"

    def __lt__(self, other: "Candidate") -> bool:
        """Compare candidates by votes."""
        if not isinstance(other, Candidate):
            return NotImplemented
        return self.votes < other.votes


class SearchMixin:
    """Mixin that provides search by surname."""

    @staticmethod
    def _normalize_query(query: str) -> str:
        """Normalize search query."""
        if not isinstance(query, str):
            raise TypeError("Search query must be a string.")
        normalized = query.strip()
        if not normalized:
            raise ValueError("Search query cannot be empty.")
        return normalized.lower()

    def find_by_surname(
        self, candidates: Iterable[Candidate], query: str
    ) -> Optional[Candidate]:
        """Find candidate by surname."""
        normalized = self._normalize_query(query)
        for candidate in candidates:
            if candidate.surname.lower() == normalized:
                return candidate
        return None


class ElectionTable(SearchMixin, BaseEntity):
    """Container for candidates with search and sorting logic."""

    def __init__(self, candidates: Optional[Iterable[Candidate]] = None) -> None:
        """Create election table and optionally preload candidates."""
        super().__init__()
        self.candidates: List[Candidate] = list(candidates or [])

    def __len__(self) -> int:
        """Return number of candidates."""
        return len(self.candidates)

    def __iter__(self) -> Iterator[Candidate]:
        """Iterate over candidates."""
        return iter(self.candidates)

    def __str__(self) -> str:
        """Return pretty text table."""
        lines = [
            "ELECTION TABLE",
            "-" * 55,
            f"{'Surname':20} | {'Votes':>5} | Status",
            "-" * 55,
        ]
        for candidate in self.candidates:
            lines.append(str(candidate))
        lines.append("-" * 55)
        lines.append(
            f"Threshold: {self.passing_threshold()} votes out of {self.total_voters}"
        )
        return "\n".join(lines)

    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> "ElectionTable":
        """Build table from surname -> votes dictionary."""
        return cls(Candidate(surname, votes) for surname, votes in data.items())

    def to_dict(self) -> Dict[str, int]:
        """Convert table to surname -> votes dictionary."""
        return {candidate.surname: candidate.votes for candidate in self.candidates}

    def add_candidate(self, candidate: Candidate) -> None:
        """Add candidate to the table."""
        if not isinstance(candidate, Candidate):
            raise TypeError("Only Candidate objects can be added.")
        self.candidates.append(candidate)

    def sort_by_votes(self, reverse: bool = True) -> List[Candidate]:
        """Return candidates sorted by votes."""
        return sorted(self.candidates, key=lambda item: item.votes, reverse=reverse)

    def passed_candidates(self) -> List[Candidate]:
        """Return all candidates who passed."""
        return [candidate for candidate in self.candidates if candidate.passed]

    def search(self, query: str) -> Optional[Candidate]:
        """Search candidate by surname."""
        return self.find_by_surname(self.candidates, query)

    def result_text(self) -> str:
        """Return the overall election result."""
        passed = self.passed_candidates()
        if passed:
            winners = ", ".join(candidate.surname for candidate in passed)
            return f"Passed: {winners}"
        return "No candidate passed. Runoff election is required."