from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from testhumanizer.core.artifacts import GeneratedTestSuite, TargetClass


class TestGenerator(ABC):
    @abstractmethod
    def generate(self, target: TargetClass, output_dir: Path) -> List[GeneratedTestSuite]:
        raise NotImplementedError
