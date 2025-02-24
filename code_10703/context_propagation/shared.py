import dataclasses
from contextvars import ContextVar
from typing import Any, Optional, Type

from temporalio.api.common.v1 import Payload
from temporalio.converter import (
    CompositePayloadConverter,
    DefaultPayloadConverter,
    EncodingPayloadConverter,
    DataConverter
)

from context_propagation.codec import EncryptionCodec

import temporalio.converter

HEADER_KEY = "__my_user_id"

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
