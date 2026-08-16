import logging
import sys


def configure_logging(service_name: str, level: int = logging.INFO) -> None:
    """Configure a standard log format for a service entrypoint. Call once, at
    process startup (a service's `main.py`), never from library code.
    """
    logging.basicConfig(
        level=level,
        stream=sys.stdout,
        format=f"%(asctime)s %(levelname)s [{service_name}] %(name)s: %(message)s",
        force=True,
    )
