import asyncio
import os

from .clients import start_clients, bot
from .handlers import register_handlers
from .db import init_db


async def main() -> None:
    await init_db()
    await start_clients()
    # Optional raw updates logger
    if os.getenv("DEBUG_LOG", "1") != "0":
        try:
            @bot.on_raw_update()
            async def _raw_update_logger(_, update, __, ___):
                try:
                    print(f"[Nova][RAW] update={type(update).__name__}")
                except Exception:
                    pass
        except Exception:
            pass
    register_handlers()
    print("[Nova] Bot ve Asistan başlatıldı. Handlers kaydedildi. Ctrl+C ile durdurabilirsiniz.")
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    asyncio.run(main())

