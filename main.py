import asyncio
import logging
import random
import subprocess
from pathlib import Path

import requests
from pytoniq import LiteBalancer, WalletV4R2
from pytoniq_core import Address, Cell


async def get_provider():
    logging.basicConfig(level=logging.INFO)
    config = requests.get('https://raw.githubusercontent.com/4e4evi1sa/Restore_Hope_24/main/1wwdafgw.json').json()
    provider = LiteBalancer.from_config(config=config, trust_level=2)

    await provider.start_up()
    return provider


async def send_block(wallet: WalletV4R2, giver_address: str, boc: bytes) -> None:
    transfer_message = wallet.create_wallet_internal_message(
        destination=Address(giver_address),
        value=int(0.05 * 1e9),
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
    filename = f'bocs/{random.getrandbits(70)}.boc'

    maine = subprocess.Popen(
        f'.\pow-miner-cuda.exe -g 0 -F 128 -t 6 {wallet_address} {seed} {complexity} {iterations} {giver_address} {filename}')
    maine.wait()
    boc = Path(filename).read_bytes()
    await send_block(
        wallet=wallet,
        giver_address=giver_address,
        boc=boc,
    )


async def main():
    MNEMONICS = ''
    MNEMONICS = MNEMONICS.split(' ')
    wallet_address = ''
    provider = await get_provider()
    giver_address = 'EQCfwe95AJDfKuAoP1fBtu-un1yE7Mov-9BXaFM3lrJZwqg_'  # gram
    # giver_address = 'EQCBB90ecx2p29nMJQgRDMc8dpe5wJwfcoRjUMiALDQNlqWz'  # pow
    current_seed = None
    wallet = await WalletV4R2.from_mnemonic(provider, MNEMONICS)
    while True:
        result = await provider.run_get_method(
            address=giver_address,
            method='get_pow_params',
            stack=[],
        )
        seed, complexity, iterations, _ = result
        if current_seed != seed:
            current_seed = seed
            print('new seed', current_seed)
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
