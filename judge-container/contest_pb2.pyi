from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class UpdateMessage(_message.Message):
    __slots__ = ("submission_id",)
    SUBMISSION_ID_FIELD_NUMBER: _ClassVar[int]
    submission_id: str
    def __init__(self, submission_id: _Optional[str] = ...) -> None: ...

class UpdateResponse(_message.Message):
    __slots__ = ("changed",)
    CHANGED_FIELD_NUMBER: _ClassVar[int]
    changed: bool
    def __init__(self, changed: bool = ...) -> None: ...

class EventData(_message.Message):
    __slots__ = ("contest_id", "participant_id", "caller", "data")
    CONTEST_ID_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_ID_FIELD_NUMBER: _ClassVar[int]
    CALLER_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    contest_id: str
    participant_id: str
    caller: str
    data: str
    def __init__(self, contest_id: _Optional[str] = ..., participant_id: _Optional[str] = ..., caller: _Optional[str] = ..., data: _Optional[str] = ...) -> None: ...
