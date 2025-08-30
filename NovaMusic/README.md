# Nova Music (Minimal Telegram Voice Chat Player)

Nova Music, Pyrogram + PyTgCalls ile yazılmış, basit ve stabil bir Telegram sesli sohbet müzik botudur.

## Özellikler
- /play: Yanıtlanan ses/voice dosyasını çalar (asistan ile sesli sohbet)
- /pause, /resume, /stop: Oynatımı kontrol eder
- /queue: Kuyruğu listeler
- /broadcast: SUDO kullanıcıları, yanıtlanan metin/medyayı yayınlar

## Gereksinimler
- Python 3.10+
- ffmpeg yüklü (PATH içine ekli)

## Kurulum
1. Depoyu klonla veya dosyaları indir
2. Bağımlılıkları kur:
```bash
pip install -r requirements.txt
```
3. Ortam değişkenlerini ayarla (veya `.env` dosyası kullan):
- API_ID, API_HASH
- BOT_TOKEN
- STRING_SESSION (asistan hesabı oturumu)
- SUDO_IDS (boşlukla ayrılmış kullanıcı ID listesi)

4. Çalıştır:
```bash
python -m novamusic.run
```

## Heroku Deploy
1) Bu klasörde bir repo oluşturup GitHub'a push edin
2) Heroku Dashboard > Create App > Deploy via GitHub
3) Config Vars içine `.env.example` değişkenlerini girin
4) Dyno type: worker (Procfile hazır)
5) Deploy'u başlatın

## Yapı
```
novamusic/
  __init__.py
  run.py
  clients.py
  voice.py
  handlers.py
requirements.txt
README.md
.env.example
```