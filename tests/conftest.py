import os


def pytest_configure(config):
    os.environ["KIVY_UNITTEST_SCREENSHOTS"] = "1"
    os.environ["UNITTEST_INTERACTIVE"] = "0"
