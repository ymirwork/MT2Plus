import json
import app

def deep_check():
    report = {}

    # 1. Key items pricing in shops
    key_items = [
        {"vnum": 71284, "name": "Zaczarowanie Przedmiotu (mod-50)"},
        {"vnum": 71285, "name": "Wzmocnienie Przedmiotu (mod-50)"},
        {"vnum": 50513, "name": "Kamień Duchowy"},
        {"vnum": 27987, "name": "Małż"},
        {"vnum": 27992, "name": "Biała Perła"},
        {"vnum": 27993, "name": "Niebieska Perła"},
        {"vnum": 27994, "name": "Krwawa Perła"},
        {"vnum": 70031, "name": "Medal Konny"},
        {"vnum": 30004, "name": "Kawałek Klejnotu"},
        {"vnum": 30006, "name": "Ząb Orka"},
        {"vnum": 30047, "name": "Księga Klątw"},
        {"vnum": 30015, "name": "Pamiątka po Demonie"},
        {"vnum": 30050, "name": "Matowy Lód"},
    ]

    pricing = []
    for ki in key_items:
        v = ki["vnum"]
        data = app.one("""
            SELECT 
                COUNT(*) as offers,
                COALESCE(SUM(i.count), 0) as units,
                COALESCE(MIN(CAST(JSON_UNQUOTE(JSON_EXTRACT(i.ikashop_data,'$.yang')) AS UNSIGNED) / i.count), 0) AS min_price,
                COALESCE(ROUND(AVG(CAST(JSON_UNQUOTE(JSON_EXTRACT(i.ikashop_data,'$.yang')) AS UNSIGNED) / i.count)), 0) AS avg_price,
                COALESCE(MAX(CAST(JSON_UNQUOTE(JSON_EXTRACT(i.ikashop_data,'$.yang')) AS UNSIGNED) / i.count), 0) AS max_price
            FROM player.item i
            JOIN player.ikashop_offlineshop o ON o.owner = i.owner_id
            WHERE i.vnum = %s AND i.window = 'IKASHOP_OFFLINESHOP' AND o.duration > 0
              AND i.ikashop_data IS NOT NULL AND i.ikashop_data <> ''
        """, (v,)) or {}
        
        # Total in world
        wdata = app.one(f"""
            SELECT COALESCE(SUM(count), 0) as world_count
            FROM player.item i
            WHERE vnum = %s AND {app.item_not_gm_scope_sql('i')}
        """, (v,)) or {}
        
        pricing.append({
            "vnum": v,
            "name": ki["name"],
            "offers": int(data.get("offers") or 0),
            "units_in_shops": int(data.get("units") or 0),
            "world_count": int(wdata.get("world_count") or 0),
            "min_price": int(data.get("min_price") or 0),
            "min_price_fmt": app.format_yang(int(data.get("min_price") or 0)),
            "avg_price": int(data.get("avg_price") or 0),
            "avg_price_fmt": app.format_yang(int(data.get("avg_price") or 0)),
            "max_price": int(data.get("max_price") or 0),
            "max_price_fmt": app.format_yang(int(data.get("max_price") or 0)),
        })
    report["key_items_market"] = pricing

    # 2. Key Skill Books (50300) pricing and availability
    popular_skills = [
        {"id": 1, "name": "Aura Miecza"},
        {"id": 2, "name": "Berserk"},
        {"id": 3, "name": "Wir Miecza"},
        {"id": 16, "name": "Silne Ciało"},
        {"id": 61, "name": "Czarowane Ostrze"},
        {"id": 62, "name": "Czarowana Zbroja"},
        {"id": 63, "name": "Strach"},
        {"id": 31, "name": "Zasadzka"},
        {"id": 95, "name": "Pomoc Smoka"},
        {"id": 96, "name": "Błogosławieństwo"}
    ]
    books_report = []
    for s in popular_skills:
        bdata = app.one("""
            SELECT 
                COUNT(*) as offers,
                COALESCE(SUM(i.count), 0) as units,
                COALESCE(MIN(CAST(JSON_UNQUOTE(JSON_EXTRACT(i.ikashop_data,'$.yang')) AS UNSIGNED) / i.count), 0) AS min_price,
                COALESCE(ROUND(AVG(CAST(JSON_UNQUOTE(JSON_EXTRACT(i.ikashop_data,'$.yang')) AS UNSIGNED) / i.count)), 0) AS avg_price
            FROM player.item i
            JOIN player.ikashop_offlineshop o ON o.owner = i.owner_id
            WHERE i.vnum = 50300 AND i.socket0 = %s AND i.window = 'IKASHOP_OFFLINESHOP' AND o.duration > 0
              AND i.ikashop_data IS NOT NULL AND i.ikashop_data <> ''
        """, (s["id"],)) or {}

        bwdata = app.one(f"SELECT COALESCE(SUM(count), 0) as world_count FROM player.item i WHERE vnum=50300 AND socket0=%s AND {app.item_not_gm_scope_sql('i')}", (s["id"],)) or {}

        books_report.append({
            "skill_id": s["id"],
            "skill_name": s["name"],
            "offers": int(bdata.get("offers") or 0),
            "shop_units": int(bdata.get("units") or 0),
            "world_count": int(bwdata.get("world_count") or 0),
            "min_price": int(bdata.get("min_price") or 0),
            "min_price_fmt": app.format_yang(int(bdata.get("min_price") or 0)),
            "avg_price": int(bdata.get("avg_price") or 0),
            "avg_price_fmt": app.format_yang(int(bdata.get("avg_price") or 0)),
        })
    report["popular_skill_books"] = books_report

    # 3. Transactions where real players sold items (Seller is human, Buyer can be bot or human)
    human_sales = app.rows("""
        SELECT l.time, l.who as buyer_id, buyer_a.login as buyer_login,
               seller_p.name as seller_name, seller_a.login as seller_login,
               l.vnum, COALESCE(proto.locale_name, CONCAT('VNUM ', l.vnum)) as item_name,
               l.count, l.yang, l.extra
        FROM log.ikarusshop_log l
        JOIN account.account buyer_a ON buyer_a.id = l.who
        JOIN player.player seller_p ON seller_p.id = l.shop_owner
        JOIN account.account seller_a ON seller_a.id = seller_p.account_id
        LEFT JOIN player.item_proto proto ON proto.vnum = l.vnum
        WHERE l.what = 'BUY_ITEM' 
          AND seller_a.login NOT LIKE 'playerbot_%%'
        ORDER BY l.time DESC LIMIT 20
    """)
    for s in human_sales:
        s["yang_fmt"] = app.format_yang(s["yang"])
        s["time_str"] = str(s["time"])
    report["recent_human_player_sales"] = human_sales

    # Total Yang earned by human players from sales:
    human_income = app.one("""
        SELECT 
            COUNT(*) as total_sales,
            COALESCE(SUM(l.yang), 0) as total_yang_earned,
            SUM(CASE WHEN buyer_a.login LIKE 'playerbot_%%' THEN 1 ELSE 0 END) as sales_to_bots,
            COALESCE(SUM(CASE WHEN buyer_a.login LIKE 'playerbot_%%' THEN l.yang ELSE 0 END), 0) as yang_from_bots
        FROM log.ikarusshop_log l
        JOIN account.account buyer_a ON buyer_a.id = l.who
        JOIN player.player seller_p ON seller_p.id = l.shop_owner
        JOIN account.account seller_a ON seller_a.id = seller_p.account_id
        WHERE l.what = 'BUY_ITEM' 
          AND seller_a.login NOT LIKE 'playerbot_%%'
    """) or {}
    report["human_sales_summary"] = {
        "total_sales": int(human_income.get("total_sales") or 0),
        "total_yang_earned": int(human_income.get("total_yang_earned") or 0),
        "total_yang_earned_fmt": app.format_yang(int(human_income.get("total_yang_earned") or 0)),
        "sales_to_bots": int(human_income.get("sales_to_bots") or 0),
        "yang_from_bots": int(human_income.get("yang_from_bots") or 0),
        "yang_from_bots_fmt": app.format_yang(int(human_income.get("yang_from_bots") or 0)),
    }

    # 4. Human player inventory and wealth details
    human_chars = app.rows("""
        SELECT p.id, p.name, p.level, p.gold, pi.empire, a.login
        FROM player.player p
        JOIN account.account a ON a.id = p.account_id
        LEFT JOIN player.player_index pi ON pi.id = p.account_id
        WHERE a.login NOT LIKE 'playerbot_%%' AND p.name NOT IN ('[SA]Admin','Test','Admin','AdminNinja','AdminSura','AdminSzaman')
        ORDER BY p.level DESC
    """)
    for hc in human_chars:
        hc["gold_fmt"] = app.format_yang(hc["gold"])
        # Check safebox / ikashop safebox
        ika_box = app.one("SELECT gold FROM player.ikashop_safebox WHERE owner=%s", (hc["id"],)) or {}
        hc["ikashop_safebox_gold"] = int(ika_box.get("gold") or 0)
        hc["ikashop_safebox_gold_fmt"] = app.format_yang(int(ika_box.get("gold") or 0))
    report["human_characters"] = human_chars

    # 5. Check refine_proto and upgrading costs/rates
    refine_summary = app.one("""
        SELECT 
            COUNT(*) as total_refines,
            AVG(cost) as avg_cost,
            MIN(prob) as min_prob,
            MAX(prob) as max_prob,
            AVG(prob) as avg_prob
        FROM world.refine_proto
    """) or {}
    report["refine_summary"] = refine_summary

    # 6. Event flags in player.quest
    try:
        qflags = app.rows("SELECT szName as name, lValue as value FROM player.quest WHERE dwPID = 0 AND (szName LIKE '%%rate%%' OR szName LIKE '%%difficulty%%' OR szName LIKE '%%event%%' OR szName LIKE '%%biolog%%' OR szName LIKE '%%wait%%' OR szName LIKE '%%mob%%')")
        report["global_quest_flags"] = qflags
    except Exception as e:
        report["global_quest_flags"] = str(e)

    print(json.dumps(report, indent=2, default=str))

if __name__ == "__main__":
    deep_check()
