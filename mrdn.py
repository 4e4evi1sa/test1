import asyncio
import random
import subprocess
import time
from pathlib import Path

import requests
from pytoniq import LiteBalancer, WalletV4R2
from pytoniq_core import Address, Cell


import logging

logging.basicConfig(level=logging.ERROR)
async def get_provider():
    logging.basicConfig(level=logging.INFO)
    config = requests.get('https://raw.githubusercontent.com/4e4evi1sa/Restore_Hope_24/main/1wwdafgw.json').json()
    provider = LiteBalancer.from_config(config=config, trust_level=2)

    await provider.start_up()
    return provider


async def send_block(wallet: WalletV4R2, giver_address: str, boc: bytes) -> None:
    transfer_message = wallet.create_wallet_internal_message(
        destination=Address(giver_address),
        # value=int(0.05 * 1e9),
        value=int(0.08 * 1e9),
        body=Cell.from_boc(boc)[0].to_slice().load_ref(),
    )
    await wallet.raw_transfer(msgs=[transfer_message])
    print('send_block')


async def start_mainer(
        wallet: str,
        wallet_address: str,
        giver_address: str,
        seed: str,
        complexity: str,
        iterations: str,
):
    start_time = time.time()

    filename = f'bocs/{random.getrandbits(70)}.boc'
    maine = subprocess.Popen(
        f'.\pow-miner-cuda.exe -g 0 -F 128 -t 10 {wallet_address} {seed} {complexity} {iterations} {giver_address} {filename}')
    maine.wait()
    try:
        boc = Path(filename).read_bytes()
        print("--- %s seconds ---" % (time.time() - start_time))
        await send_block(
            wallet=wallet,
            giver_address=giver_address,
            boc=boc,
        )
    except FileNotFoundError:
        print('not mined')

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--giver', help='гивер')

args = parser.parse_args()

async def main():

    MNEMONICS = ''
    MNEMONICS = MNEMONICS.split(' ')
    wallet_address = ''

    provider = await get_provider()

    # giver_address = 'EQCfwe95AJDfKuAoP1fBtu-un1yE7Mov-9BXaFM3lrJZwqg_'  # gram
    # giver_address = 'EQCBB90ecx2p29nMJQgRDMc8dpe5wJwfcoRjUMiALDQNlqWz'  # pow
    giver_address = 'EQC0wy0bM9EkLAJAKOzfVWlMuxJcuqDhUQKNii8b1mI-rskf'  # mrdn 100
    giver_address = 'EQCUoxbuxROf2GKmLJPvRjvd9JYTwXv5-yXA62FMN6X-KGsK'  # mrdn 1000
    # giver_address = args.giver
    print('Giver:', giver_address)
    current_seed = None
    wallet = await WalletV4R2.from_mnemonic(provider, MNEMONICS)
    count = 1
    while True:
        result = await provider.run_get_method(
            address=giver_address,
            method='get_mining_status',
            # method='get_pow_params',
            stack=[],
        )
        complexity, iterations, seed, *_ = result
        if current_seed != seed:
            count += 1
            current_seed = seed
            print('new seed', current_seed)
            if count > 1:
                await start_mainer(
                    wallet=wallet,
                    wallet_address=wallet_address,
                    giver_address=giver_address,
                    seed=seed,
                    complexity=complexity,
                    iterations=iterations,
                )
        else:
            pass

    await client.close_all()


if __name__ == '__main__':
    asyncio.run(main())
