import os
import telegram
import asyncio
import random
import json
from datetime import datetime
from threading import Thread
import http.server
import socketserver
import httpx

# Setup the bot
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

PAYMENT_PROOF_IMAGE_PATH = './payment_proof.png'

# Initialize bot with httpx to bypass SSL verification
bot = telegram.Bot(token=BOT_TOKEN)

# Track used names to avoid duplicates
used_names = set()

# Load names from the JSON file
def load_names():
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['names']

# Generate a random bank withdrawal message
def get_random_bank_withdrawal():
    banks = ["አንበሳ ባንክ", "አቢሲኒያ ባንክ", "ንግድ ባንክ", "አዋሽ ባንክ", "ዳሽን ባንክ"]
    amount = random.choice(range(1600, 3000, 50))
    return f"ባንክ: {random.choice(banks)}, \n   የብር መጠን: {amount} ብር"

# Generate a random Binance withdrawal message
def get_random_binance_withdrawal():
    binance_types = {"USDT": range(13, 40, 1), "TON": range(2, 7, 1), "TRX": range(130, 2000, 100)}
    withdrawal_type = random.choice(list(binance_types.keys()))
    amount = random.choice(binance_types[withdrawal_type])
    return f"Binance: {withdrawal_type} \n  የብር መጠን: {amount} {withdrawal_type}"

# Generate a random PayPal withdrawal message
def get_random_paypal_withdrawal():
    amount = random.choice(range(13, 40, 1))
    return f"PayPal: USDT, \n  የብር መጠን: {amount} USDT"

# Randomly pick a withdrawal platform
def get_random_withdrawal_message():
    withdrawal_platforms = ["Bank", "Binance", "PayPal"]
    platform = random.choice(withdrawal_platforms)
    if platform == "Bank":
        return get_random_bank_withdrawal()
    elif platform == "Binance":
        return get_random_binance_withdrawal()
    else:
        return get_random_paypal_withdrawal()

# Get a random name from the list of names and ensure it's not reused
def get_random_name(names):
    global used_names
    available_names = [name for name in names if f"{name['first_name']} {name['last_name']}" not in used_names]
    if not available_names:
        print("All names have been used. Resetting the list.")
        used_names.clear()
        available_names = names
    selected_name = random.choice(available_names)
    used_names.add(f"{selected_name['first_name']} {selected_name['last_name']}")
    return selected_name

# Send an individual payment proof message
async def send_individual_payment_proof():
    names = load_names()
    random_name = get_random_name(names)
    withdrawal_message = get_random_withdrawal_message()
    full_name = f"{random_name['first_name']} {random_name['last_name']}"
    payment_message = f"ክፍያ ማረጋገጫ (Payment Proof):\n\n  ስም: {full_name}\n\n  {withdrawal_message}\n\n  ቀን: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n We couldnt post receipt for privacy concerns."
    
    try:
        # Use httpx to bypass SSL verification for this session
        async with httpx.AsyncClient(verify=False) as client:
            # Send payment proof photo
            with open(PAYMENT_PROOF_IMAGE_PATH, 'rb') as photo:
                await bot.send_photo(chat_id=CHAT_ID, photo=photo)
            # Send payment proof message
            await bot.send_message(chat_id=CHAT_ID, text=payment_message)
            print(f"Posted payment proof for {full_name} at {datetime.now()}")
    except Exception as e:
        print(f"Failed to send payment proof: {e}")

# Schedule the next post at a random interval between 30 minutes and 4 hours
async def schedule_next_post():
    await send_individual_payment_proof()

    delay = random.randint(180, 1 * 60 * 60)
    print(f"Next post will be scheduled in {delay / 60} minutes.")
    
    await asyncio.sleep(delay)
    await schedule_next_post()

# Run the bot logic
def run_bot():
    asyncio.run(schedule_next_post())

# Simple HTTP server to bind to a port (for Render or other hosting)
def run_http_server():
    PORT = int(os.environ.get("PORT", 5000))  # Render assigns the port as an environment variable
    Handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving on port {PORT}")
        httpd.serve_forever()

# Start the HTTP server in a separate thread
if __name__ == "__main__":
    # Start the simple HTTP server
    server_thread = Thread(target=run_http_server)
    server_thread.start()
    
    # Start the bot logic
    run_bot()
