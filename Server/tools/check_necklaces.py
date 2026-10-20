import json
import app

def inspect_necklaces():
    query = """
    SELECT i.id, i.vnum, proto.locale_name, i.window, i.owner_id, p.name as owner_name, a.login as owner_login,
           (a.login NOT LIKE 'playerbot_%%' AND p.name NOT IN ('[SA]Admin','Test','Admin','AdminNinja','AdminSura','AdminSzaman')) as is_player,
           i.attrtype0, i.attrvalue0, i.attrtype1, i.attrvalue1, i.attrtype2, i.attrvalue2, i.attrtype3, i.attrvalue3, i.attrtype4, i.attrvalue4,
           i.ikashop_data
    FROM player.item i
    JOIN player.item_proto proto ON proto.vnum = i.vnum
    LEFT JOIN player.player p ON p.id = i.owner_id
    LEFT JOIN account.account a ON a.id = p.account_id
    WHERE proto.type = 2 AND proto.subtype = 5
      AND (
        (i.attrtype0 = 6 AND i.attrvalue0 > 0) OR
        (i.attrtype1 = 6 AND i.attrvalue1 > 0) OR
        (i.attrtype2 = 6 AND i.attrvalue2 > 0) OR
        (i.attrtype3 = 6 AND i.attrvalue3 > 0) OR
        (i.attrtype4 = 6 AND i.attrvalue4 > 0)
      )
    """
    rows = app.rows(query)
    print(f"Total necklaces with HP in world: {len(rows)}")
    
    in_shop = [r for r in rows if r['window'] == 'IKASHOP_OFFLINESHOP']
    print(f"Necklaces with HP currently in offline shops: {len(in_shop)}")
    
    for r in in_shop:
        yang = 0
        if r.get('ikashop_data'):
            try:
                d = json.loads(r['ikashop_data'])
                yang = int(d.get('yang', 0))
            except Exception:
                pass
        hp_val = 0
        bonus_list = []
        for idx in range(5):
            at = r.get(f'attrtype{idx}')
            val = r.get(f'attrvalue{idx}')
            if at and val:
                if at == 1:
                    hp_val = val
                bonus_list.append(f"Type {at}: +{val}")
                
        print(f"- {r['locale_name']} (vnum {r['vnum']}) | HP: +{hp_val} | Price: {app.format_yang(yang)} ({yang} Yang) | Owner: {r['owner_name']} (is_real_player: {r['is_player']}) | All bonuses: {', '.join(bonus_list)}")

    # Let's also check all necklaces in shops regardless of HP
    all_shop_necklaces = app.rows("""
    SELECT i.vnum, proto.locale_name, COUNT(*) as cnt, MIN(CAST(JSON_UNQUOTE(JSON_EXTRACT(i.ikashop_data,'$.yang')) AS UNSIGNED)) as min_p,
           AVG(CAST(JSON_UNQUOTE(JSON_EXTRACT(i.ikashop_data,'$.yang')) AS UNSIGNED)) as avg_p,
           MAX(CAST(JSON_UNQUOTE(JSON_EXTRACT(i.ikashop_data,'$.yang')) AS UNSIGNED)) as max_p
    FROM player.item i
    JOIN player.item_proto proto ON proto.vnum = i.vnum
    WHERE proto.type = 2 AND proto.subtype = 5 AND i.window = 'IKASHOP_OFFLINESHOP'
    GROUP BY i.vnum
    """)
    print("\nAll necklaces in offline shops summary:")
    for asn in all_shop_necklaces:
        min_p = int(asn.get('min_p') or 0)
        avg_p = int(asn.get('avg_p') or 0)
        max_p = int(asn.get('max_p') or 0)
        print(f"* {asn['locale_name']} (vnum {asn['vnum']}): count={asn['cnt']}, min={app.format_yang(min_p)}, avg={app.format_yang(avg_p)}, max={app.format_yang(max_p)}")

if __name__ == "__main__":
    inspect_necklaces()
