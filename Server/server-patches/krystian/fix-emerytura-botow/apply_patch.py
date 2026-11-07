#!/usr/bin/env python3
"""
Patch: fix-emerytura-botow (MT2009_PLUS_BOT_RETIREMENT_FIX_V7)
Naprawa zapętlenia losowania emerytury botów, losowania postaci o poziomie 1,
obsługi botów z otwartym sklepem offline (prawdziwe wystawianie noszonego eq),
likwidacja blokady zamykania sklepu ze starym dropem (parametr gm w DB),
zwolnienie budżetu mutacji BotOfflineBudget dla emerytów oraz eliminacja zawieszania partii.
"""
import os
import sys

def patch_file(path, old_text, new_text, marker=None):
    if not os.path.exists(path):
        print(f"BŁĄD: Plik {path} nie istnieje!")
        return False
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    
    if marker and marker in content:
        print(f"Informacja: Wzorzec już zaaplikowany w {path} ({marker})")
        return True

    old_clean = old_text.replace("\r\n", "\n")
    content_clean = content.replace("\r\n", "\n")
    new_clean = new_text.replace("\r\n", "\n")
    
    if old_clean in content_clean:
        if "\r\n" in content:
            old_in_file = old_clean.replace("\n", "\r\n")
            new_in_file = new_clean.replace("\n", "\r\n")
        else:
            old_in_file = old_clean
            new_in_file = new_clean
        content = content.replace(old_in_file, new_in_file, 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Pomyślnie zmodyfikowano: {path}")
        return True
    else:
        print(f"BŁĄD: Nie znaleziono wzorca w {path}!")
        return False

def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
    print(f"MT2Plus Root: {repo_root}")

    # 1. ClientManagerIkarusShop.cpp (DB core)
    db_ikashop = os.path.join(repo_root, "Server/linux-port/docker/game/src/server/db/src/ClientManagerIkarusShop.cpp")
    if os.path.exists(db_ikashop):
        with open(db_ikashop, "r", encoding="utf-8", errors="ignore") as f:
            c = f.read()
        if '#include "Cache.h"' not in c:
            c = c.replace('#include "ClientManager.h"', '#include "ClientManager.h"\n#include "Cache.h"')
            with open(db_ikashop, "w", encoding="utf-8") as f:
                f.write(c)
            print(f"Pomyślnie dodano Cache.h do: {db_ikashop}")
    old_db_1 = """#ifdef ENABLE_MT2009_DISABLE_IKASHOP_DEFAULT_SAFEBOX
	if (shopCache->itemsmap.size() > 0)
	{
		sys_err("HARD CLOSE OFFLINESHOP WITH ITEM COUNT > 0 (%d) owner %d ", shopCache->itemsmap.size(), subpack.ownerid);
		return false;
	}
#else
	// caching item list
	auto items{ shopCache->itemsmap };
#endif

#ifdef ENABLE_IKASHOP_LOGS
	IkarusShopLog(subpack.ownerid, 0, "HARD_CLOSE_SHOP", subpack.ownerid);
#endif

	RemoveOfferOnShop(subpack.ownerid);
	m_offlineshopOfferCache.RemoveOffersByShopOwner(subpack.ownerid);
	m_offlineshopShopCache.CloseShop(subpack.ownerid);
	SendIkarusShopForceClose(subpack.ownerid);"""

    new_db_1 = """#ifdef ENABLE_MT2009_DISABLE_IKASHOP_DEFAULT_SAFEBOX
	// MT2009_PLUS_BOT_RETIREMENT_FIX_V7: GM / system bot retirement force close is permitted even if shop holds items
	if (!subpack.gm && shopCache->itemsmap.size() > 0)
	{
		sys_err("HARD CLOSE OFFLINESHOP WITH ITEM COUNT > 0 (%d) owner %d ", shopCache->itemsmap.size(), subpack.ownerid);
		return false;
	}
#else
	// caching item list
	auto items{ shopCache->itemsmap };
#endif

#ifdef ENABLE_IKASHOP_LOGS
	IkarusShopLog(subpack.ownerid, 0, "HARD_CLOSE_SHOP", subpack.ownerid);
#endif

	RemoveOfferOnShop(subpack.ownerid);
	m_offlineshopOfferCache.RemoveOffersByShopOwner(subpack.ownerid);
	m_offlineshopShopCache.CloseShop(subpack.ownerid);
	SendIkarusShopForceClose(subpack.ownerid);

	if (subpack.gm)
	{
		char szItemDelQuery[256];
		snprintf(szItemDelQuery, sizeof(szItemDelQuery), "DELETE FROM item WHERE `window` = 'IKASHOP_OFFLINESHOP' AND owner_id = %u", subpack.ownerid);
		CDBManager::instance().ReturnQuery(szItemDelQuery, QID_ITEM, 0, NULL);

		TItemCacheSet * pSet = GetItemCacheSet(subpack.ownerid);
		if (pSet)
		{
			TItemCacheSet::iterator it = pSet->begin();
			while (it != pSet->end())
			{
				CItemCache * pkItemCache = *it;
				if (pkItemCache && pkItemCache->Get() && pkItemCache->Get()->window == IKASHOP_OFFLINESHOP)
				{
					DeleteItemCache(pkItemCache->Get()->id);
					it = pSet->erase(it);
				}
				else
				{
					++it;
				}
			}
		}
	}"""
    patch_file(db_ikashop, old_db_1, new_db_1, "BOT_RETIREMENT_FIX_V7:")

    # 2. ikarus_shop_manager.h
    h_files = [
        os.path.join(repo_root, "Server/linux-port/docker/game/src/server/game/src/ikarus_shop_manager.h")
    ]
    old_h_1 = "/*db*/	void SendShopForceHardCloseDBPacket(DWORD pid);"
    new_h_1 = "/*db*/	void SendShopForceHardCloseDBPacket(DWORD pid, bool gm = false);"
    for f in h_files:
        patch_file(f, old_h_1, new_h_1, "SendShopForceHardCloseDBPacket(DWORD pid, bool gm = false);")

    # 3. ikarus_shop_manager.cpp
    cpp_files = [
        os.path.join(repo_root, "Server/linux-port/overlays/playerbot/src/game/src/ikarus_shop_manager.cpp"),
        os.path.join(repo_root, "Server/linux-port/docker/game/src/server/game/src/ikarus_shop_manager.cpp"),
    ]
    old_cpp_1 = """	void CShopManager::SendShopForceHardCloseDBPacket(DWORD pid)
	{
		TPacketGDNewIkarusShop pack{};
		pack.bSubHeader = SUBHEADER_GD_SHOP_FORCE_HARD_CLOSE;

		TSubPacketGDShopForceClose subpack{};
		subpack.ownerid = pid;
		subpack.gm = false;"""

    new_cpp_1 = """	void CShopManager::SendShopForceHardCloseDBPacket(DWORD pid, bool gm)
	{
		TPacketGDNewIkarusShop pack{};
		pack.bSubHeader = SUBHEADER_GD_SHOP_FORCE_HARD_CLOSE;

		TSubPacketGDShopForceClose subpack{};
		subpack.ownerid = pid;
		subpack.gm = gm;"""

    for f in cpp_files:
        patch_file(f, old_cpp_1, new_cpp_1, "SendShopForceHardCloseDBPacket(DWORD pid, bool gm)")

    # 4. playerbot_retirement.h
    target_files_retirement = [
        os.path.join(repo_root, "Server/linux-port/overlays/playerbot/src/game/src/playerbot_retirement.h"),
        os.path.join(repo_root, "Server/linux-port/docker/game/src/server/game/src/playerbot_retirement.h"),
    ]

    # Target 1: LoadPlayerBotRetireConfig default min level = 10
    old_retire_1 = """	const char* minLevel = std::getenv("PLAYERBOT_RETIRE_MIN_LEVEL");
	if (minLevel && *minLevel)
	{
		int ml = std::atoi(minLevel);
		if (ml >= 1 && ml <= 120)
			s_bPlayerBotRetireMinLevel = (BYTE)ml;
	}
	sys_log(0, "PLAYERBOT_RETIRE: count=%u batch_id=%u window_minutes=%u shop_minutes=%u min_level=%u",
			(unsigned int)s_dwPlayerBotRetireCount, (unsigned int)s_dwPlayerBotRetireBatchId,
			(unsigned int)(s_dwPlayerBotRetireWindowMs / 60000u),
			(unsigned int)(s_dwPlayerBotRetireShopMs / 60000u),
			(unsigned int)s_bPlayerBotRetireMinLevel);
}"""

    new_retire_1 = """	const char* minLevel = std::getenv("PLAYERBOT_RETIRE_MIN_LEVEL");
	s_bPlayerBotRetireMinLevel = 10; // MT2009_PLUS_BOT_RETIREMENT_FIX_V2: default to 10 to avoid level 1 bots
	if (minLevel && *minLevel)
	{
		int ml = std::atoi(minLevel);
		if (ml >= 1 && ml <= 120)
			s_bPlayerBotRetireMinLevel = (BYTE)ml;
	}
	sys_log(0, "PLAYERBOT_RETIRE: count=%u batch_id=%u window_minutes=%u shop_minutes=%u min_level=%u",
			(unsigned int)s_dwPlayerBotRetireCount, (unsigned int)s_dwPlayerBotRetireBatchId,
			(unsigned int)(s_dwPlayerBotRetireWindowMs / 60000u),
			(unsigned int)(s_dwPlayerBotRetireShopMs / 60000u),
			(unsigned int)s_bPlayerBotRetireMinLevel);
}"""

    # Target 2: RecordPlayerBotRetirePick SQL & set insert
    old_retire_2 = """	char query[512];
	snprintf(query, sizeof(query),
			"INSERT INTO common.playerbot_retire_pick (pid, batch_id, name, level, picked_at, stage) "
			"VALUES (%u, %u, '%s', %u, UNIX_TIMESTAMP(), 'shopping') "
			"ON DUPLICATE KEY UPDATE batch_id=VALUES(batch_id), name=VALUES(name), "
			"level=VALUES(level), picked_at=VALUES(picked_at), stage='shopping', reset_at=NULL",
			dwPlayerID, dwBatchId, escapedName, (unsigned int)bLevel);
	return PlayerBotRetireQuery(query);"""

    new_retire_2 = """	// MT2009_PLUS_BOT_RETIREMENT_FIX_V2: if already picked in this batch, never overwrite with a lower level
	char query[640];
	snprintf(query, sizeof(query),
			"INSERT INTO common.playerbot_retire_pick (pid, batch_id, name, level, picked_at, stage) "
			"VALUES (%u, %u, '%s', %u, UNIX_TIMESTAMP(), 'shopping') "
			"ON DUPLICATE KEY UPDATE batch_id=VALUES(batch_id), name=VALUES(name), "
			"level=IF(batch_id=VALUES(batch_id), GREATEST(level, VALUES(level)), VALUES(level)), "
			"picked_at=VALUES(picked_at), stage='shopping', reset_at=NULL",
			dwPlayerID, dwBatchId, escapedName, (unsigned int)bLevel);
	if (!PlayerBotRetireQuery(query))
		return false;
	s_setPlayerBotRetireBatchPIDs.insert(dwPlayerID);
	return true;"""

    # Target 3: RecoverPlayerBotRetirements
    old_retire_3 = """		s_mapPlayerBotRetiring[pid] = entry;
		++recovered;"""

    new_retire_3 = """		s_mapPlayerBotRetiring[pid] = entry;
		s_setPlayerBotRetireBatchPIDs.insert(pid); // MT2009_PLUS_BOT_RETIREMENT_FIX_V2
		++recovered;"""

    # Target 4: IsPlayerBotRetirementCandidateInner level & pid guard
    old_retire_4 = """bool IsPlayerBotRetirementCandidateInner(LPCHARACTER ch, BYTE bLevelLo, BYTE bLevelHi)
{
	if (!ch || ch->IsDead() || ch->IsStun() || !ch->IsItemLoaded())
		return false;
	if (ch->GetLevel() < bLevelLo || ch->GetLevel() > bLevelHi)
		return false;"""

    new_retire_4 = """bool IsPlayerBotRetirementCandidateInner(LPCHARACTER ch, BYTE bLevelLo, BYTE bLevelHi)
{
	if (!ch || ch->IsDead() || ch->IsStun() || !ch->IsItemLoaded())
		return false;
	// MT2009_PLUS_BOT_RETIREMENT_FIX_V2: minimum level guard and single-pick-per-batch guard
	if (ch->GetLevel() < s_bPlayerBotRetireMinLevel || ch->GetLevel() < bLevelLo || ch->GetLevel() > bLevelHi)
		return false;
	if (s_setPlayerBotRetireBatchPIDs.find(ch->GetPlayerID()) != s_setPlayerBotRetireBatchPIDs.end())
		return false;"""

    # Target 5: IsPlayerBotRetirementCandidateInner allow bots with offline shops (V6)
    old_retire_5 = """	if (CGuild* guild = ch->GetGuild())
		if (guild->GetMasterPID() == ch->GetPlayerID())
			return false;
	if (HasPlayerBotOfflineShop(ch))
		return false;
	return true;"""

    new_retire_5 = """	if (CGuild* guild = ch->GetGuild())
		if (guild->GetMasterPID() == ch->GetPlayerID())
			return false;
	// MT2009_PLUS_BOT_RETIREMENT_FIX_V6: bots with ordinary offline shops can retire;
	// their drop shop is cleanly closed so they can open a retirement stall with worn gear.
	// if (HasPlayerBotOfflineShop(ch)) return false;
	return true;"""

    # Target 6: AdvancePlayerBotRetirementStall close pre-existing offline shop (V6/V7)
    old_retire_6 = """EPlayerBotRetireStallResult AdvancePlayerBotRetirementStall(LPCHARACTER ch,
		TPlayerBotAIState& state, TPlayerBotRetireEntry& entry, DWORD dwNow)
{
	const DWORD pid = ch->GetPlayerID();

	// 1. A town of the bot's own kingdom, with a stall ring, on this core."""

    old_retire_6_v6 = """	if (HasPlayerBotOfflineShop(ch))
	{
		if (dwNow >= entry.dwNextAttempt)
		{
			entry.dwNextAttempt = dwNow + 2000;
			ikashop::GetManager().SendShopForceHardCloseDBPacket(pid);
			if (auto oldShop = ikashop::GetManager().GetShopByOwnerID(pid))
				ikashop::GetManager().DestroyShopEntity(oldShop);
			sys_log(0, "PLAYERBOT_RETIRE: pid=%u closing pre-existing drop shop for retirement stall", pid);
		}
		return PLAYERBOT_RETIRE_STALL_WAIT;
	}"""

    new_retire_6_v7 = """	if (HasPlayerBotOfflineShop(ch))
	{
		if (dwNow >= entry.dwNextAttempt)
		{
			entry.dwNextAttempt = dwNow + 2000;
			ikashop::GetManager().SendShopForceHardCloseDBPacket(pid, true); // MT2009_PLUS_BOT_RETIREMENT_FIX_V7: gm=true bypasses shop item guard
			if (auto oldShop = ikashop::GetManager().GetShopByOwnerID(pid))
				ikashop::GetManager().DestroyShopEntity(oldShop);
			sys_log(0, "PLAYERBOT_RETIRE: pid=%u closing pre-existing drop shop for retirement stall", pid);
		}
		return PLAYERBOT_RETIRE_STALL_WAIT;
	}"""

    # Target 7: ManagePlayerBotRetirement only wait if retirement stall was seen (V6)
    old_retire_7 = """	// A standing stall needs nothing from the bot; when it closes is decided by
	// MonitorPlayerBotRetirementStall, which does not depend on the bot being
	// steerable at that moment.
	if (entry.bStallSeen || ikashop::GetManager().GetShopByOwnerID(pid))
		return true;"""

    new_retire_7 = """	// A standing stall needs nothing from the bot; when it closes is decided by
	// MonitorPlayerBotRetirementStall, which does not depend on the bot being
	// steerable at that moment.
	// MT2009_PLUS_BOT_RETIREMENT_FIX_V6: only skip bot steering once the retirement stall has actually been seen
	if (entry.bStallSeen)
		return true;"""

    # Target 8: MonitorPlayerBotRetirementStall only adopt stall if dwSubmittedAt > 0 (V6)
    old_retire_8 = """void MonitorPlayerBotRetirementStall(DWORD pid, TPlayerBotRetireEntry& entry, DWORD dwNow)
{
	NativeShop shop = ikashop::GetManager().GetShopByOwnerID(pid);
	if (shop)
	{
		if (!entry.bStallSeen)"""

    new_retire_8 = """void MonitorPlayerBotRetirementStall(DWORD pid, TPlayerBotRetireEntry& entry, DWORD dwNow)
{
	NativeShop shop = ikashop::GetManager().GetShopByOwnerID(pid);
	// MT2009_PLUS_BOT_RETIREMENT_FIX_V6: only monitor the stall once the retirement listing was submitted (dwSubmittedAt > 0),
	// never falsely adopt a pre-existing drop shop as the retirement stall.
	if (shop && entry.dwSubmittedAt > 0)
	{
		if (!entry.bStallSeen)"""

    for f in target_files_retirement:
        patch_file(f, old_retire_1, new_retire_1, "s_bPlayerBotRetireMinLevel = 10")
        patch_file(f, old_retire_2, new_retire_2, "GREATEST(level, VALUES(level))")
        patch_file(f, old_retire_3, new_retire_3, "s_setPlayerBotRetireBatchPIDs.insert(pid)")
        patch_file(f, old_retire_4, new_retire_4, "s_bPlayerBotRetireMinLevel || ch->GetLevel() < bLevelLo")
        patch_file(f, old_retire_5, new_retire_5, "BOT_RETIREMENT_FIX_V6: bots with ordinary offline shops can retire")
        if not patch_file(f, old_retire_6_v6, new_retire_6_v7, "BOT_RETIREMENT_FIX_V7: gm=true"):
            patch_file(f, old_retire_6, "EPlayerBotRetireStallResult AdvancePlayerBotRetirementStall(LPCHARACTER ch,\n\t\tTPlayerBotAIState& state, TPlayerBotRetireEntry& entry, DWORD dwNow)\n{\n\tconst DWORD pid = ch->GetPlayerID();\n\n" + new_retire_6_v7 + "\n\n\t// 1. A town of the bot's own kingdom, with a stall ring, on this core.", "BOT_RETIREMENT_FIX_V7: gm=true")
        patch_file(f, old_retire_7, new_retire_7, "BOT_RETIREMENT_FIX_V6: only skip bot steering once")
        patch_file(f, old_retire_8, new_retire_8, "BOT_RETIREMENT_FIX_V6: only monitor the stall once the retirement listing was submitted")

    # 5. playerbot_offline_shop.h
    offline_files = [
        os.path.join(repo_root, "Server/linux-port/overlays/playerbot/src/game/src/playerbot_offline_shop.h"),
        os.path.join(repo_root, "Server/linux-port/docker/game/src/server/game/src/playerbot_offline_shop.h"),
    ]
    old_off_1 = """        const long long reservedGold = IsPlayerBotRetiring(ch->GetPlayerID()) ? 0 : (long long)GetPlayerBotReservedGold(ch);
        if (ch->GetGold() - aOfflineShopTime[duration].price < reservedGold ||
                !BotOfflineBudget(now) || !Begin(ch->GetPlayerID(), Create, 0, now)) return false;"""

    new_off_1 = """        const long long reservedGold = IsPlayerBotRetiring(ch->GetPlayerID()) ? 0 : (long long)GetPlayerBotReservedGold(ch);
        if (ch->GetGold() - aOfflineShopTime[duration].price < reservedGold ||
                (!IsPlayerBotRetiring(ch->GetPlayerID()) && !BotOfflineBudget(now)) ||
                !Begin(ch->GetPlayerID(), Create, 0, now)) return false; // MT2009_PLUS_BOT_RETIREMENT_FIX_V7"""

    for f in offline_files:
        patch_file(f, old_off_1, new_off_1, "BOT_RETIREMENT_FIX_V7")

    # 6. playerbot_manager.cpp
    target_files_manager = [
        os.path.join(repo_root, "Server/linux-port/overlays/playerbot/src/game/src/playerbot_manager.cpp"),
        os.path.join(repo_root, "Server/linux-port/docker/game/src/server/game/src/playerbot_manager.cpp"),
    ]

    # Target 1: RefreshPlayerBotRetireControl clear for new batch
    old_mgr_1 = """	s_dwPlayerBotRetireBatchId = batchId;
	s_dwPlayerBotRetireCount = count;
	s_dwPlayerBotRetireWindowMs = windowMinutes * 60000u;
	s_dwPlayerBotRetireShopMs = shopMinutes * 60000u;
	s_bPlayerBotRetireBatchResolved = false;
	s_bPlayerBotRetireBatchDone = false;
	s_uPlayerBotRetireBatchQueued = 0;
	s_uPlayerBotRetireRequeue = 0;
	s_dwPlayerBotRetireBatchWindowStart = dwNow;
	s_dwPlayerBotRetireNextPickTime = 0;"""

    new_mgr_1 = """	s_dwPlayerBotRetireBatchId = batchId;
	s_dwPlayerBotRetireCount = count;
	s_dwPlayerBotRetireWindowMs = windowMinutes * 60000u;
	s_dwPlayerBotRetireShopMs = shopMinutes * 60000u;
	s_bPlayerBotRetireBatchResolved = false;
	s_bPlayerBotRetireBatchDone = false;
	s_uPlayerBotRetireBatchQueued = 0;
	s_uPlayerBotRetireRequeue = 0;
	s_setPlayerBotRetireBatchPIDs.clear(); // MT2009_PLUS_BOT_RETIREMENT_FIX_V2
	s_dwPlayerBotRetireBatchWindowStart = dwNow;
	s_dwPlayerBotRetireNextPickTime = 0;"""

    # Target 2: TryScheduleRetirement batch resolved - load existing picks from DB
    old_mgr_2 = """	if (!s_bPlayerBotRetireBatchResolved)
	{
		s_bPlayerBotRetireBatchResolved = true;
		s_dwPlayerBotRetireBatchWindowStart = dwNow;
		s_uPlayerBotRetireRequeue = 0;

		AccountDB::instance().DirectQuery(
				"CREATE TABLE IF NOT EXISTS common.playerbot_retire_batch ("
				"id INT UNSIGNED NOT NULL PRIMARY KEY, "
				"queued_count INT UNSIGNED NOT NULL DEFAULT 0, "
				"started_at INT UNSIGNED NOT NULL)");
		EnsurePlayerBotRetirePickTable();

		char query[160];
		snprintf(query, sizeof(query),
				"SELECT queued_count FROM common.playerbot_retire_batch WHERE id=%u",
				s_dwPlayerBotRetireBatchId);
		std::unique_ptr<SQLMsg> batchMsg(AccountDB::instance().DirectQuery(query));
		if (batchMsg.get() && batchMsg->uiSQLErrno == 0 && batchMsg->Get() && batchMsg->Get()->pSQLResult)
		{
			MYSQL_ROW bRow = mysql_fetch_row(batchMsg->Get()->pSQLResult);
			if (bRow && bRow[0])
			{
				unsigned int q = 0;
				str_to_number(q, bRow[0]);
				s_uPlayerBotRetireBatchQueued = q;
			}
		}"""

    new_mgr_2 = """	if (!s_bPlayerBotRetireBatchResolved)
	{
		s_bPlayerBotRetireBatchResolved = true;
		s_dwPlayerBotRetireBatchWindowStart = dwNow;
		s_uPlayerBotRetireRequeue = 0;
		s_setPlayerBotRetireBatchPIDs.clear(); // MT2009_PLUS_BOT_RETIREMENT_FIX_V2

		AccountDB::instance().DirectQuery(
				"CREATE TABLE IF NOT EXISTS common.playerbot_retire_batch ("
				"id INT UNSIGNED NOT NULL PRIMARY KEY, "
				"queued_count INT UNSIGNED NOT NULL DEFAULT 0, "
				"started_at INT UNSIGNED NOT NULL)");
		EnsurePlayerBotRetirePickTable();

		// MT2009_PLUS_BOT_RETIREMENT_FIX_V2: load already picked bots for this batch
		{
			char queryBatchPicks[256];
			snprintf(queryBatchPicks, sizeof(queryBatchPicks),
					"SELECT pid FROM common.playerbot_retire_pick WHERE batch_id=%u",
					s_dwPlayerBotRetireBatchId);
			std::unique_ptr<SQLMsg> batchPicksMsg(AccountDB::instance().DirectQuery(queryBatchPicks));
			if (batchPicksMsg.get() && batchPicksMsg->uiSQLErrno == 0 && batchPicksMsg->Get() && batchPicksMsg->Get()->pSQLResult)
			{
				MYSQL_ROW bpRow;
				while (NULL != (bpRow = mysql_fetch_row(batchPicksMsg->Get()->pSQLResult)))
				{
					if (bpRow[0])
					{
						DWORD pid = 0;
						str_to_number(pid, bpRow[0]);
						if (pid > 0)
							s_setPlayerBotRetireBatchPIDs.insert(pid);
					}
				}
			}
		}

		char query[160];
		snprintf(query, sizeof(query),
				"SELECT queued_count FROM common.playerbot_retire_batch WHERE id=%u",
				s_dwPlayerBotRetireBatchId);
		std::unique_ptr<SQLMsg> batchMsg(AccountDB::instance().DirectQuery(query));
		if (batchMsg.get() && batchMsg->uiSQLErrno == 0 && batchMsg->Get() && batchMsg->Get()->pSQLResult)
		{
			MYSQL_ROW bRow = mysql_fetch_row(batchMsg->Get()->pSQLResult);
			if (bRow && bRow[0])
			{
				unsigned int q = 0;
				str_to_number(q, bRow[0]);
				s_uPlayerBotRetireBatchQueued = q;
			}
		}"""

    # Target 3: TryScheduleRetirement live bot candidate selection & minimum level
    old_mgr_3 = """	std::vector<std::pair<BYTE, DWORD> > live;
	for (TPlayerBotAccountMap::const_iterator it = m_mapBotAccounts.begin();
			it != m_mapBotAccounts.end(); ++it)
	{
		if (it->second.bChannel == g_bChannel && m_setScheduledBots.find(it->first) != m_setScheduledBots.end() &&
				!IsPlayerBotRetiring(it->first))
			live.push_back(std::make_pair(it->second.bLevel, it->first));
	}
	// Too small a world for "the middle" to mean anything.
	if (live.size() < 10)
	{
		s_dwPlayerBotRetireNextPickTime = dwNow + 60000;
		return;
	}
	std::sort(live.begin(), live.end());"""

    new_mgr_3 = """	// MT2009_PLUS_BOT_RETIREMENT_FIX_V2:
	// - Exclude bots already picked in this batch.
	// - Exclude bots below s_bPlayerBotRetireMinLevel (default 10) so newly spawned/reset bots
	//   do not pollute the percentile pool.
	// - Query real-time in-game level from LPCHARACTER and sync m_mapBotAccounts.
	std::vector<std::pair<BYTE, DWORD> > live;
	for (TPlayerBotAccountMap::const_iterator it = m_mapBotAccounts.begin();
			it != m_mapBotAccounts.end(); ++it)
	{
		if (it->second.bChannel != g_bChannel || m_setScheduledBots.find(it->first) == m_setScheduledBots.end() ||
				IsPlayerBotRetiring(it->first) ||
				s_setPlayerBotRetireBatchPIDs.find(it->first) != s_setPlayerBotRetireBatchPIDs.end())
			continue;
		LPCHARACTER ch = CHARACTER_MANAGER::instance().FindByPID(it->first);
		const BYTE level = ch ? (BYTE)ch->GetLevel() : it->second.bLevel;
		if (level < s_bPlayerBotRetireMinLevel)
			continue;
		if (ch && it->second.bLevel != level)
		{
			TPlayerBotAccountMap::iterator accIt = m_mapBotAccounts.find(it->first);
			if (accIt != m_mapBotAccounts.end())
				accIt->second.bLevel = level;
		}
		live.push_back(std::make_pair(level, it->first));
	}
	// Too small a world for "the middle" to mean anything.
	if (live.size() < 10)
	{
		s_dwPlayerBotRetireNextPickTime = dwNow + 60000;
		PlayerBotLogThrottled("retire_small_world", dwNow,
				"PLAYERBOT_RETIRE: only %u bots of level >= %u on this core, at least 10 are needed to pick",
				(unsigned int)live.size(), (unsigned int)s_bPlayerBotRetireMinLevel);
		return;
	}
	std::sort(live.begin(), live.end());"""

    # Target 4: bForcedPick guard against already-picked and level < min_level
    old_mgr_4 = """	bool bForcedPick = false;
	if (candidates.empty())
	{
		std::vector<DWORD> masters;
		for (size_t i = 0; i < live.size(); ++i)
		{
			const DWORD pid = live[i].second;
			if (m_mapBots.find(pid) == m_mapBots.end())
				continue;
			LPCHARACTER ch = CHARACTER_MANAGER::instance().FindByPID(pid);
			if (!ch || !ch->IsItemLoaded())
				continue;
			if (IsPlayerBotShouterPID(pid) || IsPlayerBotMedalShouterPID(pid) ||
					IsPlayerBotLegendTier(GetPlayerBotLegendTier(pid)) || GetPlayerBotLegendNameSlot(ch->GetName()) >= 0 ||
					IsPlayerBotSidekickPID(pid) || IsPlayerBotArezzoCohortPID(pid) ||
					IsPlayerBotArezzoDungeonCohortPID(pid) || IsPlayerBotTakeoverHold(pid))
				continue;
			CGuild* guild = ch->GetGuild();
			if (guild && guild->GetMasterPID() == pid)
				masters.push_back(pid);
			else
				candidates.push_back(pid);
		}
		if (candidates.empty())
			candidates.swap(masters);
		bForcedPick = !candidates.empty();
	}"""

    new_mgr_4 = """	bool bForcedPick = false;
	if (candidates.empty())
	{
		std::vector<DWORD> masters;
		for (size_t i = 0; i < live.size(); ++i)
		{
			const DWORD pid = live[i].second;
			// MT2009_PLUS_BOT_RETIREMENT_FIX_V2: never pick a bot already in this batch
			if (m_mapBots.find(pid) == m_mapBots.end() ||
					s_setPlayerBotRetireBatchPIDs.find(pid) != s_setPlayerBotRetireBatchPIDs.end())
				continue;
			LPCHARACTER ch = CHARACTER_MANAGER::instance().FindByPID(pid);
			if (!ch || !ch->IsItemLoaded())
				continue;
			if (ch->GetLevel() < s_bPlayerBotRetireMinLevel)
				continue;
			if (IsPlayerBotShouterPID(pid) || IsPlayerBotMedalShouterPID(pid) ||
					IsPlayerBotLegendTier(GetPlayerBotLegendTier(pid)) || GetPlayerBotLegendNameSlot(ch->GetName()) >= 0 ||
					IsPlayerBotSidekickPID(pid) || IsPlayerBotArezzoCohortPID(pid) ||
					IsPlayerBotArezzoDungeonCohortPID(pid) || IsPlayerBotTakeoverHold(pid))
				continue;
			if (ch->GetParty() && IsPlayerBotHumanLedParty(ch->GetParty()))
				continue;
			CGuild* guild = ch->GetGuild();
			if (guild && guild->GetMasterPID() == pid)
				masters.push_back(pid);
			else
				candidates.push_back(pid);
		}
		if (candidates.empty())
			candidates.swap(masters);
		bForcedPick = !candidates.empty();
	}
	if (candidates.empty())
	{
		// MT2009_PLUS_BOT_RETIREMENT_FIX_V4: If the allocated window has expired,
		// conclude the pick phase rather than retrying indefinitely every minute.
		const DWORD elapsed = dwNow - s_dwPlayerBotRetireBatchWindowStart;
		if (elapsed >= s_dwPlayerBotRetireWindowMs)
		{
			sys_log(0, "PLAYERBOT_RETIRE: batch id=%u window expired (%u ms elapsed, window %u ms), finishing pick phase with %u bots",
					s_dwPlayerBotRetireBatchId, (unsigned int)elapsed,
					(unsigned int)s_dwPlayerBotRetireWindowMs, (unsigned int)s_uPlayerBotRetireBatchQueued);
			s_bPlayerBotRetireBatchDone = true;
			s_dwPlayerBotRetireCount = s_uPlayerBotRetireBatchQueued;
			char syncControl[256];
			snprintf(syncControl, sizeof(syncControl),
					"UPDATE common.playerbot_retire_control SET bot_count=%u WHERE id=1 AND batch_id=%u",
					(unsigned int)s_uPlayerBotRetireBatchQueued, s_dwPlayerBotRetireBatchId);
			AccountDB::instance().AsyncQuery(syncControl);
			return;
		}

		s_dwPlayerBotRetireNextPickTime = dwNow + 60000;"""

    # Target 5: RecordPlayerBotRetirePick insert dwPID into s_setPlayerBotRetireBatchPIDs
    old_mgr_5 = """	TPlayerBotRetireEntry entry;
	entry.dwBatchId = s_dwPlayerBotRetireBatchId;
	entry.dwPickedAt = dwNow;
	entry.dwLastSeen = dwNow;
	s_mapPlayerBotRetiring[dwPID] = entry;"""

    new_mgr_5 = """	s_setPlayerBotRetireBatchPIDs.insert(dwPID); // MT2009_PLUS_BOT_RETIREMENT_FIX_V2
	TPlayerBotRetireEntry entry;
	entry.dwBatchId = s_dwPlayerBotRetireBatchId;
	entry.dwPickedAt = dwNow;
	entry.dwLastSeen = dwNow;
	s_mapPlayerBotRetiring[dwPID] = entry;"""

    # Target 6: don't wipe forced pick if shop stands (V4 / V6)
    old_mgr_6 = """	// MT2009_PLUS_BOT_RETIREMENT_FORCE_V1: a forced pick sells nothing - its game
	// ends at once (wiped and logged out by ProcessRetirementResets).
	if (bForcedPick)
		BeginPlayerBotRetirementClose(dwPID, s_mapPlayerBotRetiring[dwPID], "forced: no bot could go to a market");"""

    old_mgr_6_v4 = """	// MT2009_PLUS_BOT_RETIREMENT_FIX_V4: If the bot already has an offline shop standing,
	// let MonitorPlayerBotRetirementStall monitor its sales instead of immediately wiping it.
	if (bForcedPick && !ikashop::GetManager().GetShopByOwnerID(dwPID))
	{
		CGuild* pGuild = pickedCh->GetGuild();
		if (pGuild && pGuild->GetMasterPID() == dwPID)
			BeginPlayerBotRetirementClose(dwPID, s_mapPlayerBotRetiring[dwPID], "forced: guild master");
	}"""

    new_mgr_6 = """	// MT2009_PLUS_BOT_RETIREMENT_FIX_V6:
	// Guild master cannot open retirement stall, close immediately;
	// All other bots (including forced picks) proceed to AdvancePlayerBotRetirementStall to sell their worn gear.
	if (bForcedPick)
	{
		CGuild* pGuild = pickedCh->GetGuild();
		if (pGuild && pGuild->GetMasterPID() == dwPID)
			BeginPlayerBotRetirementClose(dwPID, s_mapPlayerBotRetiring[dwPID], "forced: guild master");
	}"""

    for f in target_files_manager:
        patch_file(f, old_mgr_1, new_mgr_1, "s_setPlayerBotRetireBatchPIDs.clear()")
        patch_file(f, old_mgr_2, new_mgr_2, "SELECT pid FROM common.playerbot_retire_pick WHERE batch_id=")
        patch_file(f, old_mgr_3, new_mgr_3, "level < s_bPlayerBotRetireMinLevel")
        patch_file(f, old_mgr_4, new_mgr_4, "conclude the pick phase rather than retrying indefinitely every minute")
        patch_file(f, old_mgr_5, new_mgr_5, "s_setPlayerBotRetireBatchPIDs.insert(dwPID); // MT2009_PLUS_BOT_RETIREMENT_FIX_V2")
        if not patch_file(f, old_mgr_6_v4, new_mgr_6, "BOT_RETIREMENT_FIX_V6:"):
            patch_file(f, old_mgr_6, new_mgr_6, "BOT_RETIREMENT_FIX_V6:")

    print("Wszystkie pliki zostały pomyślnie zaktualizowane do Fix V7!")

if __name__ == "__main__":
    main()
