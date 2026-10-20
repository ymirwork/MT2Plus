# Usprawnienia rozgrywki i mechanik (DEV GAMEPLAY)

Zestaw poprawek silnika (`game/src`), znacznik `MT2009_PLUS_DEV_GAMEPLAY_V1`:

1. **Czytanie Ksiąg Umiejętności (KU):**
   - Usunięto wymóg posiadania doświadczenia oraz pobieranie punktów EXP przy czytaniu KU (`char_skill.cpp`).
2. **Zdjęcie limiterów Movement Speed, Attack Speed, Damage Limit i Speedhack checków:**
   - Zdjęto sztuczne ograniczenia prędkości ataku i ruchu w `GetLimitPoint()` oraz bonusów IS (`char.cpp`).
   - Wyłączono fałszywe detekcje i rozłączanie za speedhack (`battle.cpp`, `char.cpp`, `input_main.cpp`).
   - Usunięto cofanie gracza i kary za szybki ruch w `input_main.cpp`.
   - Zdjęto limity redukcji obrażeń `MIN(200, ...)` i `MIN(300, ...)` w `char_battle.cpp`.
3. **Płynne ulepszanie (spamidło Enter):**
   - Usunięto 1-sekundowy cooldown u kowala w `input_main.cpp` (`WAIT_BEFORE_NEXT_REFINE`), umożliwiając szybkie zatwierdzanie ulepszania.
4. **Zapisywanie lochów i weryfikacja VIP/przepustki:**
   - Weryfikacja wejścia do Lochu Pająków V2 (mapa 71) przy teleportacji Zwojem Powrotu - darmowe dla VIP (`IsActivePremiumSubscription`), a dla pozostałych pobiera przepustkę 71095/71130 (`char_item.cpp`).
5. **Bonus językowy PvP (+5% obrażeń):**
   - Jeśli atakujący i ofiara są graczami z innych królestw, a atakujący posiada język królestwa ofiary na poziomie minimum M1 (`iSkillLevel >= 20`), zadawane obrażenia wzrastają o 5% (`char_battle.cpp`).

Stosowanie: `Apply-DevGameplayPatch.ps1 -SourceDir <game/src>` (Windows) lub `python3 apply_devgameplay.py <game/src>` (Linux/VPS).
