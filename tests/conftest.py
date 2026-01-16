"""
Test Configuration and Fixtures

Shared pytest fixtures and configuration for all tests.
"""

import pytest
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# TODO: Add fixtures for:
# - Mock Binance WebSocket data
# - Test database instance
# - FastAPI test client
# - Mock C++ engine (for testing without building C++)
# - Sample trade data generators
