from dataclasses import dataclass
from typing import Optional


@dataclass
class ProviderSettings:

    max_message_length: int = 1000

    auto_apply_enabled: bool = True
