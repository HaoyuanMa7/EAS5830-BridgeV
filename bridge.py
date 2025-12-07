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
    try:
        with open(contract_info, 'r') as f:
            contracts = json.load(f)
    except Exception as e:
        print(f"Failed to read contract info: {e}")
        return 0
    
    # Connect to the blockchain
    w3 = connect_to(chain)
    
    # Get contract info for current chain
    current_contract = contracts[chain]
    contract_address = current_contract['address']
    contract_abi = current_contract['abi']
    
    # Get private key for signing transactions
    warden_pk = contracts.get('warden_pk', '')
    if not warden_pk:
        print("Warden private key not found in contract_info.json")
        return 0
    
    # Create contract instance
    contract = w3.eth.contract(address=contract_address, abi=contract_abi)
    
    # Get the last 5 blocks
    end_block = w3.eth.get_block_number()
    start_block = max(0, end_block - 5)
    
    print(f"Scanning blocks {start_block} to {end_block} on {chain} chain")
    
    # Scan for events based on which chain we're on
    if chain == 'source':
        # Look for Deposit events on source chain
        try:
            event_filter = contract.events.Deposit.create_filter(
                fromBlock=start_block,
                toBlock=end_block
            )
            events = event_filter.get_all_entries()
            
            print(f"Found {len(events)} Deposit events on source chain")
            
            # For each Deposit event, call wrap() on destination chain
            for evt in events:
                token = evt.args['token']
                recipient = evt.args['recipient']
                amount = evt.args['amount']
                tx_hash = evt.transactionHash.hex()
                
                print(f"Processing Deposit: token={token}, recipient={recipient}, amount={amount}")
                
                # Call wrap on destination chain
                wrap_on_destination(token, recipient, amount, contracts, warden_pk)
                
        except Exception as e:
            print(f"Error scanning Deposit events: {e}")
    
    elif chain == 'destination':
        # Look for Unwrap events on destination chain
        try:
            event_filter = contract.events.Unwrap.create_filter(
                fromBlock=start_block,
                toBlock=end_block
            )
            events = event_filter.get_all_entries()
            
            print(f"Found {len(events)} Unwrap events on destination chain")
            
            # For each Unwrap event, call withdraw() on source chain
            for evt in events:
                underlying_token = evt.args['underlying_token']
                recipient = evt.args['to']
                amount = evt.args['amount']
                tx_hash = evt.transactionHash.hex()
                
                print(f"Processing Unwrap: underlying_token={underlying_token}, recipient={recipient}, amount={amount}")
                
                # Call withdraw on source chain
                withdraw_on_source(underlying_token, recipient, amount, contracts, warden_pk)
                
        except Exception as e:
            print(f"Error scanning Unwrap events: {e}")


def wrap_on_destination(underlying_token, recipient, amount, contracts, warden_pk):
    """
    Call the wrap function on the destination contract
    """
    try:
        # Connect to destination chain
        w3_dest = connect_to('destination')
        
        # Get destination contract info
        dest_contract_info = contracts['destination']
        dest_address = dest_contract_info['address']
        dest_abi = dest_contract_info['abi']
        
        # Create contract instance
        contract = w3_dest.eth.contract(address=dest_address, abi=dest_abi)
        
        # Get account from private key
        account = w3_dest.eth.account.from_key(warden_pk)
        
        # Build transaction
        nonce = w3_dest.eth.get_transaction_count(account.address)
        
        txn = contract.functions.wrap(
            underlying_token,
            recipient,
            amount
        ).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': 200000,
            'gasPrice': w3_dest.eth.gas_price
        })
        
        # Sign and send transaction
        signed_txn = w3_dest.eth.account.sign_transaction(txn, warden_pk)
        tx_hash = w3_dest.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        print(f"Wrap transaction sent: {tx_hash.hex()}")
        
        # Wait for transaction receipt
        receipt = w3_dest.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Wrap transaction confirmed in block {receipt.blockNumber}")
        
    except Exception as e:
        print(f"Error calling wrap on destination: {e}")


def withdraw_on_source(token, recipient, amount, contracts, warden_pk):
    """
    Call the withdraw function on the source contract
    """
    try:
        # Connect to source chain
        w3_source = connect_to('source')
        
        # Get source contract info
        source_contract_info = contracts['source']
        source_address = source_contract_info['address']
        source_abi = source_contract_info['abi']
        
        # Create contract instance
        contract = w3_source.eth.contract(address=source_address, abi=source_abi)
        
        # Get account from private key
        account = w3_source.eth.account.from_key(warden_pk)
        
        # Build transaction
        nonce = w3_source.eth.get_transaction_count(account.address)
        
        txn = contract.functions.withdraw(
            token,
            recipient,
            amount
        ).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': 200000,
            'gasPrice': w3_source.eth.gas_price
        })
        
        # Sign and send transaction
        signed_txn = w3_source.eth.account.sign_transaction(txn, warden_pk)
        tx_hash = w3_source.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        print(f"Withdraw transaction sent: {tx_hash.hex()}")
        
        # Wait for transaction receipt
        receipt = w3_source.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Withdraw transaction confirmed in block {receipt.blockNumber}")
        
    except Exception as e:
        print(f"Error calling withdraw on source: {e}")
