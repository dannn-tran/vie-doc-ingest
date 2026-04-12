from dataclasses import dataclass


@dataclass
class Validated[E, A]:
    is_valid: bool
    error: E
    value: A
