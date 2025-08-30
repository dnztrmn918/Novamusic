from typing import Dict, Deque
from collections import deque

from pytgcalls import PyTgCalls

from .clients import assistant


class Player:
    def __init__(self) -> None:
        self.tgcalls = PyTgCalls(assistant)
        self.queues: Dict[int, Deque[str]] = {}

    async def start(self) -> None:
        await self.tgcalls.start()

    def get_queue(self, chat_id: int) -> Deque[str]:
        if chat_id not in self.queues:
            self.queues[chat_id] = deque()
        return self.queues[chat_id]

    async def play(self, chat_id: int, file_path: str) -> None:
        q = self.get_queue(chat_id)
        if not q:
            q.append(file_path)
            await self.tgcalls.play(chat_id, file_path)
        else:
            q.append(file_path)

    async def pause(self, chat_id: int) -> None:
        await self.tgcalls.pause(chat_id)

    async def resume(self, chat_id: int) -> None:
        await self.tgcalls.resume(chat_id)

    async def stop(self, chat_id: int) -> None:
        await self.tgcalls.leave_call(chat_id)
        self.queues.pop(chat_id, None)


player = Player()
