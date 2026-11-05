#!/usr/bin/env python3
"""
Modyfikacja: Odnawianie Sklepów Botów (V1: 4 strony / 320 slotów; V2: Priorytetowe wznawianie wygasłych sklepów)
Autor: Krystian
Data: 2026-10-24 (V1), 2026-11-05 (V2)

Opis V2:
Usuwa błąd logiczny z upstreamu 2.41.0, gdzie bot posiadający wygasły sklep offline (IkarusShop):
1. Blokował odnowienie sklepu na sprawdzaniu GetPlayerBotReservedGold(ch) (rezerwa na konia ~500k-1kk yang
   blokowała opłatę 6000 yang za sklep u bota mającego setki tysięcy yang) oraz rollu TRADE slidera.
2. Zamiast natychmiast odnowić sklep na świecie, w pętli podejmował próby zdejmowania niesprzedanych przedmiotów
   (po 1 sztuce na 15 minut), a przy pełnym ekwipunku lub braku rolla zawieszał się na zawsze, zostawiając
   sklep z duration=0. W rezultacie liczba aktywnych sklepów spadła z ~1460 do 759.
V2 przenosi odnowienie sklepu (reopen) na najwyższy priorytet w sekcji wygasłego sklepu, umożliwiając
natychmiastowe przywrócenie sklepu na mapie z czasem 480 minut, jeśli tylko sklep posiada asortyment
i bota stać na podstawową opłatę 6000 yang.
"""

import sys
from pathlib import Path

