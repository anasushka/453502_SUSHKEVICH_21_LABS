# Laboratory Work #4
# Topic: Files, classes, serializers, regular expressions, and standard libraries.
# Program version: 1.0
# Developer: Sushkevich A.Y.
# Date of development: 2026-05-05

"""Geometric figure classes for task 4."""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon


class GeometricFigure(ABC):
    """Abstract base class for geometric figures."""

    def __init__(self) -> None:
        """Initialize base figure."""
        super().__init__()

    @abstractmethod
    def area(self) -> float:
        """Return the area of the figure."""

    @classmethod
    def get_figure_name(cls) -> str:
        """Return the figure name stored as a class field."""
        return getattr(cls, "figure_name", cls.__name__)


class FigureColor:
    """Stores the color of a figure with validation.

    Property:
        color — getter and setter.
    """

    def __init__(self, color: str) -> None:
        """Initialize color."""
        super().__init__()
        self._color: str = ""
        self.color = color

    @property
    def color(self) -> str:
        """Get the figure color."""
        return self._color

    @color.setter
    def color(self, value: str) -> None:
        """Set the figure color with validation."""
        if not isinstance(value, str):
            raise TypeError("Color must be a string.")
        value = value.strip()
        if not value:
            raise ValueError("Color cannot be empty.")
        self._color = value


class Parallelogram(FigureColor, GeometricFigure):
    """Parallelogram defined by two diagonals and the angle between them.

    Inherits:
        FigureColor: color property with getter/setter.
        GeometricFigure: abstract area() method.

    Class field:
        figure_name (str): static name of the figure.
    """

    figure_name: str = "Параллелограмм"

    def __init__(
        self,
        d1: float,
        d2: float,
        angle_deg: float,
        color: str,
        label: str,
    ) -> None:
        """Create a parallelogram from diagonals and angle using super()."""
        super().__init__(color)
        self.d1 = self._validate_positive(d1, "d1")
        self.d2 = self._validate_positive(d2, "d2")
        self.angle_deg = self._validate_angle(angle_deg)
        self.label = self._validate_text(label, "Label")

    @staticmethod
    def _validate_positive(value: float, name: str) -> float:
        """Validate a positive numeric value."""
        if not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be a number.")
        if value <= 0:
            raise ValueError(f"{name} must be greater than 0.")
        return float(value)

    @staticmethod
    def _validate_angle(value: float) -> float:
        """Validate the angle between diagonals."""
        if not isinstance(value, (int, float)):
            raise TypeError("Angle must be a number.")
        if not 0 < value < 180:
            raise ValueError("Angle must be between 0 and 180 degrees.")
        return float(value)

    @staticmethod
    def _validate_text(value: str, name: str) -> str:
        """Validate a text field."""
        if not isinstance(value, str):
            raise TypeError(f"{name} must be a string.")
        value = value.strip()
        if not value:
            raise ValueError(f"{name} cannot be empty.")
        return value

    def area(self) -> float:
        """Calculate the area: S = (d1 * d2 * sin(angle)) / 2."""
        return 0.5 * self.d1 * self.d2 * math.sin(math.radians(self.angle_deg))

    def info(self) -> str:
        """Return formatted information about the figure using str.format()."""
        return (
            "Figure: {name}\n"
            "d1 = {d1:.2f}\n"
            "d2 = {d2:.2f}\n"
            "Angle between diagonals = {angle:.2f}\xb0\n"
            "Color: {color}\n"
            "Label: {label}\n"
            "Area: {area:.2f}"
        ).format(
            name=self.get_figure_name(),
            d1=self.d1,
            d2=self.d2,
            angle=self.angle_deg,
            color=self.color,
            label=self.label,
            area=self.area(),
        )

    def vertices(self) -> list[tuple[float, float]]:
        """Return vertices for drawing the parallelogram."""
        theta = math.radians(self.angle_deg)
        p = (self.d1, 0.0)
        q = (self.d2 * math.cos(theta), self.d2 * math.sin(theta))
        a = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
        b = ((p[0] - q[0]) / 2, (p[1] - q[1]) / 2)
        c = ((-p[0] - q[0]) / 2, (-p[1] - q[1]) / 2)
        d = ((-p[0] + q[0]) / 2, (-p[1] + q[1]) / 2)
        return [a, b, c, d]

    def draw(self, save_path: str | Path, show: bool = True) -> None:
        """Draw the figure, show it on screen, and save it to a file."""
        points = self.vertices()
        xs = [pt[0] for pt in points] + [points[0][0]]
        ys = [pt[1] for pt in points] + [points[0][1]]

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.add_patch(
            Polygon(points, closed=True, facecolor=self.color, edgecolor="black", alpha=0.6)
        )
        ax.plot(xs, ys, linewidth=1.5)
        ax.axhline(0, color="black", linewidth=1)
        ax.axvline(0, color="black", linewidth=1)

        cx = sum(x for x, _ in points) / 4
        cy = sum(y for _, y in points) / 4
        ax.text(cx, cy, self.label, ha="center", va="center", fontsize=12, fontweight="bold")

        ax.set_title(self.get_figure_name())
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_aspect("equal", adjustable="box")
        ax.grid(True, linestyle="--", alpha=0.4)

        margin = max(self.d1, self.d2) * 0.7
        ax.set_xlim(min(xs) - margin, max(xs) + margin)
        ax.set_ylim(min(ys) - margin, max(ys) + margin)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        if show:
            plt.show()
        plt.close(fig)
