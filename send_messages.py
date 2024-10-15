import os
import telegram
import asyncio
import random
import json
from datetime import datetime

# Your bot token and chat ID
BOT_TOKEN = os.getenv('BOT_TOKEN')  # Replace 'BOT_TOKEN' with the name of your environment variable
CHAT_ID = os.getenv('CHAT_ID')

# Image to attach with every post (replace with the actual path to your image)
PAYMENT_PROOF_IMAGE_PATH = './payment_proof.jpeg'

# Initialize the bot
bot = telegram.Bot(token=BOT_TOKEN)

# Global variable to track used names
used_names = set()

# Load names from data.json
def load_names():
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['names']

def get_random_amount():
    return random.choice(range(8000, 14001, 200))

# Function to get a random Ethiopian name without repetition
def get_random_name(names):
    global used_names
    
    # Get available names (those that haven't been used)
    available_names = [name for name in names if f"{name['first_name']} {name['last_name']}" not in used_names]
    
    # If all names have been used, reset the used names list
    if not available_names:
        print("All names have been used. Resetting the list.")
        used_names.clear()
        available_names = names  # Reset available names to all names
    
    # Randomly select one name
    selected_name = random.choice(available_names)
    used_names.add(f"{selected_name['first_name']} {selected_name['last_name']}")
    
    return selected_name

# Function to send individual payment proof message along with an image
async def send_individual_payment_proof():
    names = load_names()
    random_name = get_random_name(names)
    
    # Generate a random withdrawal amount between 8000 and 14000 in increments of 200
    withdrawal_amount = random.choice(range(8000, 14001, 200))
    
    # Construct the message with the random name and amount
    full_name = f"{random_name['first_name']} {random_name['last_name']}"
    payment_message = f"ክፍያ ማረጋገጫ:\nስም: {full_name}\nወጪ: {withdrawal_amount} ብር\nቀን: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    try:
        # Send the message to the group
        await bot.send_message(chat_id=CHAT_ID, text=payment_message)
        
        # Send the payment proof image
        await bot.send_photo(chat_id=CHAT_ID, photo=open(PAYMENT_PROOF_IMAGE_PATH, 'rb'))
        
        print(f"Posted payment proof for {full_name} at {datetime.now()}")
    except Exception as e:
        print(f"Failed to send payment proof: {e}")

# Function to schedule the next post
async def schedule_next_post():
    # Randomly select the delay between 15 seconds and 60 seconds
    # delay = random.randint(30 * 60, 4 * 60 * 60)  # Random delay between 30 minutes and 4 hours
    delay = random.randint(3, 7)  # Random delay between 30 minutes and 4 hours
    # delay = random.randint(3, 10)  
    print(f"Next post will be scheduled in {delay} minutes.")
    
    # Schedule the next post
    await asyncio.sleep(delay)
    await send_individual_payment_proof()
    await schedule_next_post()  # Schedule the next post again

# Run the schedule
if __name__ == "__main__":
    print("Bot is running and will post individual proofs randomly...")
    asyncio.run(schedule_next_post())  # Start the scheduling

