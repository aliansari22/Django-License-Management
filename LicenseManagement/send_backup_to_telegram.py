import os
import asyncio
import telegram
from datetime import datetime

# Replace these with your bot's token and chat ID
BOT_TOKEN = ''
CHAT_IDS = {}

# Path to your backup directory
BACKUP_DIR = '.' + os.path.sep + 'backup'

async def send_backup():
    bot = telegram.Bot(token=BOT_TOKEN)
    files = os.listdir(BACKUP_DIR)
    if not files:
        print("No backup files found.")
        return

    # Get the most recent backup file
    files.sort(key=lambda x: os.path.getmtime(os.path.join(BACKUP_DIR, x)))
    latest_backup = os.path.join(BACKUP_DIR, files[-1])

    for username in CHAT_IDS:
        with open(latest_backup, 'rb') as file:
            _ = await bot.send_document(chat_id=CHAT_IDS[username], document=file, filename=f'backup_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.backup')

if __name__ == "__main__":
    asyncio.run(send_backup())
