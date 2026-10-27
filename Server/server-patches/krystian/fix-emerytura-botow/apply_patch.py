#!/usr/bin/env python3
"""
Patch: fix-emerytura-botow (MT2009_PLUS_BOT_RETIREMENT_FIX_V2)
Naprawa zapętlenia losowania emerytury botów oraz losowania postaci o poziomie 1.
"""
import os
import sys

def patch_file(path, old_text, new_text):
    if not os.path.exists(path):
        print(f"BŁĄD: Plik {path} nie istnieje!")
        return False
    with open(path, "rb") as f:
        content = f.read()
    
    # Try with raw bytes (handling \r\n vs \n)
    old_bytes = old_text.encode("utf-8")
    new_bytes = new_text.encode("utf-8")
    
    # Normalize CRLF to LF for comparison if needed
    if old_bytes not in content:
        old_bytes_crlf = old_text.replace("\n", "\r\n").encode("utf-8")
        new_bytes_crlf = new_text.replace("\n", "\r\n").encode("utf-8")
        if old_bytes_crlf in content:
            content = content.replace(old_bytes_crlf, new_bytes_crlf, 1)
        else:
            old_bytes_lf = old_text.replace("\r\n", "\n").encode("utf-8")
            new_bytes_lf = new_text.replace("\r\n", "\n").encode("utf-8")
            if old_bytes_lf in content:
                content = content.replace(old_bytes_lf, new_bytes_lf, 1)
            else:
                print(f"BŁĄD: Nie znaleziono wzorca w {path}!")
                return False
    else:
        content = content.replace(old_bytes, new_bytes, 1)
    
    with open(path, "wb") as f:
        f.write(content)
    print(f"Pomyślnie zmodyfikowano: {path}")
    return True

