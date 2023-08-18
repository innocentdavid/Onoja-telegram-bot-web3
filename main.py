# Below is an example of how to subscribe to Ethereum log events
# using Web3.py in Python. I chose to use the uniswap smart contract as
# the example in the code below due to the high volume of activity. As
# the uniswap smart contract emits events about newly created liquidity
# trading pairs these actions are saved to the log. The Python code below
# runs in a loop, listens for newly created liquidity trading pair
# events, and prints the log message to the IDE console.

# Before you get started make sure you have:

# An IDE and Python installed
# A connection point (e.g. Infura)
# Web3.py installed in your Python environment

# Read the comments in the Python code below to understand how to listen for events on the Ethereum blockchain.

# import the following dependencies import json from web3 import Web3
import os
from dotenv import load_dotenv
import json
import asyncio
import humanize
from web3 import Web3
from dexscreener import DexscreenerClient

from telegram.handler import (
    start_bot,
    send_loggers_message,
    send_listeners_message,
    stop_bot,
)

# Load the environment variables from the .env file
load_dotenv()

dex = DexscreenerClient()

# Log check interval in seconds
check_interval = 10

# add your blockchain connection information
infura_url = os.getenv("INFURA_ENDPOINT")
web3 = Web3(Web3.HTTPProvider(infura_url))

# uniswap address and abi
uniswap_router = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
uniswap_factory = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
uniswap_factory_abi = json.load(open("uniswap_factory_abi.json", "r"))

etherscan_abi = json.load(open("etherscan_abi.json", "r"))

contract = web3.eth.contract(address=uniswap_factory, abi=uniswap_factory_abi)


def format_number(num):
    value = float(num)

    if value == 0:
        value == "<i>0</i>"
    elif value < 0.0000001:
        value = "<i>&lt0.0000001</i>"
    elif value < 1000:
        approx = ""
        if len(str(value)) > 10:
            approx = "≈ "
        value = approx + f"{value:.10f}".rstrip("0").rstrip(".")

    elif value >= 1000000000000:  # Billion
        value = f"{value / 1000000000000:.1f}T"
    elif value >= 1000000000:  # Billion
        value = f"{value / 1000000000:.1f}B"
    elif value >= 1000000:  # Million
        value = f"{value / 1000000:.1f}M"
    elif value >= 1000:  # Thousand
        value = f"{value / 1000:.1f}k"

    return value


# define function to handle events and print to the console
def handle_event(event):
    print(
        "Token 0: "
        + str(event["args"]["pair"])
        + "\nToken 1: "
        + event["args"]["token1"]
        + "\nPair: "
        + event["args"]["pair"]
    )

    # token0_address = event["args"]["token0"]
    # token0 = web3.eth.contract(token0_address, abi=etherscan_abi)
    # token0_name = token0.functions.name().call()
    # token0_symbol = token0.functions.symbol().call()

    # token1_address = event["args"]["token1"]
    # token1 = web3.eth.contract(token1_address, abi=etherscan_abi)
    # token1_name = token1.functions.name().call()
    # token1_symbol = token1.functions.symbol().call()

    exc_address = event["args"]["pair"]
    exc = web3.eth.contract(exc_address, abi=etherscan_abi)
    exc_name = exc.functions.name().call()
    exc_symbol = exc.functions.symbol().call()

    # Check if ETH pair
    try:
        pair = dex.get_token_pair("ethereum", exc_address)
    except:
        print("Couldn't fetch pair")
        return

    if pair.liquidity == None or pair.liquidity.usd == 0:
        print("No liquidity")
        return

    price_usd = format_number(pair.price_usd)
    liquidity_usd = format_number(pair.liquidity.usd)
    fdv = format_number(pair.fdv)

    pair.fdv

    message = f"""🚀 <u><b>New Crypto Listing Alert!</b></u> 🚀

📢 <b>Token: {pair.base_token.name} ({pair.base_token.symbol}) / {pair.quote_token.symbol}</b>

💹 <b>Price:</b> ${price_usd}

💰 <b>LIQ/MC</b> ${liquidity_usd} / ${fdv}

🏦 <b>Exchange:</b> {exc_name} ({exc_symbol})

📬 <b>Address:</b>
<code>{pair.base_token.address}</code>

🔍 <a href="{pair.url}">View on Dex Screener</a>

"""
    # 💰 <b>Price:</b> {token0_symbol}
    # 💹 <b>Volume:</b> 500 {token0_symbol}
    # 🌊 <b>Liquidity:</b> $1,000,000

    # print(message)
    send_listeners_message(message)
    # and whatever


# asynchronous defined function to loop
# this loop sets up an event filter and is looking for new entires for the "PairCreated" event
# this loop runs on a poll interval
async def log_loop(event_filter, poll_interval):
    while True:
        for PairCreated in event_filter.get_new_entries():
            handle_event(PairCreated)
        await asyncio.sleep(poll_interval)


# when main is called
# create a filter for the latest block and look for the "PairCreated" event for the uniswap factory contract
# run an async loop
# try to run the log_loop function above every 2 seconds
def main():
    event_filter = contract.events.PairCreated.create_filter(fromBlock="latest")
    # block_filter = web3.eth.filter('latest')
    # tx_filter = web3.eth.filter('pending')
    loop = asyncio.get_event_loop()
    try:
        start_bot()
        send_loggers_message("<code>New-Listings Listener Running!</code>")

        # test
        handle_event(
            {
                "args": {
                    "token0": "0x550C347BC177351F77440262D6039DB2a1c648f7",
                    "token1": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                    "pair": "0x5f3167825479cB5FEd6f8e2F34E239d993Cd830B",
                }
            }
        )

        loop.run_until_complete(asyncio.gather(log_loop(event_filter, check_interval)))
        # log_loop(block_filter, 2),
        # log_loop(tx_filter, 2)))
    except KeyboardInterrupt:
        print("\nStopping")
    finally:
        # close loop to free up system resources
        loop.close()
        send_loggers_message("<code>New-Listings Listener Aborted!</code>")
        stop_bot()


if _name_ == "_main_":
    main()
