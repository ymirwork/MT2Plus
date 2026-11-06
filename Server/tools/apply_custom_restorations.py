#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_custom_restorations.py - Restores all custom MT2Plus modifications to playerbot files
after upstream v2.41.0 sync.
"""
import os
import sys
import shutil

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OVERLAYS_DIR = os.path.join(REPO, 'Server/linux-port/overlays/playerbot/src/game/src')
DOCKER_DIR = os.path.join(REPO, 'Server/linux-port/docker/game/src/server/game/src')

def patch_file(filepath, replacements):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    newline = '\r\n' if '\r\n' in content else '\n'

    for target, replacement in replacements:
        target_norm = target.replace('\r\n', '\n')
        replacement_norm = replacement.replace('\r\n', '\n')

        # Check if already present
        if replacement_norm in content.replace('\r\n', '\n'):
            print(f"  [ALREADY PRESENT] in {os.path.basename(filepath)}")
            continue

        content_lf = content.replace('\r\n', '\n')
        if target_norm not in content_lf:
            raise RuntimeError(f"Target not found in {filepath}:\n{target_norm[:150]}...")

        content_lf = content_lf.replace(target_norm, replacement_norm, 1)
        if newline == '\r\n':
            content = content_lf.replace('\n', '\r\n')
        else:
            content = content_lf
        print(f"  [APPLIED] replacement in {os.path.basename(filepath)}")

    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        f.write(content)

def main():
    print("=== Restoring Custom Playerbot Overlays ===")

    # 1. playerbot_town.h
    print("\n1. Patching playerbot_town.h...")
    town_path = os.path.join(OVERLAYS_DIR, 'playerbot_town.h')
    with open(town_path, 'r', encoding='utf-8', errors='ignore') as f:
        town_c = f.read()
    if '#include "playerbot_custom_prices.h"' not in town_c:
        town_c = '#include "playerbot_custom_prices.h"\n' + town_c
        with open(town_path, 'w', encoding='utf-8', newline='') as f:
            f.write(town_c)
        print("  [APPLIED] #include \"playerbot_custom_prices.h\"")

    town_replacements = [
        # Book price
        (
            """DWORD GetPlayerBotBookAskingBase(DWORD dwSkill)
	{
		DWORD base = PLAYERBOT_PRIOR_BOOK_ORDINARY;""",
            """DWORD GetPlayerBotBookAskingBase(DWORD dwSkill)
	{
		const DWORD custom = playerbot_custom_prices::GetCustomSkillPrice(dwSkill);
		if (custom > 0)
			return ScalePlayerBotIwakuraPrice(custom);
		DWORD base = PLAYERBOT_PRIOR_BOOK_ORDINARY;"""
        ),
        # Material price
        (
            """DWORD GetPlayerBotMaterialAskingBase(DWORD dwVnum)
	{
		// The guild building materials at the operator's price""",
            """DWORD GetPlayerBotMaterialAskingBase(DWORD dwVnum)
	{
		const DWORD custom = playerbot_custom_prices::GetCustomItemPrice(dwVnum);
		if (custom > 0)
			return ScalePlayerBotIwakuraPrice(custom);
		// The guild building materials at the operator's price"""
        ),
        # Soul stone price
        (
            """DWORD GetPlayerBotSoulStoneAskingBase(DWORD dwVnum)
	{
		const int kind = GetPlayerBotSoulStoneKind(dwVnum);""",
            """DWORD GetPlayerBotSoulStoneAskingBase(DWORD dwVnum)
	{
		const DWORD custom = playerbot_custom_prices::GetCustomItemPrice(dwVnum);
		if (custom > 0)
			return ScalePlayerBotIwakuraPrice(custom);
		const int kind = GetPlayerBotSoulStoneKind(dwVnum);"""
        ),
        # Group unit worth
        (
            """		if (dwVnum <= (DWORD)CSpecialItemGroup::MOB_GROUP)
			return 0;
		const TItemTable* proto = ITEM_MANAGER::instance().GetTable(dwVnum);""",
            """		if (dwVnum <= (DWORD)CSpecialItemGroup::MOB_GROUP)
			return 0;
		const DWORD custom = playerbot_custom_prices::GetCustomItemPrice(dwVnum);
		if (custom > 0)
			return ScalePlayerBotIwakuraPrice(custom);
		const TItemTable* proto = ITEM_MANAGER::instance().GetTable(dwVnum);"""
        ),
        # Green tradeable bonus check
        (
            """		if (IsPlayerBotTradeableBonusVnum(item->GetVnum()))
			return playerbot_stall_rules::HoldsSpare(CountPlayerBotVnumUnitsAhead(ch, item),
					(int)item->GetCount(), GetPlayerBotCountedGoodsKeep(ch, item))
					? PlayerBotGoods(PLAYERBOT_SHOP_RARE_GOODS_SCORE, per::GOODS_RARE_GOODS) : -1;""",
            """		if (IsPlayerBotTradeableBonusVnum(item->GetVnum()) || IsPlayerBotGreenTradeableBonusVnum(item->GetVnum()))
			return playerbot_stall_rules::HoldsSpare(CountPlayerBotVnumUnitsAhead(ch, item),
					(int)item->GetCount(), GetPlayerBotCountedGoodsKeep(ch, item))
					? PlayerBotGoods(PLAYERBOT_SHOP_RARE_GOODS_SCORE, per::GOODS_RARE_GOODS) : -1;"""
        )
    ]
    patch_file(town_path, town_replacements)

    # 2. playerbot_economy.h
    print("\n2. Patching playerbot_economy.h...")
    econ_replacements = [
        # PlayerBotScrapLevel30ForMerchant helper
        (
            """	bool IsPlayerBotJunkItem(LPCHARACTER ch, LPITEM item)
	{
		if (!ch || !item || item->IsEquipped() || item->isLocked())""",
            """	// MT2009_PLUS_HARDCORE_L30_RECYCLE_V1:
	// Decide whether a level-30 weapon is scrap for the General Store merchant.
	// On a hard server, weapons with low/negative average damage (<= 10%) or excessive
	// surplus copies when the bag is getting full are vendored for pocket money,
	// exactly like human players do on savage minions / bestials.
	bool PlayerBotScrapLevel30ForMerchant(LPCHARACTER ch, LPITEM item)
	{
		if (!ch || !item || !IsPlayerBotSpecialLevel30Weapon(item) || item->IsEquipped() || item->isLocked())
			return false;
		if (IsPlayerBotHighValueLevel30(item))
			return false;
		if (item == FindPlayerBotClassLevel30Weapon(ch) || IsPlayerBotLevel30Project(ch, item) ||
				IsPlayerBotSashGrailProject(ch, item) || PlayerBotKeepsLevel30ForAnvil(ch, item) ||
				IsPlayerBotLottery30Piece(ch, item))
			return false;

		const long avg = SumPlayerBotItemLines(item, APPLY_NORMAL_HIT_DAMAGE_BONUS);
		const BYTE plus = item->GetRefineLevel();

		// Negative or very weak average damage (<= 10%) at +0..+3 is pure scrap
		if (avg <= 10 && plus <= 3)
			return true;

		// When bag has multiple copies ahead, or bag is under pressure, surplus is scrap
		if (plus <= 3 && (CountPlayerBotVnumUnitsAhead(ch, item) >= 1 || IsPlayerBotBagUnderPressure(ch)))
			return true;

		return false;
	}

	bool IsPlayerBotJunkItem(LPCHARACTER ch, LPITEM item)
	{
		if (!ch || !item || item->IsEquipped() || item->isLocked())"""
        ),
        # L30 junk check in IsPlayerBotJunkItem
        (
            """		// Level-30 weapons with average/skill damage are strategic market assets.
		// Never vendor them: this also applies when the current owner is below level
		// 30 or belongs to another class. They remain available for future playerbot
		// trading/private shops instead of disappearing for a trivial NPC price.
		if (IsPlayerBotSpecialLevel30Weapon(item))
			return false;""",
            """		// MT2009_PLUS_HARDCORE_L30_RECYCLE_V1:
		// Level-30 weapons with high average/skill damage (>= 25% avg or >= 8% skill)
		// are strategic market assets. Never vendor them.
		// Surplus scrap (negative/low avg, or surplus copies filling the bag)
		// is sold at the merchant when the bot already has enough copies or bag is full.
		if (IsPlayerBotSpecialLevel30Weapon(item))
		{
			if (IsPlayerBotHighValueLevel30(item))
				return false;
			if (PlayerBotScrapLevel30ForMerchant(ch, item))
				return true;
			return false;
		}"""
        ),
        # OnPlayerBotLottery30Refined declaration
        (
            """	// MT2009_PLUS_UPSTREAM_BOTLOGIC_LOTTERY30_V1 (playerbot_upstream_botlogic.h).
	bool TryPickPlayerBotLottery30(LPCHARACTER ch, LPITEM item);

	bool ManagePlayerBotRefining(LPCHARACTER ch, TPlayerBotAIState& state, DWORD dwNow)""",
            """	// MT2009_PLUS_UPSTREAM_BOTLOGIC_LOTTERY30_V1 (playerbot_upstream_botlogic.h).
	bool TryPickPlayerBotLottery30(LPCHARACTER ch, LPITEM item);
	void OnPlayerBotLottery30Refined(LPCHARACTER ch, DWORD dwOldId, LPITEM pkItemAfter);

	bool ManagePlayerBotRefining(LPCHARACTER ch, TPlayerBotAIState& state, DWORD dwNow)"""
        ),
        # OnPlayerBotLottery30Refined call in ManagePlayerBotRefining
        (
            """			if (attempted)
			{
				// The step's fee goes on the level-30 weapon's budget.""",
            """			// MT2009_PLUS_UPSTREAM_BOTLOGIC_LOTTERY30_V1: track the lottery piece across upgrades
			// so the bot continues refining the same weapon instead of abandoning it at +1.
			if (attempted)
				OnPlayerBotLottery30Refined(ch, idBefore, ch->GetInventoryItem(cellBefore));
			if (attempted)
			{
				// The step's fee goes on the level-30 weapon's budget."""
        )
    ]
    patch_file(os.path.join(OVERLAYS_DIR, 'playerbot_economy.h'), econ_replacements)

    # 3. playerbot_offline_shop.h
    print("\n3. Patching playerbot_offline_shop.h...")
    shop_replacements = [
        # Forward declare IsPlayerBotRetiring
        (
            """namespace {
    using NativeShop = ikashop::CShopManager::SHOP_HANDLE;""",
            """namespace {
    bool IsPlayerBotRetiring(DWORD dwPlayerID);
    using NativeShop = ikashop::CShopManager::SHOP_HANDLE;"""
        ),
        # Retiring bot bypasses 120s spawn delay and reserved gold
        (
            """        if (now - state.dwSpawnTime < 120000) return false;
        if (ch->GetGold() - aOfflineShopTime[duration].price < GetPlayerBotReservedGold(ch) ||
                !BotOfflineBudget(now) || !Begin(ch->GetPlayerID(), Create, 0, now)) return false;""",
            """        if (!IsPlayerBotRetiring(ch->GetPlayerID()) && now - state.dwSpawnTime < 120000) return false;
        const long long reservedGold = IsPlayerBotRetiring(ch->GetPlayerID()) ? 0 : (long long)GetPlayerBotReservedGold(ch);
        if (ch->GetGold() - aOfflineShopTime[duration].price < reservedGold ||
                !BotOfflineBudget(now) || !Begin(ch->GetPlayerID(), Create, 0, now)) return false;"""
        ),
        # Bot shop reopening ignores player premium slots check
        (
            """                for (const auto& [lineId, line] : shop->GetItems())
                    if (line && line->GetTable() &&
                            !ch->CanPlaceItemOnShopSlot((BYTE)line->GetInfo().pos, (BYTE)line->GetTable()->bSize)) {""",
            """                for (const auto& [lineId, line] : shop->GetItems())
                    if (line && line->GetTable() &&
                            !(ch->GetDesc() && ch->GetDesc()->IsBot()) && !ch->CanPlaceItemOnShopSlot((BYTE)line->GetInfo().pos, (BYTE)line->GetTable()->bSize)) {"""
        )
    ]
    patch_file(os.path.join(OVERLAYS_DIR, 'playerbot_offline_shop.h'), shop_replacements)

    # 4. playerbot_manager.cpp
    print("\n4. Patching playerbot_manager.cpp...")
    mgr_replacements = [
        # Reload custom prices in LoadRegisteredBots
        (
            """	LoadPlayerBotSidekicks();
	s_dwPlayerBotSidekickNextLoad = get_dword_time() + PLAYERBOT_SIDEKICK_RELOAD_MS;

	// The second channel's plan""",
            """	LoadPlayerBotSidekicks();
	s_dwPlayerBotSidekickNextLoad = get_dword_time() + PLAYERBOT_SIDEKICK_RELOAD_MS;
	playerbot_custom_prices::Reload();

	// The second channel's plan"""
        ),
        # RefreshPlayerBotRetireControl clear
        (
            """	s_bPlayerBotRetireBatchDone = false;
	s_uPlayerBotRetireBatchQueued = 0;
	s_uPlayerBotRetireRequeue = 0;
	s_dwPlayerBotRetireBatchWindowStart = dwNow;""",
            """	s_bPlayerBotRetireBatchDone = false;
	s_uPlayerBotRetireBatchQueued = 0;
	s_uPlayerBotRetireRequeue = 0;
	s_setPlayerBotRetireBatchPIDs.clear(); // MT2009_PLUS_BOT_RETIREMENT_FIX_V2
	s_dwPlayerBotRetireBatchWindowStart = dwNow;"""
        ),
        # TryScheduleRetirement batch resolved - load existing picks from DB
        (
            """	if (!s_bPlayerBotRetireBatchResolved)
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

		char query[160];""",
            """	if (!s_bPlayerBotRetireBatchResolved)
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
		}

		char query[160];"""
        ),
        # Live vector building with level sync and min level guard
        (
            """	std::vector<std::pair<BYTE, DWORD> > live;
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
	}""",
            """	std::vector<std::pair<BYTE, DWORD> > live;
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
	}"""
        ),
        # bForcedPick candidates with already-picked guard and human-led party check
        (
            """		for (size_t i = 0; i < live.size(); ++i)
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
		}""",
            """		for (size_t i = 0; i < live.size(); ++i)
		{
			const DWORD pid = live[i].second;
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
			if (HasPlayerBotOfflineShop(ch))
				continue;
			if (ch->GetParty() && IsPlayerBotHumanLedParty(ch->GetParty()))
				continue;
			CGuild* guild = ch->GetGuild();
			if (guild && guild->GetMasterPID() == pid)
				masters.push_back(pid);
			else
				candidates.push_back(pid);
		}"""
        ),
        # RecordPlayerBotRetirePick insert dwPID into s_setPlayerBotRetireBatchPIDs
        (
            """	TPlayerBotRetireEntry entry;
	entry.dwBatchId = s_dwPlayerBotRetireBatchId;
	entry.dwPickedAt = dwNow;
	entry.dwLastSeen = dwNow;
	s_mapPlayerBotRetiring[dwPID] = entry;""",
            """	s_setPlayerBotRetireBatchPIDs.insert(dwPID); // MT2009_PLUS_BOT_RETIREMENT_FIX_V2
	TPlayerBotRetireEntry entry;
	entry.dwBatchId = s_dwPlayerBotRetireBatchId;
	entry.dwPickedAt = dwNow;
	entry.dwLastSeen = dwNow;
	s_mapPlayerBotRetiring[dwPID] = entry;"""
        ),
        # MT2009_PLUS_BOT_RETIREMENT_FIX_V4: allow retiring bots with active shops and window timeout
        (
            """		if (candidates.empty())
			candidates.swap(masters);
		bForcedPick = !candidates.empty();
	}
	if (candidates.empty())
	{
		s_dwPlayerBotRetireNextPickTime = dwNow + 60000;""",
            """		if (candidates.empty())
			candidates.swap(masters);
		if (candidates.empty())
		{
			// MT2009_PLUS_BOT_RETIREMENT_FIX_V4: If almost all bots have active offline shops,
			// allow retiring bots that already keep a stall. Their existing shop will serve as
			// their retirement stall (monitored by MonitorPlayerBotRetirementStall).
			for (size_t i = 0; i < live.size(); ++i)
			{
				const DWORD pid = live[i].second;
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
					continue;
				candidates.push_back(pid);
			}
		}
		bForcedPick = !candidates.empty();
	}
	if (candidates.empty())
	{
		// MT2009_PLUS_BOT_RETIREMENT_FIX_V4: If the allocated window has expired,
		// conclude the pick phase rather than retrying indefinitely every minute.
		const DWORD elapsed = dwNow - s_dwPlayerBotRetireBatchWindowStart;
		if (elapsed >= s_dwPlayerBotRetireWindowMs)
		{
			sys_log(0, \"PLAYERBOT_RETIRE: batch id=%u window expired (%u ms elapsed, window %u ms), finishing pick phase with %u bots\",
					s_dwPlayerBotRetireBatchId, (unsigned int)elapsed,
					(unsigned int)s_dwPlayerBotRetireWindowMs, (unsigned int)s_uPlayerBotRetireBatchQueued);
			s_bPlayerBotRetireBatchDone = true;
			s_dwPlayerBotRetireCount = s_uPlayerBotRetireBatchQueued;
			char syncControl[256];
			snprintf(syncControl, sizeof(syncControl),
					\"UPDATE common.playerbot_retire_control SET bot_count=%u WHERE id=1 AND batch_id=%u\",
					(unsigned int)s_uPlayerBotRetireBatchQueued, s_dwPlayerBotRetireBatchId);
			AccountDB::instance().AsyncQuery(syncControl);
			return;
		}

		s_dwPlayerBotRetireNextPickTime = dwNow + 60000;"""
        ),
        # MT2009_PLUS_BOT_RETIREMENT_FIX_V4: don't wipe forced pick if shop stands
        (
            """	// MT2009_PLUS_BOT_RETIREMENT_FORCE_V1: a forced pick sells nothing - its game
	// ends at once (wiped and logged out by ProcessRetirementResets).
	if (bForcedPick)
		BeginPlayerBotRetirementClose(dwPID, s_mapPlayerBotRetiring[dwPID], \"forced: no bot could go to a market\");""",
            """	// MT2009_PLUS_BOT_RETIREMENT_FIX_V4: If the bot already has an offline shop standing,
	// let MonitorPlayerBotRetirementStall monitor its sales instead of immediately wiping it.
	if (bForcedPick && !ikashop::GetManager().GetShopByOwnerID(dwPID))
	{
		CGuild* pGuild = pickedCh->GetGuild();
		if (pGuild && pGuild->GetMasterPID() == dwPID)
			BeginPlayerBotRetirementClose(dwPID, s_mapPlayerBotRetiring[dwPID], \"forced: guild master\");
	}"""
        )
    ]
    mgr_path = os.path.join(OVERLAYS_DIR, 'playerbot_manager.cpp')
    patch_file(mgr_path, mgr_replacements)

    # Append IsHumanTargetReachable if missing
    with open(mgr_path, 'r', encoding='utf-8') as f:
        mgr_txt = f.read()
    if 'IsHumanTargetReachable' not in mgr_txt:
        reachable_block = """

// MT2009_PLUS_REACHABLE_TARGET_V1: Target reachable check for bots in DT and dungeons
bool CPlayerBotManager::IsHumanTargetReachable(LPCHARACTER ch, long targetX, long targetY)
{
	if (!ch)
		return false;
	const long lMapIndex = ch->GetMapIndex();
	if (GetHumanPathKind(lMapIndex) == 0)
		return true;

	const long base = lMapIndex >= PLAYERBOT_INSTANCE_MAP_INDEX_MIN ? lMapIndex / 10000 : lMapIndex;
	CPlayerBotNavigation& navigation = CPlayerBotNavigation::instance(base);
	if (!navigation.Init(base))
		return true;

	const DWORD chComp = navigation.GetComponentAtWorld(ch->GetX(), ch->GetY(), 2);
	const DWORD targetComp = navigation.GetComponentAtWorld(targetX, targetY, 2);
	if (chComp != 0 && targetComp != 0 && chComp != targetComp)
		return false;

	return true;
}
"""
        mgr_txt = mgr_txt.rstrip() + reachable_block
        with open(mgr_path, 'w', encoding='utf-8', newline='') as f:
            f.write(mgr_txt)
        print("  [APPLIED] IsHumanTargetReachable to playerbot_manager.cpp")

    # 5. playerbot_gear.h
    print("\n5. Patching playerbot_gear.h...")
    gear_replacements = [
        (
            """	bool IsPlayerBotL30WeaponSeller(LPCHARACTER ch)
	{
		return ch && GetPlayerBotPersonalityByPID(ch->GetPlayerID()) == BOT_PERSONALITY_L30_WEAPON_DROPPER;
	}""",
            """	bool IsPlayerBotL30WeaponSeller(LPCHARACTER ch)
	{
		return ch && GetPlayerBotPersonalityByPID(ch->GetPlayerID()) == BOT_PERSONALITY_L30_WEAPON_DROPPER;
	}

	// MT2009_PLUS_HARDCORE_L30_RECYCLE_V1:
	// High value level-30 weapons on a hard server: average damage >= 25%,
	// skill damage >= 8%, or refined to +7..+9.
	// These are valuable assets: never vendored to NPC, always preserved for market or scrolls.
	bool IsPlayerBotHighValueLevel30(LPITEM item)
	{
		if (!item || !IsPlayerBotSpecialLevel30Weapon(item))
			return false;
		if (item->GetRefineLevel() >= 7)
			return true;
		const long avg = SumPlayerBotItemLines(item, APPLY_NORMAL_HIT_DAMAGE_BONUS);
		const long skill = SumPlayerBotItemLines(item, APPLY_SKILL_DAMAGE_BONUS);
		return (avg >= 25 || skill >= 8);
	}"""
        )
    ]
    patch_file(os.path.join(OVERLAYS_DIR, 'playerbot_gear.h'), gear_replacements)

    # 6. playerbot_upstream_botlogic.h
    print("\n6. Patching playerbot_upstream_botlogic.h...")
    botlogic_replacements = [
        (
            """	const int PLAYERBOT_LOTTERY30_PER_DAY = 2;""",
            """	const int PLAYERBOT_LOTTERY30_PER_DAY = 8;"""
        ),
        (
            """	bool IsPlayerBotLottery30Surplus(LPCHARACTER ch, LPITEM item)
	{
		if (!ch || !item || !IsPlayerBotSpecialLevel30Weapon(item) || item->IsEquipped() ||
				item->GetWindow() != INVENTORY || (int)ch->GetLevel() < 30 ||""",
            """	bool IsPlayerBotLottery30Surplus(LPCHARACTER ch, LPITEM item)
	{
		if (!ch || !item || !IsPlayerBotSpecialLevel30Weapon(item) || item->IsEquipped() ||
				item->GetWindow() != INVENTORY || (int)ch->GetLevel() < 15 ||"""
        ),
        (
            """		sys_log(0, "PLAYERBOT_SURPLUS: lottery30 takes pid=%u name=%s item=%u vnum=%u plus=%u avg=%ld market_plus0=%d today=%d target=%u",
				ch->GetPlayerID(), ch->GetName(), item->GetID(), item->GetVnum(), (unsigned int)item->GetRefineLevel(),
				SumPlayerBotItemLines(item, APPLY_NORMAL_HIT_DAMAGE_BONUS), market, taken,
				(unsigned int)GetPlayerBotLevel30SaleTarget(item));
		return true;
	}""",
            """		sys_log(0, "PLAYERBOT_SURPLUS: lottery30 takes pid=%u name=%s item=%u vnum=%u plus=%u avg=%ld market_plus0=%d today=%d target=%u",
				ch->GetPlayerID(), ch->GetName(), item->GetID(), item->GetVnum(), (unsigned int)item->GetRefineLevel(),
				SumPlayerBotItemLines(item, APPLY_NORMAL_HIT_DAMAGE_BONUS), market, taken,
				(unsigned int)GetPlayerBotLevel30SaleTarget(item));
		return true;
	}

	void OnPlayerBotLottery30Refined(LPCHARACTER ch, DWORD dwOldId, LPITEM pkItemAfter)
	{
		if (!ch || ch->GetQuestFlag(PLAYERBOT_LOTTERY30_DAY_FLAG) != GetPlayerBotLottery30Today() ||
				(DWORD)ch->GetQuestFlag(PLAYERBOT_LOTTERY30_ID_FLAG) != dwOldId)
			return;
		if (pkItemAfter && pkItemAfter->GetID() != dwOldId)
		{
			ch->SetQuestFlag(PLAYERBOT_LOTTERY30_ID_FLAG, (int)pkItemAfter->GetID());
			sys_log(0, "PLAYERBOT_SURPLUS: lottery30 updated item ID pid=%u name=%s old=%u new=%u",
					ch->GetPlayerID(), ch->GetName(), dwOldId, pkItemAfter->GetID());
		}
	}"""
        )
    ]
    patch_file(os.path.join(OVERLAYS_DIR, 'playerbot_upstream_botlogic.h'), botlogic_replacements)

    # 7. playerbot_market.h
    print("\n7. Patching playerbot_market.h...")
    market_replacements = [
        (
            """		// MT2009_PLUS_TRADEABLE_BONUS_V2: the tradeable change or add
		// (71284/71285) only for a bot that would spend it on its own gear and
		// holds none of the kind, plain (71084/71085) or tradeable - never to
		// sell again.
		if (IsPlayerBotTradeableBonusVnum(offer->GetVnum()))
		{
			if (!PlayerBotCanSpendBonusStoneKind(ch, offer) || offer->GetCount() > 1)
				return false;
			for (WORD cell = 0; cell < PLAYERBOT_BAG_CELLS; ++cell)
			{
				LPITEM held = ch->GetInventoryItem(cell);
				if (held && held->GetType() == ITEM_USE && held->GetSubType() == offer->GetSubType() &&
						!IsPlayerBotGreenBonusStone(held->GetVnum()))
					return false;
			}
			return true;
		}""",
            """		// MT2009_PLUS_TRADEABLE_BONUS_V2: the tradeable change or add
		// (71284/71285) only for a bot that would spend it on its own gear and
		// holds none of the kind, plain (71084/71085) or tradeable - never to
		// sell again.
		if (IsPlayerBotTradeableBonusVnum(offer->GetVnum()))
		{
			if (!PlayerBotCanSpendBonusStoneKind(ch, offer) || offer->GetCount() > 1)
				return false;
			for (WORD cell = 0; cell < PLAYERBOT_BAG_CELLS; ++cell)
			{
				LPITEM held = ch->GetInventoryItem(cell);
				if (held && held->GetType() == ITEM_USE && held->GetSubType() == offer->GetSubType() &&
						!IsPlayerBotGreenBonusStone(held->GetVnum()))
					return false;
			}
			return true;
		}
		// Zielony Czar (71151) i Zielona Sila (71152) - handel i skup przez boty <= 40 lvl:
		if (IsPlayerBotGreenTradeableBonusVnum(offer->GetVnum()))
		{
			if ((int)ch->GetLevel() > 40 || !PlayerBotCanSpendBonusStoneKind(ch, offer) || offer->GetCount() > 1)
				return false;
			for (WORD cell = 0; cell < PLAYERBOT_BAG_CELLS; ++cell)
			{
				LPITEM held = ch->GetInventoryItem(cell);
				if (held && held->GetType() == ITEM_USE && held->GetSubType() == offer->GetSubType() &&
						IsPlayerBotGreenBonusStone(held->GetVnum()))
					return false;
			}
			return true;
		}"""
        ),
        (
            """		if (IsPlayerBotTradeableBonusVnum(item->GetVnum()))
			return price <= (long long)GetPlayerBotShopAskingPrice(item) &&
					price <= spare * PLAYERBOT_TRADEABLE_BONUS_BUY_PURSE_PERCENT / 100;""",
            """		if (IsPlayerBotTradeableBonusVnum(item->GetVnum()) || IsPlayerBotGreenTradeableBonusVnum(item->GetVnum()))
			return price <= (long long)GetPlayerBotShopAskingPrice(item) &&
					price <= spare * PLAYERBOT_TRADEABLE_BONUS_BUY_PURSE_PERCENT / 100;"""
        )
    ]
    patch_file(os.path.join(OVERLAYS_DIR, 'playerbot_market.h'), market_replacements)

    # 7b. zielone-kamienie-m1m2-drop
    print("\n7b. Applying zielone-kamienie-m1m2-drop patches...")
    import subprocess
    zk_patch = os.path.join(REPO, 'Server', 'server-patches', 'krystian', 'zielone-kamienie-m1m2-drop', 'apply_patch.py')
    if os.path.exists(zk_patch):
        subprocess.run([sys.executable, zk_patch], check=True)

    # 8. Sync all modified files to docker game src
    print("\n8. Syncing overlay files to docker game src...")
    sync_files = [
        'playerbot_town.h',
        'playerbot_economy.h',
        'playerbot_offline_shop.h',
        'playerbot_manager.cpp',
        'playerbot_retirement.h',
        'playerbot_gear.h',
        'playerbot_upstream_botlogic.h',
        'playerbot_market.h',
        'playerbot_targeting.h'
    ]
    for filename in sync_files:
        src = os.path.join(OVERLAYS_DIR, filename)
        dst = os.path.join(DOCKER_DIR, filename)
        shutil.copy2(src, dst)
        print(f"  [SYNCED] {filename} -> {dst}")

    print("\n=== All Playerbot Files Restored & Synchronized Successfully! ===")

if __name__ == '__main__':
    main()