def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
    print(f"Katalog repozytorium: {repo_root}")

    # 1. playerbot_retirement.h
    target_files_retire = [
        os.path.join(repo_root, "Server/linux-port/overlays/playerbot/src/game/src/playerbot_retirement.h"),
        os.path.join(repo_root, "Server/linux-port/docker/game/src/server/game/src/playerbot_retirement.h"),
    ]

    # Target 1: config & variables
    old_retire_1 = """DWORD s_dwPlayerBotRetireCount = 0;
DWORD s_dwPlayerBotRetireBatchId = 0;
DWORD s_dwPlayerBotRetireWindowMs = 24u * 3600000u;
DWORD s_dwPlayerBotRetireShopMs = 3600000u;
bool  s_bPlayerBotRetireConfigLoaded = false;

// A pick that could not be carried out (no stall in 30 minutes, or the bot
// never logged in) is called off; the scheduler gives its place to another bot.
size_t s_uPlayerBotRetireRequeue = 0;

void LoadPlayerBotRetireConfig()
{
	if (s_bPlayerBotRetireConfigLoaded)
		return;
	s_bPlayerBotRetireConfigLoaded = true;

	const char* count = std::getenv("PLAYERBOT_RETIRE_COUNT");
	if (count && *count)
	{
		int v = std::atoi(count);
		s_dwPlayerBotRetireCount = (DWORD)std::max(0, v);
	}
	const char* batchId = std::getenv("PLAYERBOT_RETIRE_BATCH_ID");
	if (batchId && *batchId)
	{
		int v = std::atoi(batchId);
		s_dwPlayerBotRetireBatchId = (DWORD)std::max(0, v);
	}
	const char* windowHours = std::getenv("PLAYERBOT_RETIRE_WINDOW_HOURS");
	const char* windowMinutes = std::getenv("PLAYERBOT_RETIRE_WINDOW_MINUTES");
	if (windowMinutes && *windowMinutes)
	{
		int m = std::atoi(windowMinutes);
		if (m > 0)
			s_dwPlayerBotRetireWindowMs = (DWORD)std::min<long long>(
					(long long)m * 60000LL, 7LL * 24LL * 3600000LL);
	}
	else if (windowHours && *windowHours)
	{
		int h = std::atoi(windowHours);
		if (h > 0)
			s_dwPlayerBotRetireWindowMs = (DWORD)h * 3600000u;
	}
	const char* shopHours = std::getenv("PLAYERBOT_RETIRE_SHOP_HOURS");
	const char* shopMinutes = std::getenv("PLAYERBOT_RETIRE_SHOP_MINUTES");
	if (shopMinutes && *shopMinutes)
	{
		int m = std::atoi(shopMinutes);
		if (m > 0)
			s_dwPlayerBotRetireShopMs = (DWORD)std::min<long long>(
					(long long)m * 60000LL, 7LL * 24LL * 3600000LL);
	}
	else if (shopHours && *shopHours)
	{
		int h = std::atoi(shopHours);
		if (h > 0)
			s_dwPlayerBotRetireShopMs = (DWORD)h * 3600000u;
	}
	sys_log(0, "PLAYERBOT_RETIRE: count=%u batch_id=%u window_minutes=%u shop_minutes=%u",
			(unsigned int)s_dwPlayerBotRetireCount, (unsigned int)s_dwPlayerBotRetireBatchId,
			(unsigned int)(s_dwPlayerBotRetireWindowMs / 60000u),
			(unsigned int)(s_dwPlayerBotRetireShopMs / 60000u));
}"""

    new_retire_1 = """DWORD s_dwPlayerBotRetireCount = 0;
DWORD s_dwPlayerBotRetireBatchId = 0;
DWORD s_dwPlayerBotRetireWindowMs = 24u * 3600000u;
DWORD s_dwPlayerBotRetireShopMs = 3600000u;
BYTE  s_bPlayerBotRetireMinLevel = 10; // MT2009_PLUS_BOT_RETIREMENT_FIX_V2: minimum level to be eligible for retirement
bool  s_bPlayerBotRetireConfigLoaded = false;

// MT2009_PLUS_BOT_RETIREMENT_FIX_V2: track bots already picked in the active batch
// so a bot can never be picked more than once in the same batch.
std::set<DWORD> s_setPlayerBotRetireBatchPIDs;

// A pick that could not be carried out (no stall in 30 minutes, or the bot
// never logged in) is called off; the scheduler gives its place to another bot.
size_t s_uPlayerBotRetireRequeue = 0;

void LoadPlayerBotRetireConfig()
{
	if (s_bPlayerBotRetireConfigLoaded)
		return;
	s_bPlayerBotRetireConfigLoaded = true;

	const char* count = std::getenv("PLAYERBOT_RETIRE_COUNT");
	if (count && *count)
	{
		int v = std::atoi(count);
		s_dwPlayerBotRetireCount = (DWORD)std::max(0, v);
	}
	const char* batchId = std::getenv("PLAYERBOT_RETIRE_BATCH_ID");
	if (batchId && *batchId)
	{
		int v = std::atoi(batchId);
		s_dwPlayerBotRetireBatchId = (DWORD)std::max(0, v);
	}
	const char* windowHours = std::getenv("PLAYERBOT_RETIRE_WINDOW_HOURS");
	const char* windowMinutes = std::getenv("PLAYERBOT_RETIRE_WINDOW_MINUTES");
	if (windowMinutes && *windowMinutes)
	{
		int m = std::atoi(windowMinutes);
		if (m > 0)
			s_dwPlayerBotRetireWindowMs = (DWORD)std::min<long long>(
					(long long)m * 60000LL, 7LL * 24LL * 3600000LL);
	}
	else if (windowHours && *windowHours)
	{
		int h = std::atoi(windowHours);
		if (h > 0)
			s_dwPlayerBotRetireWindowMs = (DWORD)h * 3600000u;
	}
	const char* shopHours = std::getenv("PLAYERBOT_RETIRE_SHOP_HOURS");
	const char* shopMinutes = std::getenv("PLAYERBOT_RETIRE_SHOP_MINUTES");
	if (shopMinutes && *shopMinutes)
	{
		int m = std::atoi(shopMinutes);
		if (m > 0)
			s_dwPlayerBotRetireShopMs = (DWORD)std::min<long long>(
					(long long)m * 60000LL, 7LL * 24LL * 3600000LL);
	}
	else if (shopHours && *shopHours)
	{
		int h = std::atoi(shopHours);
		if (h > 0)
			s_dwPlayerBotRetireShopMs = (DWORD)h * 3600000u;
	}
	const char* minLevel = std::getenv("PLAYERBOT_RETIRE_MIN_LEVEL");
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

    # Target 4: IsPlayerBotRetirementCandidateInner
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

    for f in target_files_retire:
        if not patch_file(f, old_retire_1, new_retire_1):
            sys.exit(1)
        if not patch_file(f, old_retire_2, new_retire_2):
            sys.exit(1)
        if not patch_file(f, old_retire_3, new_retire_3):
            sys.exit(1)
        if not patch_file(f, old_retire_4, new_retire_4):
            sys.exit(1)

    # 2. playerbot_manager.cpp
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
		EnsurePlayerBotRetirePickTable();"""

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
					DWORD bpPid = 0;
					if (bpRow[0])
						str_to_number(bpPid, bpRow[0]);
					if (bpPid != 0)
						s_setPlayerBotRetireBatchPIDs.insert(bpPid);
				}
			}
		}"""

    # Target 3: TryScheduleRetirement building live
    old_mgr_3 = """	// The level table, all active bots on both channels, by level. "The middle"
	// is the 35th to the 65th percentile of it: not the best, not the worst.
	std::vector<std::pair<BYTE, DWORD> > live;
	for (TPlayerBotAccountMap::const_iterator it = m_mapBotAccounts.begin();
			it != m_mapBotAccounts.end(); ++it)
	{
		// "Active" = in this core's world: since 2.0.84 (upstream's second channel) the account map
		// has no bActive, and only this channel's scheduled bots can be picked anyway.
		if (it->second.bChannel != g_bChannel || m_setScheduledBots.find(it->first) == m_setScheduledBots.end() ||
				IsPlayerBotRetiring(it->first))
			continue;
		live.push_back(std::make_pair(it->second.bLevel, it->first));
	}
	// Too small a world for "the middle" to mean anything.
	if (live.size() < 10)
	{
		s_dwPlayerBotRetireNextPickTime = dwNow + 60000;
		PlayerBotLogThrottled("retire_small_world", dwNow,
				"PLAYERBOT_RETIRE: only %u bots on this core, at least 10 are needed to pick",
				(unsigned int)live.size());
		return;
	}
	std::sort(live.begin(), live.end());"""

    new_mgr_3 = """	// The level table, all active bots on this core, by level. "The middle"
	// is the 35th to the 65th percentile of it: not the best, not the worst.
	// MT2009_PLUS_BOT_RETIREMENT_FIX_V2:
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

    for f in target_files_manager:
        if not patch_file(f, old_mgr_1, new_mgr_1):
            sys.exit(1)
        if not patch_file(f, old_mgr_2, new_mgr_2):
            sys.exit(1)
        if not patch_file(f, old_mgr_3, new_mgr_3):
            sys.exit(1)
        if not patch_file(f, old_mgr_4, new_mgr_4):
            sys.exit(1)
        if not patch_file(f, old_mgr_5, new_mgr_5):
            sys.exit(1)

    print("Wszystkie pliki zostały pomyślnie zaktualizowane!")

if __name__ == "__main__":
    main()
