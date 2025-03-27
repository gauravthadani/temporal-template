import dataclasses
from contextvars import ContextVar
from datetime import datetime
from typing import Any, Optional, Type
from typing import Optional, Dict

import temporalio.converter
from context_propagation.codec import EncryptionCodec
from pydantic import BaseModel, PositiveInt
from pydantic import BaseModel, PositiveInt
from temporalio.api.common.v1 import Payload
from temporalio.converter import (
    CompositePayloadConverter,
    DefaultPayloadConverter,
    EncodingPayloadConverter,
    DataConverter
)

HEADER_KEY = "__my_user_id"


class User(BaseModel):
    id: int  # Required integer field
    name: str = "John Doe"  # Default value for name
    signup_ts: Optional[datetime] = None  # Optional datetime field
    tastes: Dict[str, PositiveInt]


external_data = {
    "id": 123,
    "signup_ts": "2019-06-01 12:22",
    "tastes": {
        "wine": 9,
        "cheese": 7,
        "cabbage": "1",  # Will be converted to an integer
    },
}

user = User(**external_data)

user_id: ContextVar[Optional[str]] = ContextVar("user_id", default=None)

# class GreetingEncodingPayloadConverter(EncodingPayloadConverter):
#     @property
#     def encoding(self) -> str:
#         return "text/my-greeting-encoding"
#
#     def to_payload(self, value: Any) -> Optional[Payload]:
#             return Payload(
#                 metadata={"encoding": self.encoding.encode(), "is_input": b"true"},
#                 data=value.encode(),)
#
#     def from_payload(self, payload: Payload, type_hint: Optional[Type] = None) -> Any:
#             return payload.data.decode()
#
# class GreetingPayloadConverter(CompositePayloadConverter):
#     def __init__(self) -> None:
#         # Just add ours as first before the defaults
#         super().__init__(
#             GreetingEncodingPayloadConverter(),
#             *DefaultPayloadConverter.default_encoding_payload_converters
#         )
#
# greeting_data_converter = dataclasses.replace(
#     temporalio.converter.default(),
#     payload_converter_class=GreetingPayloadConverter,
# )

# encryption_data_converter = dataclasses.replace(
#     temporalio.converter.default(),
#     payload_codec=EncryptionCodec(),
#     failure_converter=temporalio.converter.DefaultFailureConverterWithEncodedAttributes(),
# )

encryption_data_converter = DataConverter(
    failure_converter_class=temporalio.converter.DefaultFailureConverterWithEncodedAttributes,
    payload_codec=EncryptionCodec(),
)
