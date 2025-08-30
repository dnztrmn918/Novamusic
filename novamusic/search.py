import asyncio
from typing import Tuple

import yt_dlp
from youtubesearchpython.__future__ import VideosSearch


async def search_youtube(query: str) -> Tuple[str, str]:
    search = VideosSearch(query, limit=1)
    results = await search.next()
    if not results["result"]:
        raise RuntimeError("Sonuç bulunamadı")
    first = results["result"][0]
    return first["title"], first["link"]


def _extract_audio(url: str, out_path: str) -> str:
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": out_path,
        "quiet": True,
        "noplaylist": True,
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}
        ],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info).rsplit(".", 1)[0] + ".mp3"


async def download_audio(url: str, out_basename: str = "nova_audio") -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _extract_audio, url, out_basename + ".%(ext)s")