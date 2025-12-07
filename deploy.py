"""
Deployment script for Bridge V contracts
This script helps deploy Source and Destination contracts to the testnets
"""

from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
import json
import time

# Configuration
AVALANCHE_RPC = "https://api.avax-test.network/ext/bc/C/rpc"
BSC_RPC = "https://data-seed-prebsc-1-s1.binance.org:8545/"

# Read contract ABIs and bytecode (you'll need to compile first)
# For now, this is a template showing the structure

def connect_to_chain(rpc_url):
    """Connect to a blockchain"""
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    return w3

def deploy_source_contract(private_key):
    """
    Deploy Source contract to Avalanche testnet
    
    Steps:
    1. Compile Source.sol using: forge build --via-ir
    2. Get the ABI and bytecode from out/Source.sol/Source.json
    3. Run this function with your private key
    """
    print("Deploying Source contract to Avalanche Fuji testnet...")
    
    w3 = connect_to_chain(AVALANCHE_RPC)
    account = w3.eth.account.from_key(private_key)
    
    print(f"Deploying from address: {account.address}")
    print(f"Balance: {w3.eth.get_balance(account.address) / 10**18} AVAX")
    
    # TODO: Load compiled contract ABI and bytecode
    # contract_abi = json.load(open('out/Source.sol/Source.json'))['abi']
    # contract_bytecode = json.load(open('out/Source.sol/Source.json'))['bytecode']['object']
    
    # contract = w3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
    
    # Build deployment transaction
    # txn = contract.constructor(account.address).build_transaction({
    #     'from': account.address,
    #     'nonce': w3.eth.get_transaction_count(account.address),
    #     'gas': 3000000,
    #     'gasPrice': w3.eth.gas_price
    # })
    
    # Sign and send
    # signed_txn = w3.eth.account.sign_transaction(txn, private_key)
    # tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    
    # print(f"Transaction hash: {tx_hash.hex()}")
    # receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    # contract_address = receipt.contractAddress
    
    # print(f"✅ Source contract deployed at: {contract_address}")
    # print(f"   View on SnowTrace: https://testnet.snowtrace.io/address/{contract_address}")
    
    # return contract_address
    
    print("⚠️  Please compile contracts first and uncomment deployment code")
    return None

def deploy_destination_contract(private_key):
    """
    Deploy Destination contract to BSC testnet
    
    Steps:
    1. Compile Destination.sol and BridgeToken.sol using: forge build --via-ir
    2. Get the ABI and bytecode from out/Destination.sol/Destination.json
    3. Run this function with your private key
    """
    print("\nDeploying Destination contract to BSC testnet...")
    
    w3 = connect_to_chain(BSC_RPC)
    account = w3.eth.account.from_key(private_key)
    
    print(f"Deploying from address: {account.address}")
    print(f"Balance: {w3.eth.get_balance(account.address) / 10**18} BNB")
    
    # TODO: Same as above
    print("⚠️  Please compile contracts first and uncomment deployment code")
    return None

def register_tokens(source_address, private_key):
    """Register tokens on Source contract"""
    print("\nRegistering tokens on Source contract...")
    
    w3 = connect_to_chain(AVALANCHE_RPC)
    account = w3.eth.account.from_key(private_key)
    
    # Load Source contract ABI
    # contract = w3.eth.contract(address=source_address, abi=SOURCE_ABI)
    
    tokens = [
        "0xc677c31AD31F73A5290f5ef067F8CEF8d301e45c",
        "0x0773b81e0524447784CcE1F3808fed6AaA156eC8"
    ]
    
    for token in tokens:
        print(f"  Registering {token}...")
        # txn = contract.functions.registerToken(token).build_transaction({...})
        # ... sign and send
    
    print("⚠️  Please uncomment registration code after deployment")

def create_wrapped_tokens(destination_address, private_key):
    """Create wrapped tokens on Destination contract"""
    print("\nCreating wrapped tokens on Destination contract...")
    
    w3 = connect_to_chain(BSC_RPC)
    account = w3.eth.account.from_key(private_key)
    
    # Load Destination contract ABI
    # contract = w3.eth.contract(address=destination_address, abi=DESTINATION_ABI)
    
    tokens = [
        ("0xc677c31AD31F73A5290f5ef067F8CEF8d301e45c", "Wrapped Token 1", "WTK1"),
        ("0x0773b81e0524447784CcE1F3808fed6AaA156eC8", "Wrapped Token 2", "WTK2")
    ]
    
    for underlying, name, symbol in tokens:
        print(f"  Creating {name} ({symbol}) for {underlying}...")
        # txn = contract.functions.createToken(underlying, name, symbol).build_transaction({...})
        # ... sign and send
    
    print("⚠️  Please uncomment creation code after deployment")

def update_contract_info(source_address, destination_address, private_key):
    """Update contract_info.json with deployed addresses"""
    
    with open('contract_info.json', 'r') as f:
        config = json.load(f)
    
    config['source']['address'] = source_address
    config['destination']['address'] = destination_address
    config['warden_pk'] = private_key
    
    with open('contract_info.json', 'w') as f:
        json.dump(config, f, indent=4)
    
    print("\n✅ contract_info.json updated!")
    print("   Remember to commit and push the changes")

def main():
    """
    Main deployment workflow
    
    BEFORE RUNNING:
    1. Set your private key as environment variable: export PRIVATE_KEY=0x...
    2. Make sure you have testnet funds on both chains
    3. Compile contracts: forge build --via-ir
    """
    
    import os
    private_key = os.environ.get('PRIVATE_KEY', '')
    
    if not private_key:
        print("❌ Please set PRIVATE_KEY environment variable")
        print("   export PRIVATE_KEY=0xyour_private_key")
        return
    
    print("=" * 60)
    print("BRIDGE V DEPLOYMENT SCRIPT")
    print("=" * 60)
    
    # Deploy contracts
    source_address = deploy_source_contract(private_key)
    destination_address = deploy_destination_contract(private_key)
    
    if source_address and destination_address:
        # Register tokens
        register_tokens(source_address, private_key)
        create_wrapped_tokens(destination_address, private_key)
        
        # Update config
        update_contract_info(source_address, destination_address, private_key)
        
        print("\n" + "=" * 60)
        print("✅ DEPLOYMENT COMPLETE!")
        print("=" * 60)
        print(f"Source (Avalanche):      {source_address}")
        print(f"Destination (BSC):       {destination_address}")
        print("\nNext steps:")
        print("1. git add contract_info.json")
        print("2. git commit -m 'Add deployed contract addresses'")
        print("3. git push origin main")
    else:
        print("\n⚠️  Deployment incomplete - see messages above")

if __name__ == "__main__":
    main()
