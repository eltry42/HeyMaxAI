import csv
import asyncio
import os
from dotenv import load_dotenv
from telethon import TelegramClient
from insert_db import insert_channel, insert_scraped_message, get_channel_id
from tqdm import tqdm
from telethon.tl.types import MessageMediaPhoto

load_dotenv()

# Use your own api_id and api_hash -> GET FROM https://my.telegram.org/auth
api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")
chat_usernames_to_check = ["milelion", "heymaxai", "heymax.ai community"]
# clear_data = True
message_amount = 10000

async def run():
    async with TelegramClient("session_name", api_id, api_hash) as client:
        await client.start()

        with open("keywords.txt", "r") as f:
            keywords = [k.strip() for k in f.readlines()]

        processed_message_contents = set()  # Set to track processed message content
        existing_messages = set()  # Set to track already existing messages in the CSV

        # Read existing messages from search_results.csv to avoid duplicates
        if os.path.exists("search_results.csv"):
            with open("search_results.csv", "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    if row:
                        existing_messages.add(row[3])  # Add message link (unique identifier)

        with open("search_results.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Username", "Message", "Date", "Link", "Keyword", "Image"])

            for username in tqdm(chat_usernames_to_check, desc="Scanning Selected Chats", unit="chat"):
                try:
                    chat = await client.get_entity(username)
                    insert_channel(username, True)
                    channel_id = get_channel_id(username)  # Fetch the channel_id from the DB
                    
                    if channel_id is None:
                        print(f"Error: Channel '{username}' not found in database.")
                        continue
                    
                    messages = await client.get_messages(chat, limit=message_amount)

                    for message in messages:
                        if not message.message:
                            continue

                        # Check if the message contains any of the keywords
                        if not any(keyword in message.message.lower() for keyword in keywords):
                            continue
                        
                        if username == "heymax.ai community" :
                            message_link = f"https://t.me/+gNZRwXXy9Gc1MzJl/{message.id}"
                        else:
                            message_link = f"https://t.me/{username}/{message.id}"

                        # Skip already processed messages
                        if message_link in existing_messages:
                            continue  # Skip this message

                        # Process and store the message and associated image if available
                        image_path = None
                        if message.media and isinstance(message.media, MessageMediaPhoto):
                            image_path = await client.download_media(message.media, file=f"images/{message.id}.jpg")


                        keywordFound = next((keyword for keyword in keywords if keyword in message.message.lower()), None)

                        writer.writerow([
                            username,
                            message.message,
                            message.date.strftime("%Y-%m-%d %H:%M:%S"),
                            message_link,
                            keywordFound,
                            image_path  # Store the image path or URL
                        ])

                        # Insert the message into the database
                        insert_scraped_message(
                            channel_id,
                            message.message,
                            message.date,
                            keywordFound,
                            media_url=image_path
                        )

                        # Mark this message content as processed and add to the existing set
                        processed_message_contents.add(message.message.lower())
                        existing_messages.add(message_link)

                except Exception as e:
                    print(f"Error processing chat '{username}': {e}")

        print("Scraping complete. Data saved to database and CSV file.")

if __name__ == "__main__":
    asyncio.run(run())
