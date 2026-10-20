from hi_contracts.api.envelope import Envelope, ErrorBody, ErrorCode, ErrorEnvelope


def test_envelope_generates_unique_request_ids() -> None:
    a, b = Envelope[int](data=1), Envelope[int](data=2)
    assert a.meta.request_id != b.meta.request_id


def test_error_envelope_shape() -> None:
    err = ErrorEnvelope(error=ErrorBody(code=ErrorCode.OUT_OF_COVERAGE, message="fuera"))
    assert err.model_dump()["error"]["code"] == "OUT_OF_COVERAGE"
