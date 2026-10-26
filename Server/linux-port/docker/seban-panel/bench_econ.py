import app, time

def time_query(label, fn):
    t0 = time.time()
    res = fn()
    dt = round(time.time() - t0, 3)
    print(f"{label:<42} : {dt}s")
    return res

print("=== BENCHMARK START ===")
time_query("KPI world_yang", lambda: app.one("SELECT COALESCE(SUM(gold),0) AS world_yang FROM player.player"))
time_query("KPI baseline_yang", lambda: app.one("SELECT value FROM player.web_seban_metric_snapshot WHERE metric='total_yang' AND captured_at >= NOW() - INTERVAL 24 HOUR ORDER BY captured_at ASC LIMIT 1"))
time_query("KPI bonus_pool", lambda: app.one(f"SELECT COALESCE(SUM(count),0) AS c FROM player.item i WHERE vnum IN (71284, 71285, 71084, 71085) AND {app.item_not_gm_scope_sql('i')}"))

w_vnums = [w["vnum"] for w in app.ECONOMY_WATCHLIST_DEF]
w_placeholders = ",".join(["%s"] * len(w_vnums))
time_query("Watchlist prices subquery JOIN", lambda: app.rows(f"""
  SELECT s.vnum, ROUND(s.total_value / s.total_units) AS avg_price, s.offers, s.total_units
  FROM player.web_seban_shop_item_snapshot s
  JOIN (
    SELECT vnum, MAX(captured_at) AS max_cap
    FROM player.web_seban_shop_item_snapshot
    WHERE vnum IN ({w_placeholders})
    GROUP BY vnum
  ) m ON s.vnum = m.vnum AND s.captured_at = m.max_cap
""", tuple(w_vnums)))

time_query("Faucet/Sink money_log 24h", lambda: app.one("""
    SELECT 
        SUM(CASE WHEN gold > 0 THEN gold ELSE 0 END) AS faucet_gold,
        SUM(CASE WHEN gold < 0 THEN -gold ELSE 0 END) AS sink_gold
    FROM log.money_log
    WHERE time >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
"""))

time_query("Faucet/Sink ikarusshop_log TAX 24h", lambda: app.one("""
    SELECT SUM(CAST(SUBSTRING_INDEX(extra, 'TAX: ', -1) AS UNSIGNED)) AS total_tax
    FROM log.ikarusshop_log
    WHERE what = 'BUY_ITEM' AND extra LIKE '%%TAX:%%'
      AND time >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
"""))

time_query("Faucet/Sink bot market JOIN", lambda: app.one("""
    SELECT SUM(l.yang) as bot_spent, COUNT(*) as bot_buys
    FROM log.ikarusshop_log l
    JOIN account.account a ON a.id = l.who
    WHERE l.what = 'BUY_ITEM' AND a.login LIKE 'playerbot_%%'
      AND l.time >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
"""))

latest = (app.one("SELECT MAX(captured_at) AS captured_at FROM player.web_seban_item_snapshot") or {}).get("captured_at")
time_query("Items snapshot SELECT with PROTO join", lambda: app.rows("""
  SELECT s.vnum, s.socket0, s.amount, COALESCE(p.locale_name, CONCAT('VNUM ', s.vnum)) AS item_name,
         p.type AS item_type, p.subtype AS item_subtype
  FROM player.web_seban_item_snapshot s LEFT JOIN player.item_proto p ON p.vnum=s.vnum
  WHERE s.captured_at=%s ORDER BY s.amount DESC
""", (latest,)))
print("=== BENCHMARK END ===")
