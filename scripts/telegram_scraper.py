from telethon import TelegramClient
import csv
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')
api_id = os.getenv('TG_API_ID')  # Your API ID
api_hash = os.getenv('TG_API_HASH')  # Your API Hash
phone = os.getenv('TG_PHONE')  # Your phone number

# Function to scrape data from a single channel
async def scrape_channel(client, channel_username, writer):
    entity = await client.get_entity(channel_username)
    channel_title = entity.title  # Extract the channel's title
    async for message in client.iter_messages(entity, limit=10000):  # Limit set to 6000 messages
        # Write the channel title along with other data
        writer.writerow([channel_title, channel_username, message.id, message.message, message.date])
        print(f"Scraped message ID {message.id} from {channel_title}")

# Initialize the client once
client = TelegramClient('scraping_session', api_id, api_hash)

async def main():
    await client.start()

    # Open the CSV file and prepare the writer
    with open('telegram_data.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Channel Title', 'Channel Username', 'ID', 'Message', 'Date'])  # Header for CSV file
        
        # List of channels to scrape
        channels = [
            '@ZemenExpress',
            '@sinayelj',
        ]
        
        # Iterate over channels and scrape data into the CSV file
        for channel in channels:
            await scrape_channel(client, channel, writer)

with client:
    client.loop.run_until_complete(main())


