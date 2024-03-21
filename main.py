# main.py

import asyncio
import logging
import sys
from bot import dp, bot, main

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    asyncio.run(main())
