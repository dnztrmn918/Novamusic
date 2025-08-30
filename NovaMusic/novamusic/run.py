import asyncio

from .clients import start_clients
from .handlers import register_handlers


async def main() -> None:
    await start_clients()
    register_handlers()
    print("[Nova] Bot ve Asistan başlatıldı. Ctrl+C ile durdurabilirsiniz.")
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    asyncio.run(main())

