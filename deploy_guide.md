# Deployment Guide for Bridge V

## Error Explanation
The grader is failing because `contract_info.json` has placeholder addresses:
```
'0xYOUR_SOURCE_CONTRACT_ADDRESS_ON_AVAX' is invalid
```

You MUST deploy actual contracts and update the addresses before the grader can work.

## Prerequisites
1. **Testnet funds** from Bridge I assignment:
   - AVAX on Avalanche Fuji testnet
   - BNB on BSC testnet
2. **Private key** with funds on both chains
3. **Web3 provider** or deployment tool (Remix, Hardhat, Foundry)

## Deployment Steps

### Step 1: Deploy Source Contract to Avalanche

**Network:** Avalanche Fuji C-Chain Testnet
**RPC:** https://api.avax-test.network/ext/bc/C/rpc
**Chain ID:** 43113

**Contract:** `Source.sol`
**Constructor Parameter:** Your address (will become admin/warden)

**After deployment:**
- Note the contract address
- Call `registerToken("0xc677c31AD31F73A5290f5ef067F8CEF8d301e45c")`
- Call `registerToken("0x0773b81e0524447784CcE1F3808fed6AaA156eC8")`

### Step 2: Deploy Destination Contract to BSC

**Network:** BSC Testnet
**RPC:** https://data-seed-prebsc-1-s1.binance.org:8545/
**Chain ID:** 97

**Contract:** `Destination.sol`
**Constructor Parameter:** Your address (will become admin/warden/creator)

**After deployment:**
- Note the contract address
- Call `createToken("0xc677c31AD31F73A5290f5ef067F8CEF8d301e45c", "Wrapped Token 1", "WTK1")`
- Call `createToken("0x0773b81e0524447784CcE1F3808fed6AaA156eC8", "Wrapped Token 2", "WTK2")`

### Step 3: Update contract_info.json

Replace placeholders with your actual deployed addresses:

```json
{
    "source": {
        "address": "0xYOUR_ACTUAL_SOURCE_ADDRESS_ON_AVAX_TESTNET",
        ...
    },
    "destination": {
        "address": "0xYOUR_ACTUAL_DESTINATION_ADDRESS_ON_BSC_TESTNET",
        ...
    },
    "warden_pk": "0xYOUR_ACTUAL_PRIVATE_KEY"
}
```

### Step 4: Test the Bridge

After updating `contract_info.json`, commit and push:

```bash
cd /Users/haoyuanma/Desktop/EAS5830-BridgeV
git add contract_info.json
git commit -m "Add deployed contract addresses"
git push origin main
```

## Quick Deployment Options

### Option A: Using Remix IDE (Easiest)
1. Go to https://remix.ethereum.org/
2. Create new files: Source.sol, Destination.sol, BridgeToken.sol
3. Switch to "Deploy & Run Transactions" tab
4. Select "Injected Provider - MetaMask"
5. Switch MetaMask to Avalanche Fuji
6. Deploy Source.sol
7. Switch MetaMask to BSC Testnet
8. Deploy Destination.sol
9. Copy addresses to contract_info.json

### Option B: Using Foundry
```bash
# Deploy to Avalanche
forge create --rpc-url https://api.avax-test.network/ext/bc/C/rpc \
  --private-key YOUR_PRIVATE_KEY \
  --constructor-args YOUR_ADDRESS \
  Source

# Deploy to BSC
forge create --rpc-url https://data-seed-prebsc-1-s1.binance.org:8545/ \
  --private-key YOUR_PRIVATE_KEY \
  --constructor-args YOUR_ADDRESS \
  Destination
```

### Option C: Using Web3.py Script
See `deploy.py` script (if created)

## Important Notes

⚠️ **Security:** Never commit your actual private key to git in production!
   For this assignment, the grader needs it, but be careful.

⚠️ **Gas:** Make sure you have enough testnet tokens for:
   - Contract deployment (both chains)
   - Token registration (2 txns on Avalanche)
   - Token creation (2 txns on BSC)
   - Bridge operations (ongoing)

⚠️ **Verification:** After deployment, verify on block explorers:
   - Avalanche: https://testnet.snowtrace.io/
   - BSC: https://testnet.bscscan.com/

## Troubleshooting

**"Insufficient funds":** Get testnet tokens from faucets
**"Contract creation failed":** Check your Solidity version matches (^0.8.17)
**"Import not found":** Make sure OpenZeppelin contracts are available
