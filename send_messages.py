import os
import telegram
import asyncio
import random
import json
from datetime import datetime

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

def get_random_bank_withdrawal():
    banks = [
        "አንበሳ ባንክ", "አቢሲኒያ ባንክ", "ንግድ ባንክ", 
        "አዋሽ ባንክ", "ዳሽን ባንክ"
    ]
    amount = random.choice(range(1600, 3000, 50))
    return f"ባንክ: {random.choice(banks)}, \n   የብር መጠን: {amount} ብር"


def get_random_binance_withdrawal():
    binance_types = {
        "USDT": range(13, 40, 1),
        "TON": range(2, 7, 1),
        "TRX": range(130, 2000, 100)
    }
    
    withdrawal_type = random.choice(list(binance_types.keys()))
    amount = random.choice(binance_types[withdrawal_type])
    
    return f"Binance: {withdrawal_type} \n  የብር መጠን: {amount} {withdrawal_type}"


def get_random_paypal_withdrawal():
    amount = random.choice(range(13, 40, 1))
    return f"PayPal: USDT, \n  የብር መጠን: {amount} USDT"


# Function to get a random withdrawal message
def get_random_withdrawal_message():
    withdrawal_platforms = ["Bank", "Binance", "PayPal"]
    platform = random.choice(withdrawal_platforms)
    
    if platform == "Bank":
        return get_random_bank_withdrawal()
    elif platform == "Binance":
        return get_random_binance_withdrawal()
    else:
        return get_random_paypal_withdrawal()


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
    
    # Get a random withdrawal message
    withdrawal_message = get_random_withdrawal_message()
    
    # Construct the message with the random name and withdrawal message
    full_name = f"{random_name['first_name']} {random_name['last_name']}"
    payment_message = f"ክፍያ ማረጋገጫ (Payment Proof):\n\n  ስም: {full_name}\n\n  {withdrawal_message}\n\n  ቀን: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    try:
        # Send the payment proof image
        await bot.send_photo(chat_id=CHAT_ID, photo=open(PAYMENT_PROOF_IMAGE_PATH, 'rb'))
        
        # Send the payment proof message
        await bot.send_message(chat_id=CHAT_ID, text=payment_message)
        
        print(f"Posted payment proof for {full_name} at {datetime.now()}")
    except Exception as e:
        print(f"Failed to send payment proof: {e}")


# Function to schedule the next post
async def schedule_next_post():
    # Send the payment proof

    # Randomly select the delay between 60 and 65 seconds
    delay = random.randint(30 * 60, 4 * 60 * 60)  # Random delay between 30 minutes and 4 hours    
    print(f"Next post will be scheduled in {delay / 60} minutes.")

    await send_individual_payment_proof()
    await asyncio.sleep(delay)
    await schedule_next_post()

    

# Run the schedule
if __name__ == "__main__":
    print("Bot is running and will post individual proofs randomly...")
    asyncio.run(schedule_next_post())  # Start the scheduling
