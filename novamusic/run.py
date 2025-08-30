import asyncio

from .clients import start_clients
from .handlers import register_handlers
from .db import init_db


async def main() -> None:
    await init_db()
    await start_clients()
    register_handlers()
    print("[Nova] Bot ve Asistan başlatıldı. Handlers kaydedildi. Ctrl+C ile durdurabilirsiniz.")
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    asyncio.run(main())

