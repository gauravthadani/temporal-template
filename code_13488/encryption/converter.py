import dataclasses
from typing import Any, Optional, Type

import temporalio.converter
from temporalio.api.common.v1 import Payload
from temporalio.exceptions import FailureError, ApplicationError

from temporalio.converter import (
    CompositePayloadConverter,
    DefaultPayloadConverter,
    EncodingPayloadConverter,
)


class CustomEncodingPayloadConverter(EncodingPayloadConverter):
    @property
    def encoding(self) -> str:
        return "unauthorized"

    def to_payload(self, value: Any) -> Optional[Payload]:
        pass

    def from_payload(self, payload: Payload, type_hint: Optional[Type] = None) -> Any:
        print("In from_payload", payload)
        raise ApplicationError(payload.metadata.get("message"))


class CustomPayloadConverter(CompositePayloadConverter):
    def __init__(self) -> None:
        # Just add ours as first before the defaults
        super().__init__(
            CustomEncodingPayloadConverter(),
            *DefaultPayloadConverter.default_encoding_payload_converters
        )
