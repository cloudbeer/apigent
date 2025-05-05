
from datetime import datetime 

class DateTimeString(datetime):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()
        return v