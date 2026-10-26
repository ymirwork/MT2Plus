import json
import app

def analyze():
    report = {}

    # 1. Yang & Inflation
    world_yang_row = app.one("SELECT COALESCE(SUM(gold),0) AS world_yang, COUNT(*) as cnt FROM player.player")
    world_yang = int(world_yang_row["world_yang"])
    total_chars = int(world_yang_row["cnt"])
    
    inflation_factor = app.calculate_world_yang_inflation(world_yang)
    
    wealth_row = app.one("""
    SELECT 
      SUM(CASE WHEN a.login NOT LIKE 'playerbot_%%' AND p.name NOT IN ('[SA]Admin','Test','Admin','AdminNinja','AdminSura','AdminSzaman') THEN p.gold ELSE 0 END) AS player_gold,
      SUM(CASE WHEN a.login LIKE 'playerbot_%%' THEN p.gold ELSE 0 END) AS bot_gold,
      COUNT(CASE WHEN a.login NOT LIKE 'playerbot_%%' AND p.name NOT IN ('[SA]Admin','Test','Admin','AdminNinja','AdminSura','AdminSzaman') THEN 1 END) AS player_count,
      COUNT(CASE WHEN a.login LIKE 'playerbot_%%' THEN 1 END) AS bot_count
    FROM player.player p
    JOIN account.account a ON a.id = p.account_id
    """)
    
    try:
        ika_safebox = app.one("SELECT COALESCE(SUM(gold), 0) AS ika_gold FROM player.ikashop_safebox") or {"ika_gold": 0}
    except Exception:
        ika_safebox = {"ika_gold": 0}

    report["yang"] = {
        "world_yang": world_yang,
        "world_yang_formatted": app.format_yang(world_yang),
        "inflation_factor": round(inflation_factor, 4),
        "player_gold": int(wealth_row.get("player_gold") or 0),
        "player_gold_formatted": app.format_yang(int(wealth_row.get("player_gold") or 0)),
        "player_count": int(wealth_row.get("player_count") or 0),
        "bot_gold": int(wealth_row.get("bot_gold") or 0),
        "bot_gold_formatted": app.format_yang(int(wealth_row.get("bot_gold") or 0)),
        "bot_count": int(wealth_row.get("bot_count") or 0),
        "ika_safebox_gold": int(ika_safebox.get("ika_gold") or 0),
        "ika_safebox_gold_fmt": app.format_yang(int(ika_safebox.get("ika_gold") or 0)),
    }

    # Anomalies: negative gold or >= 1.9B
    anomalies = app.rows("""
    SELECT p.id, p.name, p.gold, a.login
    FROM player.player p
    JOIN account.account a ON a.id = p.account_id
    WHERE p.gold < 0 OR p.gold >= 1900000000
    """)
    report["gold_anomalies"] = anomalies

    # Top 5 richest players and bots
    top_players = app.rows("""
    SELECT p.name, p.level, p.gold, pi.empire
    FROM player.player p
    JOIN account.account a ON a.id = p.account_id
    LEFT JOIN player.player_index pi ON pi.id = p.account_id
    WHERE a.login NOT LIKE 'playerbot_%%' AND p.name NOT IN ('[SA]Admin','Test','Admin','AdminNinja','AdminSura','AdminSzaman')
    ORDER BY p.gold DESC LIMIT 5
    """)
    for p in top_players:
        p["gold_fmt"] = app.format_yang(p["gold"])
    report["top_players"] = top_players

    top_bots = app.rows("""
    SELECT p.name, p.level, p.gold, pi.empire
    FROM player.player p
    JOIN account.account a ON a.id = p.account_id
    LEFT JOIN player.player_index pi ON pi.id = p.account_id
    WHERE a.login LIKE 'playerbot_%%'
    ORDER BY p.gold DESC LIMIT 5
    """)
    for b in top_bots:
        b["gold_fmt"] = app.format_yang(b["gold"])
    report["top_bots"] = top_bots

    # 2. Faucet vs Sink (Last 24h & Overall)
    fs_24h = app.one("""
        SELECT 
            SUM(CASE WHEN gold > 0 THEN gold ELSE 0 END) AS faucet_gold,
            SUM(CASE WHEN gold < 0 THEN -gold ELSE 0 END) AS sink_gold,
            SUM(CASE WHEN type = 'MONSTER' AND gold > 0 THEN gold ELSE 0 END) AS monster_drop,
            SUM(CASE WHEN type = 'DROP' AND gold > 0 THEN gold ELSE 0 END) AS ground_drop,
            SUM(CASE WHEN type = 'SHOP' AND gold > 0 THEN gold ELSE 0 END) AS npc_sales,
            SUM(CASE WHEN type = 'REFINE' AND gold < 0 THEN -gold ELSE 0 END) AS blacksmith_sink,
            SUM(CASE WHEN type = 'GUILD' AND gold < 0 THEN -gold ELSE 0 END) AS guild_sink
        FROM log.money_log
        WHERE time >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
    """) or {}
    
    tax_24h = app.one("""
        SELECT SUM(CAST(SUBSTRING_INDEX(extra, 'TAX: ', -1) AS UNSIGNED)) AS total_tax
        FROM log.ikarusshop_log
        WHERE what = 'BUY_ITEM' AND extra LIKE '%%TAX:%%'
          AND time >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
    """) or {}

    faucet_val = int(fs_24h.get("faucet_gold") or 0)
    sink_val = int(fs_24h.get("sink_gold") or 0) + int(tax_24h.get("total_tax") or 0)

    report["faucet_sink_24h"] = {
        "faucet_gold": faucet_val,
        "faucet_gold_fmt": app.format_yang(faucet_val),
        "sink_gold": sink_val,
        "sink_gold_fmt": app.format_yang(sink_val),
        "net_delta": faucet_val - sink_val,
        "net_delta_fmt": app.format_yang(faucet_val - sink_val),
        "burn_rate_pct": round(sink_val / faucet_val * 100, 1) if faucet_val > 0 else 0.0,
        "blacksmith_sink": int(fs_24h.get("blacksmith_sink") or 0),
        "shop_tax_sink": int(tax_24h.get("total_tax") or 0),
        "monster_drop": int(fs_24h.get("monster_drop") or 0),
        "npc_sales": int(fs_24h.get("npc_sales") or 0),
    }

    # 3. Offline Shops & Market (Ikarus)
    shops_count = app.one("""
        SELECT 
            COUNT(*) as total_shops,
            SUM(CASE WHEN a.login LIKE 'playerbot_%%' THEN 1 ELSE 0 END) as bot_shops,
            SUM(CASE WHEN a.login NOT LIKE 'playerbot_%%' THEN 1 ELSE 0 END) as player_shops
        FROM player.ikashop_offlineshop s
        JOIN player.player p ON p.id = s.owner
        JOIN account.account a ON a.id = p.account_id
    """) or {}

    latest_shop = (app.one("SELECT MAX(captured_at) AS m FROM player.web_seban_shop_snapshot") or {}).get("m")
    shop_stats = app.one("SELECT COALESCE(SUM(total_value),0) AS shop_val, COALESCE(SUM(offer_count),0) AS shop_offers, COALESCE(SUM(item_count),0) as item_cnt FROM player.web_seban_shop_snapshot WHERE captured_at=%s", (latest_shop,)) if latest_shop else {}

    report["shops"] = {
        "total_shops": int(shops_count.get("total_shops") or 0),
        "bot_shops": int(shops_count.get("bot_shops") or 0),
        "player_shops": int(shops_count.get("player_shops") or 0),
        "total_offers": int(shop_stats.get("shop_offers") or 0),
        "total_items": int(shop_stats.get("item_cnt") or 0),
        "total_value": int(shop_stats.get("shop_val") or 0),
        "total_value_fmt": app.format_yang(int(shop_stats.get("shop_val") or 0)),
    }

    # 4. Market Transactions (last 24h & last 7 days)
    tx_24h = app.one("""
        SELECT 
            COUNT(*) as tx_count,
            COALESCE(SUM(yang), 0) as tx_volume,
            SUM(CASE WHEN a.login LIKE 'playerbot_%%' THEN 1 ELSE 0 END) as bot_buyer_tx,
            SUM(CASE WHEN a.login LIKE 'playerbot_%%' THEN yang ELSE 0 END) as bot_buyer_volume
        FROM log.ikarusshop_log l
        JOIN account.account a ON a.id = l.who
        WHERE l.what = 'BUY_ITEM' AND l.time >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
    """) or {}

    report["transactions_24h"] = {
        "count": int(tx_24h.get("tx_count") or 0),
        "volume": int(tx_24h.get("tx_volume") or 0),
        "volume_fmt": app.format_yang(int(tx_24h.get("tx_volume") or 0)),
        "bot_buys_count": int(tx_24h.get("bot_buyer_tx") or 0),
        "bot_buys_volume": int(tx_24h.get("bot_buyer_volume") or 0),
        "bot_buys_volume_fmt": app.format_yang(int(tx_24h.get("bot_buyer_volume") or 0)),
    }

    # 5. YmirWork Telemetry (Liquidations of M1/M2 ulepszacze)
    liq = app.one("""
        SELECT 
            COUNT(*) AS total_liquidations,
            COUNT(DISTINCT who) AS active_bots,
            SUM(CASE WHEN vnum=71285 THEN 1 ELSE 0 END) AS adds_created,
            SUM(CASE WHEN vnum=71284 THEN 1 ELSE 0 END) AS switches_created
        FROM log.log
        WHERE how='PLAYERBOT_M1M2_LIQUIDATION'
    """) or {}
    report["ymirwork"] = {
        "total_liquidations": int(liq.get("total_liquidations") or 0),
        "active_bots": int(liq.get("active_bots") or 0),
        "adds_created": int(liq.get("adds_created") or 0),
        "switches_created": int(liq.get("switches_created") or 0),
    }

    # 6. Circulation of critical items
    key_vnums = [71284, 71285, 50513, 27992, 27993, 27994, 70031, 27987, 51001, 71084, 71085]
    placeholders = ','.join(['%s'] * len(key_vnums))
    circ = app.rows(f"""
        SELECT i.vnum, COALESCE(p.locale_name, CONCAT('VNUM ', i.vnum)) as name,
               SUM(CASE WHEN i.window IN ('INVENTORY','EQUIPMENT') THEN i.count ELSE 0 END) AS inv_count,
               SUM(CASE WHEN i.window='SAFEBOX' THEN i.count ELSE 0 END) AS safebox_count,
               SUM(CASE WHEN i.window='IKASHOP_OFFLINESHOP' THEN i.count ELSE 0 END) AS shop_count,
               SUM(i.count) AS total_count
        FROM player.item i
        LEFT JOIN player.item_proto p ON p.vnum = i.vnum
        WHERE i.vnum IN ({placeholders})
          AND {app.item_not_gm_scope_sql('i')}
        GROUP BY i.vnum
    """, tuple(key_vnums))
    report["critical_items"] = circ

    # 7. Infinite Money Exploit Check (item_proto: shop_buy_price > gold)
    bad_prices = app.rows("""
        SELECT vnum, locale_name, gold, shop_buy_price
        FROM player.item_proto
        WHERE shop_buy_price > gold AND gold > 0
        LIMIT 10
    """)
    report["infinite_money_exploits"] = bad_prices

    # 8. M1/M2 upgrade materials sample supply in offline shops
    supply_row = app.one(f"""
        SELECT COALESCE(SUM(count), 0) AS total_supply
        FROM player.item i
        WHERE window = 'IKASHOP_OFFLINESHOP'
          AND vnum IN (30031, 30028, 30071, 30004, 30003, 30078)
          AND {app.item_not_gm_scope_sql('i')}
    """) or {}
    sample_supply = int(supply_row.get("total_supply") or 0)
    if sample_supply < 300:
        buyer_pct = 3
    elif sample_supply >= 8000:
        buyer_pct = 35
    else:
        buyer_pct = 5 + int((sample_supply - 300) * 25 / 7700)
    report["ymirwork_market_balance"] = {
        "sample_m1m2_shop_supply": sample_supply,
        "dynamic_bot_buyer_ratio_pct": buyer_pct
    }

    # 9. Skill books (50300) availability
    ku_stats = app.one(f"""
        SELECT 
            COUNT(DISTINCT socket0) as distinct_skills,
            COUNT(*) as total_books,
            SUM(CASE WHEN window='IKASHOP_OFFLINESHOP' THEN 1 ELSE 0 END) as shop_books
        FROM player.item i
        WHERE vnum=50300 AND {app.item_not_gm_scope_sql('i')}
    """) or {}
    report["skill_books"] = ku_stats

    # 10. Server Difficulty & event flags
    try:
        flags = app.rows("SELECT szName as name, lValue as value FROM player.quest WHERE dwPID = 0 AND (szName LIKE '%%rate%%' OR szName LIKE '%%event%%' OR szName LIKE '%%difficulty%%' OR szName LIKE '%%mob%%' OR szName LIKE '%%m2_%%')")
        report["event_flags"] = flags
    except Exception as e:
        report["event_flags"] = str(e)

    print(json.dumps(report, indent=2, default=str))

if __name__ == "__main__":
    analyze()
