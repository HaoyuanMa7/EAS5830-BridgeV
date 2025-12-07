# EAS5830 Bridge V - Integration Assignment

## Overview
This is the final integration assignment for the Bridge Project. All smart contracts and Python bridge code are complete and ready for deployment.

## ✅ What's Complete

### Smart Contracts (Ready to Deploy)
✅ **Source.sol** - Deposit contract for Avalanche (from Bridge III)
- `deposit()` - Accepts ERC20 deposits and emits Deposit event
- `withdraw()` - Releases tokens (only WARDEN_ROLE)
- `registerToken()` - Registers approved tokens (only ADMIN_ROLE)

✅ **Destination.sol** - Wrapping contract for BSC (from Bridge II)
- `wrap()` - Mints wrapped tokens (only WARDEN_ROLE)
- `unwrap()` - Burns wrapped tokens and emits Unwrap event
- `createToken()` - Creates new BridgeToken (only CREATOR_ROLE)

✅ **BridgeToken.sol** - ERC20 token with mint/burn capabilities

### Python Bridge Implementation
✅ **bridge.py** - Complete event listener and transaction relayer
- `scan_blocks()` - Scans chains for events
- `wrap_on_destination()` - Mints wrapped tokens on BSC
- `withdraw_on_source()` - Releases tokens on Avalanche

### Configuration Files
✅ **erc20s.csv** - Token addresses for both chains (required by grader)
✅ **contract_info.json** - Template with ABIs (needs your deployed addresses)

## What You Need To Do

### 1. Deploy Contracts

#### Deploy Source Contract to Avalanche Testnet
- Use the Source.sol contract (from Bridge III assignment)
- Deploy to Avalanche Fuji C-Chain testnet
- Make sure to implement the three functions:
  - `deposit()` - accepts ERC20 deposits
  - `withdraw()` - releases tokens (only WARDEN_ROLE)
  - `registerToken()` - registers approved tokens (only ADMIN_ROLE)

#### Deploy Destination Contract to BSC Testnet  
- Use the Destination.sol contract (from Bridge II assignment)
- Deploy to BSC testnet
- Make sure to implement the three functions:
  - `wrap()` - mints wrapped tokens (only WARDEN_ROLE)
  - `unwrap()` - burns wrapped tokens and emits Unwrap event
  - `createToken()` - creates new BridgeToken (only CREATOR_ROLE)

### 2. Update contract_info.json

Replace the placeholder values in `contract_info.json`:

```json
{
    "source": {
        "address": "0xYOUR_ACTUAL_SOURCE_CONTRACT_ADDRESS_ON_AVAX",
        ...
    },
    "destination": {
        "address": "0xYOUR_ACTUAL_DESTINATION_CONTRACT_ADDRESS_ON_BSC",
        ...
    },
    "warden_pk": "0xYOUR_ACTUAL_PRIVATE_KEY"
}
```

### 3. Register Tokens

From `erc20.csv`, register these tokens:

**On Avalanche (Source):**
- Call `registerToken("0xc677c31AD31F73A5290f5ef067F8CEF8d301e45c")`
- Call `registerToken("0x0773b81e0524447784CcE1F3808fed6AaA156eC8")`

**On BSC (Destination):**
- Call `createToken("0xc677c31AD31F73A5290f5ef067F8CEF8d301e45c", "Token Name", "SYMBOL")`
- Call `createToken("0x0773b81e0524447784CcE1F3808fed6AaA156eC8", "Token Name", "SYMBOL")`

### 4. Test the Bridge

The bridge.py script will:
1. Scan the last 5 blocks on the specified chain
2. Look for Deposit events (on source) or Unwrap events (on destination)
3. Automatically call wrap() or withdraw() on the opposite chain

Run it with:
```python
from bridge import scan_blocks

# Scan source chain for deposits
scan_blocks('source')

# Scan destination chain for unwraps
scan_blocks('destination')
```

## How It Works

### Source → Destination (Deposit → Wrap)
1. User calls `deposit(token, recipient, amount)` on Source contract (Avalanche)
2. Deposit event is emitted
3. Bridge scanner detects the Deposit event
4. Bridge calls `wrap(token, recipient, amount)` on Destination contract (BSC)
5. Wrapped tokens are minted to recipient on BSC

### Destination → Source (Unwrap → Withdraw)
1. User calls `unwrap(wrapped_token, recipient, amount)` on Destination contract (BSC)
2. Unwrap event is emitted
3. Bridge scanner detects the Unwrap event
4. Bridge calls `withdraw(token, recipient, amount)` on Source contract (Avalanche)
5. Original tokens are released to recipient on Avalanche

## Important Notes
- Source contract MUST be on Avalanche testnet
- Destination contract MUST be on BSC testnet
- The warden private key must have both WARDEN_ROLE and sufficient gas on both chains
- Make sure to fund your warden address with testnet tokens (AVAX and BNB)
