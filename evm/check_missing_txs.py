import requests
import json
import asyncio
from aiohttp import ClientSession, ClientTimeout, ClientConnectorError
import time
from datetime import datetime

# RPC URL
RPC_URL = 'http://localhost:8545'
STATE_FILE = 'last_processed_block.txt'  # File to save the last processed block

# Function to get block data with timeout and retry logic
async def get_block_by_number(session, block_number, retries=3):
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBlockByNumber",
        "params": [hex(block_number), True],  # True for fetching all transactions
        "id": 1
    }
    attempt = 0
    while attempt < retries:
        try:
            async with session.post(RPC_URL, json=payload) as response:
                return await response.json()
        except (asyncio.TimeoutError, ClientConnectorError) as e:
            attempt += 1
            print(f"Attempt {attempt} failed while fetching block {block_number}: {e}")
            if attempt == retries:
                return None
            await asyncio.sleep(2)  # Wait before retrying

# Function to get transaction data by tx ID with retry logic
async def get_transaction_by_txid(session, txid, retries=3):
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getTransactionByHash",
        "params": [txid],
        "id": 1
    }
    attempt = 0
    while attempt < retries:
        try:
            async with session.post(RPC_URL, json=payload) as response:
                return await response.json()
        except (asyncio.TimeoutError, ClientConnectorError) as e:
            attempt += 1
            print(f"Attempt {attempt} failed while fetching transaction {txid}: {e}")
            if attempt == retries:
                return None
            await asyncio.sleep(2)  # Wait before retrying

# Function to process a block and return a list of failed transactions
async def process_block(session, block_number):
    block_data = await get_block_by_number(session, block_number)
    failed_transactions = []

    if block_data and 'result' in block_data and block_data['result']:
        transactions = block_data['result']['transactions']
        print(f"Found {len(transactions)} transactions in block {block_number}")

        for tx in transactions:
            txid = tx['hash']
            timestamp = datetime.fromtimestamp(int(block_data['result']['timestamp'], 16)).isoformat()  # Get timestamp from block data

            print(f"Processing tx ID: {txid}")

            # Get transaction data
            tx_data = await get_transaction_by_txid(session, txid)
            if not tx_data or 'result' not in tx_data or not tx_data['result'] or 'hash' not in tx_data['result']:
                print(f"Failed to get valid data for transaction {txid} in block {block_number}")
                failed_transactions.append((block_number, txid, timestamp))
                log_failed_transaction(block_number, txid, timestamp)  # Log failed transaction
            else:
                print(f"Transaction data for {txid} successfully retrieved")
    else:
        print(f"Failed to get data for block {block_number}")

    return failed_transactions

# Function to process a range of blocks and output information about failed transactions
async def process_block_range(start_block, end_block):
    timeout = ClientTimeout(total=15)  # Timeout increased to 15 seconds
    semaphore = asyncio.Semaphore(1000)  # Increased to 1000 concurrent requests

    async with ClientSession(timeout=timeout) as session:
        tasks = []
        for block_number in range(start_block, end_block + 1):
            tasks.append(process_block_with_semaphore(session, block_number, semaphore))

        all_failed_transactions = await asyncio.gather(*tasks)

        # Flatten the list of failed transactions
        all_failed_transactions = [item for sublist in all_failed_transactions for item in sublist]

        # Check and print results
        if all_failed_transactions:
            print("\nFailed to retrieve data for the following transactions:")
            for block, txid, timestamp in all_failed_transactions:
                print(f"Block {block}, tx ID {txid}, timestamp {timestamp}")
        else:
            print("\nAll transactions successfully retrieved")

# Helper function to process block with semaphore
async def process_block_with_semaphore(session, block_number, semaphore):
    async with semaphore:
        return await process_block(session, block_number)

# Function to log a single failed transaction to a CSV file and print to console
def log_failed_transaction(block, txid, timestamp):
    log_message = f"{block},{txid},{timestamp}"  # Format: block_number, txid, timestamp
    with open('tx_ids.csv', 'a') as f:  # Open in append mode
        f.write(log_message + '\n')
    print(f"Failed transaction logged: {log_message}")  # Log to console as well

# Function to read the last processed block from a file
def read_last_processed_block():
    try:
        with open(STATE_FILE, 'r') as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return None

# Function to save the last processed block to a file
def save_last_processed_block(block_number):
    with open(STATE_FILE, 'w') as f:
        f.write(str(block_number))

# Specify the start and end block numbers for processing
start_block = read_last_processed_block() or 2840250  # Read from file or start from default
end_block = 13848616

# Run the block processing
if __name__ == "__main__":
    start_time = time.time()  # Start time measurement
    try:
        asyncio.run(process_block_range(start_block, end_block))
    except Exception as e:
        print(f"Script terminated due to an error: {e}")
    finally:
        end_time = time.time()  # End time measurement
        execution_time = end_time - start_time
        print(f"\nScript executed in {execution_time:.2f} seconds")

        # Save the last processed block
        save_last_processed_block(end_block)
