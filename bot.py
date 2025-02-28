import requests
import json
import random
import time
import threading
import sys

# Load API keys
api_keys = []
with open('account.txt', 'r') as file:
    api_keys = [line.strip() for line in file.readlines() if line.strip()]

# Track exhausted API keys
exhausted_keys = set()

# Set fixed API URL
API_URL = "https://maplesyrup.gaia.domains/v1/chat/completions"

# Load messages
with open('message.txt', 'r') as file:
    user_messages = [msg.strip() for msg in file.readlines()]

def send_request(message):
    global api_keys, exhausted_keys
    
    for api_key in api_keys:
        if api_key in exhausted_keys:
            continue  # Skip exhausted keys
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        data = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message}
            ]
        }
        
        try:
            response = requests.post(API_URL, headers=headers, data=json.dumps(data))
            raw_response = response.text  # Simpan response mentah
            
            if response.status_code == 402 and "You don't have enough credits" in raw_response:
                print(f"Error: Not enough credits for API key: {api_key}. Marking as exhausted...")
                exhausted_keys.add(api_key)
                continue
            elif response.status_code == 429:
                print(f"Rate limit exceeded for API key: {api_key}. Retrying with next key in 2 seconds...")
                time.sleep(2)
                continue
            elif response.status_code == 200:
                try:
                    response_json = response.json()
                    print(f"Response for message: '{message}'")
                    print(response_json)
                    return
                except json.JSONDecodeError:
                    print("Error: Received invalid JSON. Retrying in 5 seconds...")
                    time.sleep(5)
            else:
                print(f"Error: {response.status_code}, {raw_response}. Retrying in 5 seconds...")
                time.sleep(5)
        except requests.exceptions.RequestException as e:
            print(f"Request failed with error: {e}. Retrying in 5 seconds...")
            time.sleep(5)
    
    print("All API keys exhausted. Please refill your credits or add more keys.")
    exit()

def start_thread():
    while True:
        if len(exhausted_keys) >= len(api_keys):
            print("No working API keys left. Stopping threads.")
            exit()
        random_message = random.choice(user_messages)
        send_request(random_message)

# Get thread count from command-line argument
try:
    num_threads = int(sys.argv[1]) if len(sys.argv) > 1 else 5  # Default 5 thread
    if num_threads < 1:
        print("Please enter a number greater than 0.")
        exit()
except ValueError:
    print("Invalid input. Please enter an integer.")
    exit()

threads = []
for _ in range(num_threads):
    thread = threading.Thread(target=start_thread)
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

print("All requests have been processed.")
