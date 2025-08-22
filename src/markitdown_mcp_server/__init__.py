from .server import run
import os
import asyncio


def main() -> None:
    # Cross-platform notification (skip on Windows)
    if os.name != 'nt':  # Not Windows
        os.system("notify-send 'Parseer server started'")
    asyncio.run(run())
