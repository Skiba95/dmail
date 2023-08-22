import time
import random 
from web3 import Account, Web3
from colorama import Fore, Style
from config import *

ZK_MAIL_ADDRESS = "0x981F198286E40F9979274E0876636E9144B8FB8E"

w3 = Web3(Web3.HTTPProvider(RPC))

# Чтение приватных ключей из файла
private_keys = []

with open('wallets.txt', 'r') as private_keys_file:
    private_keys = private_keys_file.read().splitlines()

def load_wallets() -> list[Account]:
    return [Account.from_key(private_key) for private_key in private_keys]


# Генерация почты получателя (адресс_ММ@gmail.com) и валидных данных для транзакции
def generate_data(address: str) -> str:

    mail = address + "@gmail.com"
    mail = w3.to_hex(text=mail)[2:]
    mail += "0" * (64 - len(mail))
    from_mail = address.lower() + "@dmail.ai"
    data = (
        "0x5b7d7482"
        + "0000000000000000000000000000000000000000000000000000000000000040"
        + "00000000000000000000000000000000000000000000000000000000000000a0"
        + "0000000000000000000000000000000000000000000000000000000000000033"
        + w3.to_hex(text=from_mail)[2:]
        + "00000000000000000000000000"
        + "0000000000000000000000000000000000000000000000000000000000000000"
        + mail
        + "00000000000000000000000000000000"
    )

    return data


# Отправка письма-транзакции
def send_mail(wallet: Account) -> None:

    data = generate_data(wallet.address)
    dict_transaction = {
        "chainId": w3.eth.chain_id,
        "from": wallet.address,
        "to": w3.to_checksum_address(ZK_MAIL_ADDRESS),
        "gasPrice": w3.eth.gas_price,
        "data": data,
        "nonce": w3.eth.get_transaction_count(wallet.address),
    }

    dict_transaction["gas"] = w3.eth.estimate_gas(dict_transaction)
    signed_tx = wallet.sign_transaction(dict_transaction).rawTransaction
    tx_hash = w3.eth.send_raw_transaction(signed_tx)

    print(f"{Fore.GREEN}https://explorer.zksync.io/tx/{tx_hash.hex()}{Style.RESET_ALL}")


# Случайная задержка между кошельками
def sleep() -> None:

    sleep_amount = random.randint(MIN_DELAY, MAX_DELAY)
    print(f"Sleep {sleep_amount} sec")
    time.sleep(sleep_amount)


def main() -> None:
    wallets = load_wallets()

    if RANDOM_WALLETS:
        random.shuffle(wallets)

    for wallet in wallets:

        print('')
        print('')
        print(f"{Fore.BLUE}Send email from: {Style.RESET_ALL}{wallet.address}")
        print('')
        
        num_transactions = random.randint(MIN_TRANSACTIONS, MAX_TRANSACTIONS)
        for _ in range(num_transactions):
            try:
                send_mail(wallet)
            except Exception as e:
                print(f"{Fore.RED}Error sending transaction: {e}{Style.RESET_ALL}")
                break  # Переход к следующему кошельку
                
            if wallet != wallets[-1]:
                sleep()

if __name__ == "__main__":
    main()