from web3 import Web3
from web3.providers.rpc import HTTPProvider
from web3.middleware import ExtraDataToPOAMiddleware #Necessary for POA chains
from datetime import datetime
import json
import pandas as pd


def connect_to(chain):
    if chain == 'source':  # The source contract chain is avax
        api_url = f"https://api.avax-test.network/ext/bc/C/rpc" #AVAX C-chain testnet

    if chain == 'destination':  # The destination contract chain is bsc
        api_url = f"https://data-seed-prebsc-1-s1.binance.org:8545/" #BSC testnet

    if chain in ['source','destination']:
        w3 = Web3(Web3.HTTPProvider(api_url))
        # inject the poa compatibility middleware to the innermost layer
        w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    return w3


def get_contract_info(chain, contract_info):
    """
        Load the contract_info file into a dictionary
        This function is used by the autograder and will likely be useful to you
    """
    try:
        with open(contract_info, 'r')  as f:
            contracts = json.load(f)
    except Exception as e:
        print( f"Failed to read contract info\nPlease contact your instructor\n{e}" )
        return 0
    return contracts[chain]



def scan_blocks(chain, contract_info="contract_info.json"):
    """
        chain - (string) should be either "source" or "destination"
        Scan the last 5 blocks of the source and destination chains
        Look for 'Deposit' events on the source chain and 'Unwrap' events on the destination chain
        When Deposit events are found on the source chain, call the 'wrap' function the destination chain
        When Unwrap events are found on the destination chain, call the 'withdraw' function on the source chain
    """

    # This is different from Bridge IV where chain was "avax" or "bsc"
    if chain not in ['source','destination']:
        print( f"Invalid chain: {chain}" )
        return 0
    
    # Load contract information
    contracts = get_contract_info(chain, contract_info)
    if contracts == 0:
        return 0
    
    # Also load the warden private key
    with open(contract_info, 'r') as f:
        all_contracts = json.load(f)
    
    warden_pk = all_contracts.get('warden_pk')
    if not warden_pk:
        print("Error: warden_pk not found in contract_info.json")
        return 0
    
    # Connect to the blockchain
    w3 = connect_to(chain)
    
    # Get current block number
    current_block = w3.eth.block_number
    start_block = max(0, current_block - 5)
    
    # Create contract instance
    contract_address = contracts['address']
    contract_abi = contracts['abi']
    contract = w3.eth.contract(address=contract_address, abi=contract_abi)
    
    print(f"Scanning {chain} chain from block {start_block} to {current_block}")
    
    if chain == 'source':
        # Look for Deposit events on source chain
        scan_deposits(w3, contract, start_block, current_block, warden_pk, contract_info)
    
    elif chain == 'destination':
        # Look for Unwrap events on destination chain
        scan_unwraps(w3, contract, start_block, current_block, warden_pk, contract_info)


def scan_deposits(w3_source, source_contract, start_block, end_block, warden_pk, contract_info):
    """
    Scan for Deposit events on source chain and call wrap on destination
    """
    # Create event filter for Deposit events
    try:
        event_filter = source_contract.events.Deposit.create_filter(
            from_block=start_block,
            to_block=end_block
        )
        events = event_filter.get_all_entries()
    except Exception as e:
        print(f"Error scanning for Deposit events: {e}")
        return
    
    if len(events) == 0:
        print("No Deposit events found")
        return
    
    print(f"Found {len(events)} Deposit event(s)")
    
    # For each Deposit event, call wrap on destination
    for event in events:
        token = event.args['token']
        recipient = event.args['recipient']
        amount = event.args['amount']
        
        print(f"Deposit: token={token}, recipient={recipient}, amount={amount}")
        
        # Call wrap on destination
        wrap_on_destination(token, recipient, amount, warden_pk, contract_info)


def scan_unwraps(w3_dest, dest_contract, start_block, end_block, warden_pk, contract_info):
    """
    Scan for Unwrap events on destination chain and call withdraw on source
    """
    # Create event filter for Unwrap events
    try:
        event_filter = dest_contract.events.Unwrap.create_filter(
            from_block=start_block,
            to_block=end_block
        )
        events = event_filter.get_all_entries()
    except Exception as e:
        print(f"Error scanning for Unwrap events: {e}")
        return
    
    if len(events) == 0:
        print("No Unwrap events found")
        return
    
    print(f"Found {len(events)} Unwrap event(s)")
    
    # For each Unwrap event, call withdraw on source
    for event in events:
        underlying_token = event.args['underlying_token']
        recipient = event.args['to']
        amount = event.args['amount']
        
        print(f"Unwrap: token={underlying_token}, recipient={recipient}, amount={amount}")
        
        # Call withdraw on source
        withdraw_on_source(underlying_token, recipient, amount, warden_pk, contract_info)


def wrap_on_destination(token, recipient, amount, warden_pk, contract_info):
    """
    Call wrap function on destination contract
    """
    from eth_account import Account
    
    # Connect to destination chain
    w3_dest = connect_to('destination')
    
    # Load destination contract info
    with open(contract_info, 'r') as f:
        contracts = json.load(f)
    
    dest_info = contracts['destination']
    dest_contract = w3_dest.eth.contract(
        address=dest_info['address'],
        abi=dest_info['abi']
    )
    
    # Create account from private key
    account = Account.from_key(warden_pk)
    
    # Build transaction
    nonce = w3_dest.eth.get_transaction_count(account.address)
    
    txn = dest_contract.functions.wrap(token, recipient, amount).build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gas': 300000,
        'gasPrice': w3_dest.eth.gas_price
    })
    
    # Sign and send transaction
    signed_txn = account.sign_transaction(txn)
    tx_hash = w3_dest.eth.send_raw_transaction(signed_txn.raw_transaction)
    
    print(f"Wrap transaction sent: {tx_hash.hex()}")
    
    # Wait for receipt
    receipt = w3_dest.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    
    if receipt.status == 1:
        print(f"✅ Wrap successful at block {receipt.blockNumber}")
    else:
        print(f"❌ Wrap transaction failed")


def withdraw_on_source(token, recipient, amount, warden_pk, contract_info):
    """
    Call withdraw function on source contract
    """
    from eth_account import Account
    
    # Connect to source chain
    w3_source = connect_to('source')
    
    # Load source contract info
    with open(contract_info, 'r') as f:
        contracts = json.load(f)
    
    source_info = contracts['source']
    source_contract = w3_source.eth.contract(
        address=source_info['address'],
        abi=source_info['abi']
    )
    
    # Create account from private key
    account = Account.from_key(warden_pk)
    
    # Build transaction
    nonce = w3_source.eth.get_transaction_count(account.address)
    
    txn = source_contract.functions.withdraw(token, recipient, amount).build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gas': 300000,
        'gasPrice': w3_source.eth.gas_price
    })
    
    # Sign and send transaction
    signed_txn = account.sign_transaction(txn)
    tx_hash = w3_source.eth.send_raw_transaction(signed_txn.raw_transaction)
    
    print(f"Withdraw transaction sent: {tx_hash.hex()}")
    
    # Wait for receipt
    receipt = w3_source.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    
    if receipt.status == 1:
        print(f"✅ Withdraw successful at block {receipt.blockNumber}")
    else:
        print(f"❌ Withdraw transaction failed")

