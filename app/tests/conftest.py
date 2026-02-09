import pytest
from app.tests.mocks import FakeCtx


@pytest.fixture
def fake_ctx() -> FakeCtx:
    return FakeCtx()
