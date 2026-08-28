"""Adapter contract for managed data platforms."""

from abc import ABC, abstractmethod

from src.control_plane.models import PlatformHealth


class PlatformAdapter(ABC):
    @abstractmethod
    def collect(self) -> PlatformHealth:
        """Collect and normalize platform health."""
        raise NotImplementedError
