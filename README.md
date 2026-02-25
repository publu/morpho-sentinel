# morpho-lender

Browse Morpho Blue lending markets, curated vaults, and user positions. Claude Code skill + standalone CLI.

## Install as Claude Code Skill

```bash
curl -sL https://raw.githubusercontent.com/publu/morpho-lender/master/morpho-lender.md >> ~/.claude/skills/morpho-lender.md
```

Then ask: _"show me the best USDC yields on morpho"_

## Standalone CLI

```bash
# Top USDC markets on Base
python3 morpho_check.py markets --chain base --asset USDC

# All vaults on Ethereum
python3 morpho_check.py vaults --chain ethereum

# Check a position
python3 morpho_check.py position 0xYourAddress --chain base
```

No dependencies — Python standard library only.

## Supported Chains

| Chain | ID |
|-------|----|
| Base | 8453 |
| Ethereum | 1 |

## Output

```
MORPHO BLUE — Base

  MARKET                     SUPPLY APY        TVL     UTIL
  ──────────────────────────────────────────────────────────
  USDC / cbBTC                    3.89%      $1.0B      90%
  USDC / wstETH                   3.89%    $955.5k      90%
  USDC / WETH                     3.82%    $142.0M      71%
```

## Data Source

Uses the [Morpho Blue GraphQL API](https://blue-api.morpho.org/graphql) — no API key required.

## Links

- [Morpho App](https://app.morpho.org)
- [Morpho Docs](https://docs.morpho.org)

## License

MIT
