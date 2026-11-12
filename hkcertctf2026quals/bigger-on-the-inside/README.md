# `bigger_on_the_inside` writeup

This was an unintended discovery/achievement when an AI agent is preparing for its first dungeon fight. It wanted to purchase 3 minor health potions + 1 antidote before a dungeon run. But when AI wrote the script, no one was aware that in the shop there would only be at most 1 minor health potions stock in the shop without refresh. Although out of stock, since the target 3 potions were not bought yet, then the agent still continued to send the buy command thinking it still wants to buy potions, which led it to buy the barley porridge instead. Coincidentally it also happened that barley porridge is cheap and unstackable, making it easy to fill the slots. This loop continue until all 24 slots are filled up, out of expectation, more than the 20 spaces from the UI. And then it triggered the achievement.

## The buggy purchase script (gear_prep6.py)
```python
ls = listings('lobby.quartermaster')
print('[QM]', ls, flush=True)
want = {'health-potion-minor': 3, 'antidote': 1}
for want_item, qty in want.items():
    # dedupe listings by item_id, prefer lowest price; retry other listings on unknown_listing
    cands = sorted(((price, lid) for lid, (iid, price) in ls.items() if iid == want_item))
    got = 0
    for price, lid in cands:
        while got < qty:
            n0 = len(rej)
            send_cmd('buy_item', {'shop_id': 'lobby.quartermaster', 'item_listing_id': lid,
                                  'quantity': 1, 'expected_price': price})
            pump(2)
            s = cur()
            g = dict(s.wallet).get('gold', 0) if s else 0
            if len(rej) > n0:
                print('[buy fail]', want_item, rej[-1][:120], flush=True)
                break
            got += 1
            print('[buy]', want_item, got, '-> gold', g, flush=True)
            if g < price:
                break
    print('[buy done]', want_item, got, flush=True)
```

## Background

### The bag model
- The player inventory is a slot-addressed array. Every item has a `Slot` index and a `SlotKind` (`Bag=0`, `Equip=1`, `Stash=2`).
- The Unity client renders a 20-cell grid (`InventoryGridView.Capacity = 20`).
- The server actually accepts items at slots 0 to 23: 20 visible + 4 "overflow" slots (indices 20-23) that the UI never draws.

### The shop model (root cause of the porridge flood)
From `StreamingAssets/content/shop.json`:

- The lobby quartermaster has a set of permanent listings: including `meal-barley-porridge` that are always buyable.
- He also has a rotating pool (potions, antidotes, etc.) that is re-rolled on every shop refresh: only 2-4 pool items appear at a time, with rarity weights and price jitter. From my game experience at most 1 minor health potion could be bought at one refresh. And Listing IDs from a previous refresh become invalid, which buying them will return `unknown_listing` rejections, making it buy barley porridge

### The item model (why porridge specifically floods cells)
From `StreamingAssets/content/items.json`:

```
meal-barley-porridge: Consumable / Uncommon / effectId hunger-quarter
                      maxStack: 1   baseGoldValue: 48
health-potion-minor:  maxStack: 5
```

Thus the unstackable barley porridge fills the 24 cells quickly

### The bugs
The buy loop was keyed by `item id`, not by listing freshness:

1. It looked up the quartermaster's listings and tried to buy `health-potion-minor` × 3 and `antidote` × 1.
2. After buying 1 potion, the shop has no more potion and the shop rejects the stale listing ids with `unknown_listing`.
3. The loop's only stop conditions were `server rejected` or `not enough gold`. A rejection of an item didn't stop the loop. It fell through to the next candidate item, which was porridge, a permanent listing.
4. The server happily sold one porridge per buy, 48-72g each, always in stock.
5. The server placed each porridge in the first free slot. When visible slots 0-19 filled, it kept going into slots 20, 21, 22, 23 causing the overflow region the UI doesn't render.
6. At 24 items, the server answered `command.buy.bag_full` and the loop stopped, so there are 4 hidden slots.

### The trigger
The award is done not immediately during the purchase into the hidden slots. Instead we found out it could be detected at party creation event or swap_slots (swapping a stash slot with bag slot) event. This was found during post-testing, since the entire thing was accidentally achieved, we needed to investigate more on the reasonings about what happened, and eventually tried to understand what could be the achievement trigger. (`replay_script.py`)
