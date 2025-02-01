from telethon import TelegramClient
from telethon.tl.types import Channel
from tqdm import tqdm
import csv
import asyncio
import os
from dotenv import load_dotenv
from insert_db import insert_channel, insert_scraped_message, get_channel_id

load_dotenv()

# Use your own api_id and api_hash -> GET FROM https://my.telegram.org/auth
api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")
chat_usernames_to_check = ["heymax.ai community", "heymaxai"]
clear_data = True

async def run():
    async with TelegramClient("session_name", api_id, api_hash) as client:
        await client.start()

        if clear_data:
            with open("search_results.csv", "w") as file:
                pass

        with open("keywords.txt", "r") as f:
            keywords = [k.strip() for k in f.readlines()]

        processed_messages = set()
        with open("search_results.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Username", "Message", "Date", "Link", "Keyword"])

            for username in tqdm(chat_usernames_to_check, desc="Scanning Selected Chats", unit="chat"):
                try:
                    chat = await client.get_entity(username)
                    insert_channel(username, True)
                    channel_id = get_channel_id(username)  # Fetch the channel_id from the DB
                    
                    if channel_id is None:
                        print(f"Error: Channel '{username}' not found in database.")
                        continue
                    
                    messages = await client.get_messages(chat, limit=1000)

                    for message in messages:
                        if not message.message:
                            continue

                        message_id = (message.id, chat.username)
                        if message_id in processed_messages:
                            continue

                        for keyword in keywords:
                            if keyword in message.message:
                                processed_messages.add(message_id)
                                insert_scraped_message(channel_id, message.message, message.date)
                                writer.writerow([
                                    chat.username,
                                    message.message,
                                    message.date,
                                    f"https://t.me/{chat.username}",
                                    keyword
                                ])
                                break
                except Exception as e:
                    print(f"Error processing chat '{username}': {e}")

        print("Scraping complete. Data saved to database and CSV file.")

asyncio.run(run())