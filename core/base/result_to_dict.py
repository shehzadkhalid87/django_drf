from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class BaseResult:
    def to_dict(self):
        return {key: val for key, val in self.__dict__.items()}