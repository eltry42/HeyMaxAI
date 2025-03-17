import csv
import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.functions.messages import GetRepliesRequest
from telethon.tl.functions.messages import GetHistoryRequest
import google.generativeai as genai
import pandas as pd
import numpy as np
import groq

load_dotenv()

api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")
groq_api_key = os.getenv("GROQ_API_KEY")

groq_client = groq.Client(api_key=groq_api_key)

def generate_summary(conversation_text):
    """Uses Groq AI to generate a summary of the conversation."""
    try:
        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",  # Use the appropriate model name
            messages=[{"role": "user", "content": conversation_text}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating summary: {e}")
        return "Error generating summary."


async def fetch_replies(client, chat, message_id):
    """Fetch replies to a specific message."""
    try:
        replies = await client(GetRepliesRequest(peer=chat, msg_id=message_id, offset_id=0, offset_date=None, add_offset=0, limit=10, max_id=0, min_id=0, hash=0))
        return [reply.message for reply in replies.messages if reply.message]
    except Exception as e:
        print(f"Error fetching replies for {chat}/{message_id}: {e}")
        return []

async def fetch_surrounding_messages(client, chat, message_id, limit=5):
    """Fetch surrounding messages (preceding and following)."""
    try:
        history = await client(GetHistoryRequest(peer=chat, offset_id=message_id, offset_date=None, add_offset=-limit, limit=limit * 2, max_id=0, min_id=0, hash=0))
        return [msg.message for msg in history.messages if msg.message]
    except Exception as e:
        print(f"Error fetching surrounding messages for {chat}/{message_id}: {e}")
        return []

async def process_csv():
    async with TelegramClient("session_name", api_id, api_hash) as client:
        await client.start()
        
        if not os.path.exists("search_results.csv"):
            print("No search_results.csv file found.")
            return
        
        df = pd.read_csv("search_results.csv", encoding="utf-8").head(10)  # Only process first 10 rows
        df = df.replace({np.nan: None})  # Replace NaN with None for safe unpacking
        
        results = []
        
        for _, row in df.iterrows():
            username = row["Username"]
            original_message = row["Message"]
            date = row["Date"]
            link = row["Link"]
            keyword = row["Keyword"]
            image = row["Image"] if "Image" in df.columns else None
            
            try:
                message_id = int(link.split("/")[-1])
            except ValueError:
                print(f"Skipping invalid link format: {link}")
                continue
            
            chat = await client.get_entity(username)
            
            replies = await fetch_replies(client, chat, message_id)
            surrounding_messages = await fetch_surrounding_messages(client, chat, message_id)
            
            conversation = surrounding_messages + [original_message] + replies
            conversation_text = "\n".join(conversation)
            summary = generate_summary(conversation_text)
            
            results.append([username, date, keyword, link, original_message, conversation_text, summary, image])
        
        with open("conversation_summary.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Username", "Date", "Keyword", "Link", "Original Message", "Conversation", "Summary", "Image"])
            writer.writerows(results)
        
        print("Conversation summaries saved to conversation_summary.csv")

if __name__ == "__main__":
    asyncio.run(process_csv())
