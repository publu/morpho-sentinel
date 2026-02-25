# Morpho Sentinel

Browse and interact with Morpho Blue lending markets. Check supply APYs, inspect curated vaults, and monitor positions across chains.

## Usage

When the user asks about Morpho markets, yields, vaults, or lending positions, use this skill.

### Commands

- **List markets**: "show me morpho markets on base"
- **Check position**: "check my morpho position for 0x..."
- **Best yields**: "what are the best morpho USDC yields?"
- **Vault info**: "tell me about the steakhouse USDC vault"

## How It Works

### Morpho Blue API

Morpho Blue exposes data via their public API at `https://blue-api.morpho.org/graphql`.

**Query markets:**
```bash
curl -s -X POST https://blue-api.morpho.org/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ markets(where: { chainId_in: [8453, 1] }) { items { uniqueKey loanAsset { symbol } collateralAsset { symbol } state { supplyApy borrowApy supplyAssetsUsd borrowAssetsUsd utilization } } } }"}'
```

**Query vaults:**
```bash
curl -s -X POST https://blue-api.morpho.org/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ vaults(where: { chainId_in: [8453, 1] }) { items { name address asset { symbol } state { totalAssetsUsd apy curator } } } }"}'
```

**Query user positions:**
```bash
curl -s -X POST https://blue-api.morpho.org/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ marketPositions(where: { userAddress_in: [\"<ADDRESS>\"], chainId_in: [8453], supplyShares_gte: 1 }, first: 20) { items { supplyAssetsUsd borrowAssetsUsd healthFactor market { loanAsset { symbol } collateralAsset { symbol } state { supplyApy } } } } }"}'
```

### Useful GraphQL Queries

#### Top USDC vaults by APY
```graphql
{
  vaults(where: { chainId_in: [8453, 1], assetSymbol_in: ["USDC"] }, orderBy: Apy, orderDirection: Desc, first: 10) {
    items {
      name
      address
      state {
        totalAssetsUsd
        apy
        curator
      }
    }
  }
}
```

#### Markets for a specific asset
```graphql
{
  markets(where: { chainId_in: [8453], search: "USDC" }, orderBy: SupplyApy, orderDirection: Desc) {
    items {
      loanAsset { symbol }
      collateralAsset { symbol }
      state {
        supplyApy
        borrowApy
        supplyAssetsUsd
        utilization
      }
    }
  }
}
```

### Chain IDs

| Chain | ID |
|-------|----|
| Ethereum | 1 |
| Base | 8453 |

### On-Chain: Direct RPC

For real-time position data, call Morpho Blue contract directly.

**Morpho Blue contract:** `0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb` (same on Ethereum and Base)

**Function: `position(bytes32 id, address user)`**
- Selector: `0x0eca8bf7` (first 4 bytes of keccak256)
- Returns: supplyShares, borrowShares, collateral

### Output Format

When listing markets:
```
MORPHO BLUE — Base

  MARKET                    SUPPLY APY    TVL         UTILIZATION
  ─────────────────────────────────────────────────────────────
  USDC / wstETH             4.12%         $89M        68%
  USDC / WETH               3.82%         $142M       71%
  USDC / cbBTC              2.91%         $67M        54%
```

When showing vaults:
```
MORPHO VAULTS — Base

  VAULT                     APY      TVL          CURATOR
  ──────────────────────────────────────────────────────────
  Steakhouse USDC           4.12%    $156M        Steakhouse Financial
  Gauntlet USDC Prime       3.87%    $234M        Gauntlet
  Flagship USDC             3.45%    $89M         Morpho Association
```

When reporting positions:
```
=== Morpho Blue Position ===
  Market:      USDC / wstETH (Base)
  Supplied:    $47,832.00
  Borrowed:    $0.00
  Collateral:  0.00 wstETH
  APY:         4.12%
```

### Key Curators

- **Steakhouse Financial** — Conservative, institutional-grade risk
- **Gauntlet** — Quantitative risk management
- **B.Protocol** — Liquidation-focused
- **Morpho Association** — Flagship vaults

### Links

- App: https://app.morpho.org
- Docs: https://docs.morpho.org
- API: https://blue-api.morpho.org/graphql
