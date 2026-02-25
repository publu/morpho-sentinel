#!/usr/bin/env python3
"""
morpho-lender: Query Morpho Blue markets, vaults, and positions.

Usage:
    python3 morpho_check.py markets [--chain base|ethereum] [--asset USDC]
    python3 morpho_check.py vaults  [--chain base|ethereum] [--asset USDC]
    python3 morpho_check.py position <address> [--chain base|ethereum]

No dependencies — uses only Python standard library.
"""
import json
import sys
import urllib.request

API = 'https://blue-api.morpho.org/graphql'
CHAIN_IDS = {'ethereum': 1, 'base': 8453}


def graphql(query: str) -> dict:
    payload = json.dumps({'query': query}).encode()
    req = urllib.request.Request(API, data=payload, headers={'Content-Type': 'application/json'})
    resp = json.loads(urllib.request.urlopen(req, timeout=15).read())
    if 'errors' in resp:
        print(f'GraphQL error: {resp["errors"][0]["message"]}')
        sys.exit(1)
    return resp.get('data', {})


def fmt_usd(n: float) -> str:
    if n >= 1e9:
        return f'${n/1e9:.1f}B'
    if n >= 1e6:
        return f'${n/1e6:.0f}M'
    if n >= 1e3:
        return f'${n/1e3:.1f}k'
    return f'${n:,.2f}'


def list_markets(chain: str = 'base', asset: str | None = None):
    chain_id = CHAIN_IDS.get(chain, 8453)
    search = f', search: "{asset}"' if asset else ''
    query = f'''{{
        markets(
            where: {{ chainId_in: [{chain_id}]{search}, supplyAssetsUsd_gte: 100000 }},
            orderBy: SupplyApy, orderDirection: Desc, first: 15
        ) {{
            items {{
                loanAsset {{ symbol }}
                collateralAsset {{ symbol }}
                state {{
                    supplyApy
                    borrowApy
                    supplyAssetsUsd
                    utilization
                }}
            }}
        }}
    }}'''
    data = graphql(query)
    items = data.get('markets', {}).get('items', [])
    if not items:
        print(f'No markets found on {chain}')
        return

    print(f'MORPHO BLUE — {chain.title()}\n')
    print(f'  {"MARKET":<26} {"SUPPLY APY":>10} {"TVL":>10} {"UTIL":>8}')
    print(f'  {"─" * 58}')
    for m in items:
        loan = m['loanAsset']['symbol']
        coll = m['collateralAsset']['symbol'] if m['collateralAsset'] else '—'
        state = m['state']
        apy = (state['supplyApy'] or 0) * 100
        tvl = state['supplyAssetsUsd'] or 0
        util = (state['utilization'] or 0) * 100
        print(f'  {loan + " / " + coll:<26} {apy:>9.2f}% {fmt_usd(tvl):>10} {util:>7.0f}%')
    print()


def list_vaults(chain: str = 'base', asset: str | None = None):
    chain_id = CHAIN_IDS.get(chain, 8453)
    asset_filter = f', assetSymbol_in: ["{asset}"]' if asset else ''
    query = f'''{{
        vaults(
            where: {{ chainId_in: [{chain_id}]{asset_filter} }},
            orderBy: Apy, orderDirection: Desc, first: 15
        ) {{
            items {{
                name
                address
                asset {{ symbol }}
                state {{
                    totalAssetsUsd
                    apy
                    curator
                }}
            }}
        }}
    }}'''
    data = graphql(query)
    items = data.get('vaults', {}).get('items', [])
    if not items:
        print(f'No vaults found on {chain}')
        return

    print(f'MORPHO VAULTS — {chain.title()}\n')
    print(f'  {"VAULT":<30} {"APY":>8} {"TVL":>10} {"CURATOR":<24}')
    print(f'  {"─" * 74}')
    for v in items:
        name = v['name'][:28]
        state = v['state']
        apy = (state['apy'] or 0) * 100
        tvl = state['totalAssetsUsd'] or 0
        curator = state.get('curator') or '—'
        if curator.startswith('0x'):
            curator = curator[:10] + '...'
        print(f'  {name:<30} {apy:>7.2f}% {fmt_usd(tvl):>10} {curator[:22]:<24}')
    print()


