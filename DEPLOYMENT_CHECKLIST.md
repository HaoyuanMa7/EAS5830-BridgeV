# QUICK DEPLOYMENT CHECKLIST

## ⚠️ CRITICAL: You MUST complete these steps before the grader will work!

The grader is currently failing because contract_info.json has placeholder addresses.
You need to deploy actual contracts and update the file.

## 🔧 What to Update in contract_info.json

Open `contract_info.json` and replace these THREE values:

### Line 3:
```json
"address": "0xYOUR_SOURCE_CONTRACT_ADDRESS_ON_AVAX",
```
Replace with: Your actual Source contract address from Avalanche Fuji testnet

### Around line 90 (in "destination" section):
```json
"address": "0xYOUR_DESTINATION_CONTRACT_ADDRESS_ON_BSC",
```
Replace with: Your actual Destination contract address from BSC testnet

### Last line:
```json
"warden_pk": "0xYOUR_PRIVATE_KEY_HERE"
```
Replace with: Your actual private key (the one that deployed the contracts)

## 📍 Deployment Requirements

### Avalanche Fuji Testnet (Source)
- Contract: Source.sol
- Constructor param: Your wallet address
- After deploy: Call registerToken() twice (for both tokens in erc20s.csv)
- Get testnet AVAX: https://faucet.avax.network/

### BSC Testnet (Destination)
- Contract: Destination.sol (also needs BridgeToken.sol)
- Constructor param: Your wallet address  
- After deploy: Call createToken() twice (for both tokens in erc20s.csv)
- Get testnet BNB: https://testnet.bnbchain.org/faucet-smart

## 🚀 Quick Deployment Using Remix (Recommended)

### For Source on Avalanche:
1. Open https://remix.ethereum.org/
2. Create Source.sol, paste code from your repo
3. Compile (Solidity 0.8.17)
4. Deploy tab → Injected Provider
5. MetaMask → Avalanche Fuji C-Chain
6. Deploy with your address as constructor param
7. Copy contract address → Update contract_info.json line 3
8. Call registerToken("0xc677c31AD31F73A5290f5ef067F8CEF8d301e45c")
9. Call registerToken("0x0773b81e0524447784CcE1F3808fed6AaA156eC8")

### For Destination on BSC:
1. In Remix, create Destination.sol and BridgeToken.sol
2. Compile both
3. MetaMask → BSC Testnet
4. Deploy Destination with your address as constructor param
5. Copy contract address → Update contract_info.json (~line 90)
6. Call createToken("0xc677c31AD31F73A5290f5ef067F8CEF8d301e45c", "Token1", "TK1")
7. Call createToken("0x0773b81e0524447784CcE1F3808fed6AaA156eC8", "Token2", "TK2")

### Update Private Key:
Replace the warden_pk with your private key (export from MetaMask)
⚠️ WARNING: In production, NEVER commit private keys! This is only for the grader.

## ✅ After Updating contract_info.json

```bash
cd /Users/haoyuanma/Desktop/EAS5830-BridgeV
git add contract_info.json
git commit -m "Add deployed contract addresses and private key"
git push origin main
```

Then re-run the grader - it should work!

## 📊 Network Details

### Avalanche Fuji C-Chain
- RPC: https://api.avax-test.network/ext/bc/C/rpc
- Chain ID: 43113
- Explorer: https://testnet.snowtrace.io/
- Faucet: https://faucet.avax.network/

### BSC Testnet
- RPC: https://data-seed-prebsc-1-s1.binance.org:8545/
- Chain ID: 97
- Explorer: https://testnet.bscscan.com/
- Faucet: https://testnet.bnbchain.org/faucet-smart

## 🎯 Files Status

✅ Source.sol - Ready to deploy
✅ Destination.sol - Ready to deploy
✅ BridgeToken.sol - Ready to deploy
✅ bridge.py - Complete
✅ erc20s.csv - Complete
❌ contract_info.json - NEEDS YOUR DEPLOYED ADDRESSES

## ⏱️ Time Estimate

- Get testnet funds: 5 minutes
- Deploy contracts: 10 minutes
- Register/create tokens: 5 minutes
- Update contract_info.json: 2 minutes
- **Total: ~25 minutes**
