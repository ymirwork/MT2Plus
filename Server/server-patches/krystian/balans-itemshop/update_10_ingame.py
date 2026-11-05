import re

sql_path = r'Server\linux-port\docker\mariadb\playerbot\mod\10_ingame_itemshop.sql'
patch_path = r'Server\server-patches\krystian\balans-itemshop\balans_itemshop.sql'
backup_path = r'Server\backups\itemshop_backup_pre_balance_20261105.sql'

# Odczytujemy oryginalny stan z backupu
with open(backup_path, 'r', encoding='utf-16') as f:
    backup_sql = f.read()

with open(patch_path, 'r', encoding='utf-8') as f:
    patch = f.read()

pattern = re.compile(r'\((\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*\'(\w+)\',\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)')
patch_items = {int(m[0]): m for m in pattern.findall(patch)}

# Wyciagamy z backupu wszystko oprocz 701-799
existing_items = {}
for m in pattern.findall(backup_sql):
    idx = int(m[0])
    if not (701 <= idx <= 799):
        existing_items[idx] = m

all_items = {}
all_items.update(existing_items)
all_items.update(patch_items)

sorted_keys = sorted(all_items.keys())
print('Laczna liczba pozycji (oryginalne SM + 30 SZ):', len(sorted_keys))

lines = []
for k in sorted_keys:
    m = all_items[k]
    lines.append(f"({m[0]},{m[1]},{m[2]},{m[3]},'{m[4]}',{m[5]},{m[6]},{m[7]},{m[8]})")

new_insert_values = ',\n'.join(lines) + ';'

with open(sql_path, 'r', encoding='utf-8') as f:
    sql = f.read()

insert_start = sql.find("INSERT INTO `itemshop_items`")
values_start = sql.find("VALUES", insert_start)
header_end = values_start + len("VALUES")
semicolon_idx = sql.find(";", header_end)
after_insert = sql[semicolon_idx + 1:]

new_sql = sql[:header_end] + " " + new_insert_values + after_insert

with open(sql_path, 'w', encoding='utf-8') as f:
    f.write(new_sql)

print('10_ingame_itemshop.sql zsynchronizowany pomyslnie!')