def check_position(address: str, chain: str = 'base'):
    chain_id = CHAIN_IDS.get(chain, 8453)
    query = f'''{{
        marketPositions(
            where: {{ userAddress_in: ["{address.lower()}"], chainId_in: [{chain_id}], supplyShares_gte: 1 }},
            first: 20
        ) {{
            items {{
                supplyAssetsUsd
                borrowAssetsUsd
                healthFactor
                market {{
                    loanAsset {{ symbol }}
                    collateralAsset {{ symbol }}
                    state {{ supplyApy }}
                }}
            }}
        }}
    }}'''
    data = graphql(query)
    items = data.get('marketPositions', {}).get('items', [])

    positions = [p for p in items
                 if (p.get('supplyAssetsUsd') or 0) > 0.01
                 or (p.get('borrowAssetsUsd') or 0) > 0.01]

    if not positions:
        # Also check borrow-only positions
        query2 = f'''{{
            marketPositions(
                where: {{ userAddress_in: ["{address.lower()}"], chainId_in: [{chain_id}], borrowShares_gte: 1 }},
                first: 20
            ) {{
                items {{
                    supplyAssetsUsd
                    borrowAssetsUsd
                    healthFactor
                    market {{
                        loanAsset {{ symbol }}
                        collateralAsset {{ symbol }}
                        state {{ supplyApy }}
                    }}
                }}
            }}
        }}'''
        data2 = graphql(query2)
        items2 = data2.get('marketPositions', {}).get('items', [])
        positions = [p for p in items2
                     if (p.get('supplyAssetsUsd') or 0) > 0.01
                     or (p.get('borrowAssetsUsd') or 0) > 0.01]

    if not positions:
        print(f'No Morpho positions found on {chain.title()}')
        return

    print(f'=== Morpho Blue — {chain.title()} ===\n')
    for p in positions:
        market = p['market']
        loan = market['loanAsset']['symbol']
        coll = market['collateralAsset']['symbol'] if market['collateralAsset'] else '—'
        supply = p.get('supplyAssetsUsd') or 0
        borrow = p.get('borrowAssetsUsd') or 0
        apy = (market['state']['supplyApy'] or 0) * 100
        hf = p.get('healthFactor')
        print(f'  Market:    {loan} / {coll}')
        print(f'  Supplied:  ${supply:,.2f}')
        print(f'  Borrowed:  ${borrow:,.2f}')
        print(f'  APY:       {apy:.2f}%')
        if hf is not None and borrow > 0:
            print(f'  Health:    {hf:.4f}')
        print()


def main():
    if len(sys.argv) < 2:
        print('Usage:')
        print('  python3 morpho_check.py markets [--chain base|ethereum] [--asset USDC]')
        print('  python3 morpho_check.py vaults  [--chain base|ethereum] [--asset USDC]')
        print('  python3 morpho_check.py position <address> [--chain base|ethereum]')
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    chain = 'base'
    asset = None
    address = None

    i = 0
    while i < len(args):
        if args[i] == '--chain' and i + 1 < len(args):
            chain = args[i + 1].lower()
            i += 2
        elif args[i] == '--asset' and i + 1 < len(args):
            asset = args[i + 1].upper()
            i += 2
        elif not args[i].startswith('--'):
            address = args[i]
            i += 1
        else:
            i += 1

    if cmd == 'markets':
        list_markets(chain, asset)
    elif cmd == 'vaults':
        list_vaults(chain, asset)
    elif cmd == 'position':
        if not address:
            print('Error: address required')
            print('Usage: python3 morpho_check.py position 0xYourAddress')
            sys.exit(1)
        check_position(address, chain)
    else:
        print(f'Unknown command: {cmd}')
        sys.exit(1)


if __name__ == '__main__':
    main()
