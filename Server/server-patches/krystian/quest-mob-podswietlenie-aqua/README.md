# Podświetlenie Potworów Misyjnych na Kolor Aqua (Cyan)

## Opis Modyfikacji
Modyfikacja wizualna i ergonomiczna interfejsu gry pozwalająca na natychmiastowe odróżnienie potworów wymaganych do aktywnych zadań (misji polowań, fabularnych, biologa i pobocznych):
1. **Model 3D w Świecie Gry (Additive Render Mode Glow):**
   - W odróżnieniu od standardowych czerwonych mobów, potwory będące celem aktywnej misji gracza renderowane są w trybie addytywnym (`chr.testSetAddRenderModeRGB(vid, 0.0, 0.85, 1.0)`).
   - Cały trójwymiarowy model potwora emituje jaskrawą, błękitną poświatę (Aqua / Cyan), widoczną z dużej odległości w terenie nawet przez przeszkody, mgłę i roślinność.
2. **Etykieta Nad Głową Potwora (Overhead Title Tag):**
   - Nad nazwą potwora pojawia się błękitny znacznik `[Misja]` w kolorze Aqua (`textTail.AttachPersonality(vid, "[Misja]", 0.0, 0.85, 1.0)`).
   - Etykieta jest zsynchronizowana z pozycją paska tekstu potwora i natychmiast znika po jego pokonaniu lub ukończeniu misji.
3. **Pasek Celu (Target Board UI - `uitarget.py`):**
   - Po zaznaczeniu potwora misyjnego jego nazwa na górnym pasku celu przyjmuje jaskrawy kolor Aqua (`0xFF00E5FF`) oraz prefiks `[Misja]` (np. `[Misja] Lv.12 (Stopień 2) Brąz. Niedźw.`).
   - Przy zaznaczeniu zwykłego potwora lub obiektu kolor powraca automatycznie do standardowej bieli.
4. **Weryfikacja Serwerowa i Błyskawiczna Synchronizacja (C++):**
   - Funkcja `IsPlayerQuestTargetMob(ch, dwRaceNum)` dynamicznie weryfikuje misję polowania (`hunting.huntingMobVnum`, `hunting.huntingMobCount`) oraz wszelkie aktywne misje w silniku questów z licznikami potworów (`qs._counter_name` formatu `{m<vnum>}` oraz nazwy lokalnej moba).
   - W momencie wejścia moba w zasięg widzenia gracza (`CHARACTER::EncodeInsertPacket`), serwer natychmiast przesyła pakiet `QuestMobMark <vid> 1` (zero lagów i zero opóźnień).
   - Przy zmianie stanu misji i po zabiciu potwora wywoływana jest funkcja `RefreshQuestMobMarks()`, która odświeża stan wszystkich mobów w polu widzenia gracza.
   - Dodano komendę `/refresh_quest_mobs` dla gracza.
5. **Opcja w Ustawieniach Gry:**
   - W menu `Opcje Gry > Dodatkowe` dodano przełącznik: `"Ukryj podświetlenie potworów misyjnych"`, pozwalający graczom na wyłączenie tego efektu w dowolnym momencie.

## Dotknięte Pliki
- `Server/linux-port/docker/game/src/server/game/src/char.h` (Deklaracja `RefreshQuestMobMarks`)
- `Server/linux-port/docker/game/src/server/game/src/char.cpp` (`EncodeInsertPacket` wysyłający `QuestMobMark %u 1`, implementacja `RefreshQuestMobMarks`)
- `Server/linux-port/docker/game/src/server/game/src/questmanager.cpp` (Implementacja `IsPlayerQuestTargetMob`)
- `Server/linux-port/docker/game/src/server/game/src/questpc.cpp` (Odświeżanie znaczników przy `SetCurrentQuestCounterValue`)
- `Server/linux-port/docker/game/src/server/game/src/cmd.cpp` oraz `cmd_general.cpp` (Rejestracja komendy `/refresh_quest_mobs`)
- `Klient/pack/root/questmobhighlight.py` (Nowy moduł zarządzania podświetleniem Aqua)
- `Klient/pack/root/uitarget.py` (Kolor fontu Aqua `0xFF00E5FF` i prefiks `[Misja]`)
- `Klient/pack/root/game.py` (Obsługa komendy sieciowej `QuestMobMark` i pętla w `OnPerSecondFixedUpdate`)
- `Klient/pack/root/uiopcjedodatkowe.py` (Opcja wyłączenia w menu dodatkowym)