def patch_file(path: Path):
    if not path.is_file():
        print(f"[!] Plik nie istnieje: {path}")
        return False

    content = path.read_text(encoding="utf-8")
    original = content
    filename = path.name

    if filename == "char_shop.cpp":
        # Patch CanPlaceOnShopSlot
        target_on = "bool CHARACTER::CanPlaceOnShopSlot(BYTE slot)\n{\n"
        replacement_on = (
            "bool CHARACTER::CanPlaceOnShopSlot(BYTE slot)\n"
            "{\n"
            "\t// MT2009_PLUS_FIX_BOT_SHOP_REOPEN_V1: bot shops are not subject to player lock or premium restrictions\n"
            "\tif (GetDesc() && GetDesc()->IsBot())\n"
            "\t\treturn true;\n"
        )
        if "MT2009_PLUS_FIX_BOT_SHOP_REOPEN_V1" not in content:
            if target_on in content:
                content = content.replace(target_on, replacement_on, 1)
            else:
                target_on_crlf = target_on.replace("\n", "\r\n")
                replacement_on_crlf = replacement_on.replace("\n", "\r\n")
                if target_on_crlf in content:
                    content = content.replace(target_on_crlf, replacement_on_crlf, 1)

        # Patch CanPlaceItemOnShopSlot
        target_item = "bool CHARACTER::CanPlaceItemOnShopSlot(BYTE slot, BYTE itemHeight)\n{\n"
        replacement_item = (
            "bool CHARACTER::CanPlaceItemOnShopSlot(BYTE slot, BYTE itemHeight)\n"
            "{\n"
            "\t// MT2009_PLUS_FIX_BOT_SHOP_REOPEN_V1: bot shops have up to 4 pages (BOT_SHOP_PAGES) without human limits\n"
            "\tif (GetDesc() && GetDesc()->IsBot())\n"
            "\t\treturn true;\n"
        )
        if "MT2009_PLUS_FIX_BOT_SHOP_REOPEN_V1: bot shops have up to 4 pages" not in content:
            if target_item in content:
                content = content.replace(target_item, replacement_item, 1)
            else:
                target_item_crlf = target_item.replace("\n", "\r\n")
                replacement_item_crlf = replacement_item.replace("\n", "\r\n")
                if target_item_crlf in content:
                    content = content.replace(target_item_crlf, replacement_item_crlf, 1)

    elif filename == "ikarus_shop_manager.cpp":
        target = "if (!ch->CanPlaceItemOnShopSlot(itemHandle->GetInfo().pos, itemHandle->GetTable()->bSize))"
        replacement = "// MT2009_PLUS_FIX_BOT_SHOP_REOPEN_V1: bot shops are not subject to player lock or premium restrictions\n\t\t\t\tif (!(ch->GetDesc() && ch->GetDesc()->IsBot()) && !ch->CanPlaceItemOnShopSlot(itemHandle->GetInfo().pos, itemHandle->GetTable()->bSize))"
        if target in content and "MT2009_PLUS_FIX_BOT_SHOP_REOPEN_V1" not in content:
            content = content.replace(target, replacement, 1)

    elif filename == "playerbot_offline_shop.h":
        # V1: CanPlaceItemOnShopSlot bypass for bots
        target_v1 = "!ch->CanPlaceItemOnShopSlot((BYTE)line->GetInfo().pos, (BYTE)line->GetTable()->bSize)"
        replacement_v1 = "!(ch->GetDesc() && ch->GetDesc()->IsBot()) && !ch->CanPlaceItemOnShopSlot((BYTE)line->GetInfo().pos, (BYTE)line->GetTable()->bSize)"
        if target_v1 in content and "!(ch->GetDesc() && ch->GetDesc()->IsBot())" not in content:
            content = content.replace(target_v1, replacement_v1, 1)

        # V2: BotOfflineWouldRenew - always renew if bot has goods and basic shop fee
        target_renew = (
            "    bool BotOfflineWouldRenew(LPCHARACTER ch, const TPlayerBotAIState& state, NativeShop shop) {\n"
            "        if (!ch || !shop || shop->GetDuration() != 0 || shop->GetItems().empty()) return false;\n"
            "        if (IsPlayerBotShopReasonRolled(state.bShopOpenReason) && !ShouldPlayerBotKeepShop(ch, state)) return false;\n"
            "        return ch->GetGold() - aOfflineShopTime[1].price >= GetPlayerBotReservedGold(ch);\n"
            "    }"
        )
        replacement_renew = (
            "    bool BotOfflineWouldRenew(LPCHARACTER ch, const TPlayerBotAIState& state, NativeShop shop) {\n"
            "        if (!ch || !shop || shop->GetDuration() != 0 || shop->GetItems().empty()) return false;\n"
            "        // MT2009_PLUS_FIX_BOT_SHOP_REOPEN_V2: bot offline shops with goods always renew if bot has basic shop fee\n"
            "        return ch->GetGold() >= aOfflineShopTime[1].price;\n"
            "    }"
        )
        if "MT2009_PLUS_FIX_BOT_SHOP_REOPEN_V2: bot offline shops with goods always renew" not in content:
            if target_renew in content:
                content = content.replace(target_renew, replacement_renew, 1)
            else:
                target_renew_crlf = target_renew.replace("\n", "\r\n")
                replacement_renew_crlf = replacement_renew.replace("\n", "\r\n")
                if target_renew_crlf in content:
                    content = content.replace(target_renew_crlf, replacement_renew_crlf, 1)

        # V2: Priority Reopen in ManagePlayerBotOfflineService
        old_expired_block = (
            "        if (shop->GetDuration() == 0) {\n"
            "            // An expired stand needs no edit mode to give a line back, and one\n"
            "            // it would no longer take comes off before the stand is renewed.\n"
            "            int lowGear = 0;\n"
            "            const char* why = \"\";\n"
            "            const DWORD unwanted = BotOfflineUnwantedLine(ch, shop, lowGear, &why);\n"
            "            if (unwanted && BotOfflineTakeOff(ch, state, unwanted, lowGear, now, why)) {\n"
            "                BotOfflineFinishVisit(ch, state, now);\n"
            "                BotOfflineChainVisit(state, now);\n"
            "                return false;\n"
            "            }\n"
            "            // And a Cor Draconis or a sash nobody bought, for the merchant.\n"
            "            if (BotOfflineTakeOffStaleRare(ch, state, shop, now)) {\n"
            "                BotOfflineFinishVisit(ch, state, now);\n"
            "                return false;\n"
            "            }\n"
            "            // MT2009_PLUS_BOT_GOODS_TWO_BONUS_V1: and bonus goods unsold a day.\n"
            "            if (BotOfflineTakeOffStaleBonusGoods(ch, state, shop, now)) {\n"
            "                BotOfflineFinishVisit(ch, state, now);\n"
            "                return false;\n"
            "            }\n"
            "            // MT2009_PLUS_BOT_STALL_WEAK_TAKEOFF_V1: and weak-bonus scrap.\n"
            "            {\n"
            "                bool chained = false;\n"
            "                if (BotOfflineTakeOffWeakScrap(ch, state, shop, now, chained)) {\n"
            "                    BotOfflineFinishVisit(ch, state, now);\n"
            "                    if (chained) state.offlineShop.nextService = now + PLAYERBOT_STALL_WEAK_TAKEOFF_STEP_MS;\n"
            "                    return false;\n"
            "                }\n"
            "            }\n"
            "            // MT2009_PLUS_BOT_SHOP_MGMT_V1: and what the shop management takes home.\n"
            "            {\n"
            "                bool chained = false;\n"
            "                if (BotOfflineTakeOffShopMgmt(ch, state, shop, now, chained)) {\n"
            "                    BotOfflineFinishVisit(ch, state, now);\n"
            "                    if (chained) state.offlineShop.nextService = now + PLAYERBOT_STALL_WEAK_TAKEOFF_STEP_MS;\n"
            "                    return false;\n"
            "                }\n"
            "            }\n"
            "            // So does a piece the owner should be wearing.\n"
            "            {\n"
            "                long long gain = 0;\n"
            "                const DWORD reclaim = BotOfflineReclaimLine(ch, state, shop, now, gain);\n"
            "                if (reclaim && BotOfflineReclaim(ch, state, reclaim, gain, now)) {\n"
            "                    BotOfflineFinishVisit(ch, state, now);\n"
            "                    return false;\n"
            "                }\n"
            "            }\n"
            "            // The operator moved the TRADE slider while this stand was up. An\n"
            "            // eight-hour offline stand is not worth closing early - the fee is\n"
            "            // paid and the goods are with the entity - but it is not renewed\n"
            "            // under a weight that no longer wants it. The four exceptions\n"
            "            // (Merchant, poor, full bag, dropper pressure) are not asked: the\n"
            "            // slider never applied to them.\n"
            "            const bool stillWanted = !IsPlayerBotShopReasonRolled(state.bShopOpenReason) ||\n"
            "                    ShouldPlayerBotKeepShop(ch, state);\n"
            "            bool reopened = false;\n"
            "            char sign[SHOP_SIGN_MAX_LEN + 1] = \"\";\n"
            "            // MT2009_PLUS_BOT_COUNTER_RENEW_V1: the renewal stands where its\n"
            "            // owner stands, and the engine refuses it within sixty units of a\n"
            "            // running stand - one put up on the old spot while this one was\n"
            "            // expired, or beside it. The owner steps to the nearest free spot\n"
            "            // (BotOfflineFindRenewSpot) and asks there, at most\n"
            "            // PLAYERBOT_OFFLINE_RENEW_SPOT_TRIES steps a visit. A refusal for\n"
            "            // the map's limit (no stand that near) is not walked round.\n"
            "            const bool canPay = ch->GetGold() - aOfflineShopTime[1].price >= GetPlayerBotReservedGold(ch);\n"
            "            if (stillWanted && canPay && !shop->GetItems().empty() && !manager.CanOpenOnMap(ch) &&\n"
            "                    o.renewSpotTries < PLAYERBOT_OFFLINE_RENEW_SPOT_TRIES) {\n"
            "                FPlayerBotNearestStand crowd(ch);\n"
            "                if (ch->GetSectree())\n"
            "                    ch->GetSectree()->ForEachAround(crowd);\n"
            "                long spotX = 0, spotY = 0;\n"
            "                if (crowd.best >= 0 && crowd.best <= 60 + 10 &&\n"
            "                        BotOfflineFindRenewSpot(ch, serviceX, serviceY, spotX, spotY)) {\n"
            "                    ++o.renewSpotTries;\n"
            "                    ch->SetRotationToXY(spotX, spotY);\n"
            "                    if (ch->Goto(spotX, spotY)) {\n"
            "                        ch->SendMovePacket(FUNC_MOVE, 0, spotX, spotY, ch->GetCurrentMoveDuration(), now);\n"
            "                        o.renewStepX = spotX;\n"
            "                        o.renewStepY = spotY;\n"
            "                        o.renewStepUntil = now + PLAYERBOT_OFFLINE_RENEW_STEP_MS;\n"
            "                        PlayerBotLogThrottled(\"offline_renew_step\", now,\n"
            "                            \"PLAYERBOT_OFFLINE: renewal steps to a free spot pid=%u name=%s near_stand=%d from=(%ld,%ld) to=(%ld,%ld) try=%u\",\n"
            "                            ch->GetPlayerID(), ch->GetName(), crowd.best, ch->GetX(), ch->GetY(),\n"
            "                            spotX, spotY, (unsigned int)o.renewSpotTries);\n"
            "                        return true;\n"
            "                    }\n"
            "                }\n"
            "            }\n"
            "            o.renewCalledAt = 0;\n"
            "            if (stillWanted && !shop->GetItems().empty() &&\n"
            "                    ch->GetGold() - aOfflineShopTime[1].price >= GetPlayerBotReservedGold(ch) &&\n"
            "                    Begin(ch->GetPlayerID(), Create, 0, now)) {\n"
            "                // Renamed for what it holds now - eight hours of service visits\n"
            "                // have added to it - by the same rules as a new stand. A name\n"
            "                // from before those rules is not renewed either.\n"
            "                const char* how = \"kept\";\n"
            "                if (!BotOfflineNameForGoods(ch, shop, sign, sizeof(sign), &how))\n"
            "                    strlcpy(sign, shop->GetName(), sizeof(sign));\n"
            "                manager.RecvShopReopenClientPacket(ch, sign, 1);\n"
            "                reopened = EndCall(ch->GetPlayerID());\n"
            "                // Its lines are on the counts at once, not at the next ledger.\n"
            "                if (reopened)\n"
            "                    for (const auto& [lid, l] : shop->GetItems()) {\n"
            "                        if (!l) continue;\n"
            "                        NotePlayerBotCappedLineOnCounter(l->GetInfo().vnum, (int)l->GetInfo().count);\n"
            "                        NotePlayerBotMissionBooksOnCounter(serviceMap, l->GetInfo().vnum, (int)l->GetInfo().count);\n"
            "                    }\n"
            "                if (reopened)\n"
            "                    sys_log(0, \"PLAYERBOT_OFFLINE: reopen pid=%u name=%s lines=%u sign=\\\"%s\\\" how=%s moved_from=%ld spot_steps=%u\",\n"
            "                        ch->GetPlayerID(), ch->GetName(), unsigned(shop->GetItems().size()), sign, how,\n"
            "                        serviceMap != spawn.map ? (long)spawn.map : 0L, (unsigned int)o.renewSpotTries);\n"
            "            }\n"
            "            // MT2009_PLUS_BOT_COUNTER_RENEW_V1: renewed, the next expiry calls\n"
            "            // at once; refused, not before a quarter of an hour.\n"
            "            o.renewHoldUntil = reopened ? 0 : now + PLAYERBOT_OFFLINE_RENEW_HOLD_MS;"
        )

        new_expired_block = (
            "        if (shop->GetDuration() == 0) {\n"
            "            // MT2009_PLUS_FIX_BOT_SHOP_REOPEN_V2: PRIORYTET DLA REOPEN!\n"
            "            // Wygaśnięty sklep posiadający towary natychmiast wraca na świat (480 min duration).\n"
            "            // Nie blokujemy na GetPlayerBotReservedGold (rezerwa na konia) ani na TRADE sliderze.\n"
            "            const bool canPay = ch->GetGold() >= aOfflineShopTime[1].price;\n"
            "            const bool stillWanted = !shop->GetItems().empty();\n"
            "            bool reopened = false;\n"
            "            char sign[SHOP_SIGN_MAX_LEN + 1] = \"\";\n"
            "            if (canPay && !shop->GetItems().empty()) {\n"
            "                if (!manager.CanOpenOnMap(ch) && o.renewSpotTries < PLAYERBOT_OFFLINE_RENEW_SPOT_TRIES) {\n"
            "                    FPlayerBotNearestStand crowd(ch);\n"
            "                    if (ch->GetSectree())\n"
            "                        ch->GetSectree()->ForEachAround(crowd);\n"
            "                    long spotX = 0, spotY = 0;\n"
            "                    if (crowd.best >= 0 && crowd.best <= 60 + 10 &&\n"
            "                            BotOfflineFindRenewSpot(ch, serviceX, serviceY, spotX, spotY)) {\n"
            "                        ++o.renewSpotTries;\n"
            "                        ch->SetRotationToXY(spotX, spotY);\n"
            "                        if (ch->Goto(spotX, spotY)) {\n"
            "                            ch->SendMovePacket(FUNC_MOVE, 0, spotX, spotY, ch->GetCurrentMoveDuration(), now);\n"
            "                            o.renewStepX = spotX;\n"
            "                            o.renewStepY = spotY;\n"
            "                            o.renewStepUntil = now + PLAYERBOT_OFFLINE_RENEW_STEP_MS;\n"
            "                            PlayerBotLogThrottled(\"offline_renew_step\", now,\n"
            "                                \"PLAYERBOT_OFFLINE: renewal steps to a free spot pid=%u name=%s near_stand=%d from=(%ld,%ld) to=(%ld,%ld) try=%u\",\n"
            "                                ch->GetPlayerID(), ch->GetName(), crowd.best, ch->GetX(), ch->GetY(),\n"
            "                                spotX, spotY, (unsigned int)o.renewSpotTries);\n"
            "                            return true;\n"
            "                        }\n"
            "                    }\n"
            "                }\n"
            "                o.renewCalledAt = 0;\n"
            "                if (Begin(ch->GetPlayerID(), Create, 0, now)) {\n"
            "                    const char* how = \"kept\";\n"
            "                    if (!BotOfflineNameForGoods(ch, shop, sign, sizeof(sign), &how))\n"
            "                        strlcpy(sign, shop->GetName(), sizeof(sign));\n"
            "                    manager.RecvShopReopenClientPacket(ch, sign, 1);\n"
            "                    reopened = EndCall(ch->GetPlayerID());\n"
            "                    if (reopened)\n"
            "                        for (const auto& [lid, l] : shop->GetItems()) {\n"
            "                            if (!l) continue;\n"
            "                            NotePlayerBotCappedLineOnCounter(l->GetInfo().vnum, (int)l->GetInfo().count);\n"
            "                            NotePlayerBotMissionBooksOnCounter(serviceMap, l->GetInfo().vnum, (int)l->GetInfo().count);\n"
            "                        }\n"
            "                    if (reopened)\n"
            "                        sys_log(0, \"PLAYERBOT_OFFLINE: reopen pid=%u name=%s lines=%u sign=\\\"%s\\\" how=%s moved_from=%ld spot_steps=%u\",\n"
            "                            ch->GetPlayerID(), ch->GetName(), unsigned(shop->GetItems().size()), sign, how,\n"
            "                            serviceMap != spawn.map ? (long)spawn.map : 0L, (unsigned int)o.renewSpotTries);\n"
            "                }\n"
            "            }\n"
            "            o.renewHoldUntil = reopened ? 0 : now + PLAYERBOT_OFFLINE_RENEW_HOLD_MS;\n"
            "            if (reopened) {\n"
            "                BotOfflineFinishVisit(ch, state, now);\n"
            "                return false;\n"
            "            }\n"
            "            // Jeśli sklep nie został odnowiony (np. pusty lub brak yang), wykonaj zdejmowanie itemów:\n"
            "            int lowGear = 0;\n"
            "            const char* why = \"\";\n"
            "            const DWORD unwanted = BotOfflineUnwantedLine(ch, shop, lowGear, &why);\n"
            "            if (unwanted && BotOfflineTakeOff(ch, state, unwanted, lowGear, now, why)) {\n"
            "                BotOfflineFinishVisit(ch, state, now);\n"
            "                BotOfflineChainVisit(state, now);\n"
            "                return false;\n"
            "            }\n"
            "            if (BotOfflineTakeOffStaleRare(ch, state, shop, now)) {\n"
            "                BotOfflineFinishVisit(ch, state, now);\n"
            "                return false;\n"
            "            }\n"
            "            if (BotOfflineTakeOffStaleBonusGoods(ch, state, shop, now)) {\n"
            "                BotOfflineFinishVisit(ch, state, now);\n"
            "                return false;\n"
            "            }\n"
            "            {\n"
            "                bool chained = false;\n"
            "                if (BotOfflineTakeOffWeakScrap(ch, state, shop, now, chained)) {\n"
            "                    BotOfflineFinishVisit(ch, state, now);\n"
            "                    if (chained) state.offlineShop.nextService = now + PLAYERBOT_STALL_WEAK_TAKEOFF_STEP_MS;\n"
            "                    return false;\n"
            "                }\n"
            "            }\n"
            "            {\n"
            "                bool chained = false;\n"
            "                if (BotOfflineTakeOffShopMgmt(ch, state, shop, now, chained)) {\n"
            "                    BotOfflineFinishVisit(ch, state, now);\n"
            "                    if (chained) state.offlineShop.nextService = now + PLAYERBOT_STALL_WEAK_TAKEOFF_STEP_MS;\n"
            "                    return false;\n"
            "                }\n"
            "            }\n"
            "            {\n"
            "                long long gain = 0;\n"
            "                const DWORD reclaim = BotOfflineReclaimLine(ch, state, shop, now, gain);\n"
            "                if (reclaim && BotOfflineReclaim(ch, state, reclaim, gain, now)) {\n"
            "                    BotOfflineFinishVisit(ch, state, now);\n"
            "                    return false;\n"
            "                }\n"
            "            }"
        )

        if "MT2009_PLUS_FIX_BOT_SHOP_REOPEN_V2: PRIORYTET DLA REOPEN" not in content:
            if old_expired_block in content:
                content = content.replace(old_expired_block, new_expired_block, 1)
            else:
                old_crlf = old_expired_block.replace("\n", "\r\n")
                new_crlf = new_expired_block.replace("\n", "\r\n")
                if old_crlf in content:
                    content = content.replace(old_crlf, new_crlf, 1)

    if content != original:
        path.write_text(content, encoding="utf-8")
        print(f"[OK] Zaktualizowano: {path}")
        return True
    else:
        print(f"[--] Brak zmian lub juz zaaplikowane: {path}")
        return True

def main():
    repo_root = Path(__file__).resolve().parents[4]
    files = [
        repo_root / "Server/linux-port/overlays/playerbot/src/game/src/char_shop.cpp",
        repo_root / "Server/linux-port/docker/game/src/server/game/src/char_shop.cpp",
        repo_root / "Server/linux-port/overlays/playerbot/src/game/src/ikarus_shop_manager.cpp",
        repo_root / "Server/linux-port/docker/game/src/server/game/src/ikarus_shop_manager.cpp",
        repo_root / "Server/linux-port/overlays/playerbot/src/game/src/playerbot_offline_shop.h",
        repo_root / "Server/linux-port/docker/game/src/server/game/src/playerbot_offline_shop.h",
    ]

    success = True
    for f in files:
        if not patch_file(f):
            success = False

    if success:
        print("\n[SUKCES] Wszystkie pliki silnika gry zostaly pomyslnie zaktualizowane.")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
