#ifndef __INC_METIN2_PLAYERBOT_CUSTOM_PRICES_H__
#define __INC_METIN2_PLAYERBOT_CUSTOM_PRICES_H__

#include <unordered_map>
#include <string>
#include "db.h"

// MT2009_PLUS_PLAYERBOT_CUSTOM_PRICES_V1:
// Dynamic custom base prices for playerbots (materials, soul stones, skill books, etc.)
// Configurable via the web admin panel under /economy/bot-prices.
namespace playerbot_custom_prices
{
	inline std::unordered_map<DWORD, DWORD>& GetItemMap()
	{
		static std::unordered_map<DWORD, DWORD> s_map;
		return s_map;
	}

	inline std::unordered_map<DWORD, DWORD>& GetSkillMap()
	{
		static std::unordered_map<DWORD, DWORD> s_map;
		return s_map;
	}

	inline void EnsureTable()
	{
		static bool s_bTableChecked = false;
		if (s_bTableChecked)
			return;
		s_bTableChecked = true;
		DBManager::instance().DirectQuery(
			"CREATE TABLE IF NOT EXISTS player.playerbot_custom_price ("
			"  price_type VARCHAR(16) NOT NULL,"
			"  target_id INT UNSIGNED NOT NULL,"
			"  price INT UNSIGNED NOT NULL,"
			"  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,"
			"  PRIMARY KEY (price_type, target_id)"
			") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
		);
	}

	inline void Reload()
	{
		EnsureTable();
		auto msg = DBManager::instance().DirectQuery(
			"SELECT price_type, target_id, price FROM player.playerbot_custom_price"
		);

		if (!msg || !msg->Get() || !msg->Get()->pSQLResult)
			return;

		std::unordered_map<DWORD, DWORD> newItemPrices;
		std::unordered_map<DWORD, DWORD> newSkillPrices;

		MYSQL_ROW row;
		while ((row = mysql_fetch_row(msg->Get()->pSQLResult)))
		{
			if (!row[0] || !row[1] || !row[2])
				continue;

			const std::string type = row[0];
			DWORD targetId = 0;
			DWORD price = 0;
			str_to_number(targetId, row[1]);
			str_to_number(price, row[2]);

			if (targetId == 0)
				continue;

			if (type == "item")
				newItemPrices[targetId] = price;
			else if (type == "skill")
				newSkillPrices[targetId] = price;
		}

		GetItemMap() = std::move(newItemPrices);
		GetSkillMap() = std::move(newSkillPrices);

		sys_log(0, "PLAYERBOT_CUSTOM_PRICES: reloaded %u item overrides, %u skill overrides",
			(unsigned int)GetItemMap().size(), (unsigned int)GetSkillMap().size());
	}

	inline void EnsureLoaded()
	{
		static bool s_bLoaded = false;
		if (!s_bLoaded)
		{
			s_bLoaded = true;
			Reload();
		}
	}

	inline DWORD GetCustomItemPrice(DWORD dwVnum)
	{
		EnsureLoaded();
		const auto& map = GetItemMap();
		auto it = map.find(dwVnum);
		if (it != map.end())
			return it->second;
		return 0;
	}

	inline DWORD GetCustomSkillPrice(DWORD dwSkill)
	{
		EnsureLoaded();
		const auto& map = GetSkillMap();
		auto it = map.find(dwSkill);
		if (it != map.end())
			return it->second;
		return 0;
	}
}

#endif
