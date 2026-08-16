"""Shared product-domain value types, kept dependency-free so both the write
path (catalog) and read path (repositories, search) can import them without
creating a circular import between those packages."""

from typing import Literal

Gender = Literal["men", "women", "unisex"]
