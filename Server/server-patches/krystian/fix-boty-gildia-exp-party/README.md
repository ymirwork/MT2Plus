# Fix Boty: Zrzutki Gildii & Exp Party

Poprawka zachowania botów graczy (Playerbots) w gildiach oraz w grupach (party).

## Co naprawia
- **Zrzutki na ziemie gildii:**
  - Boty poprawnie partycypują w kosztach i wpłatach Yang na ziemie gildii (`playerbot_guild_orders.h`, `playerbot_manager.cpp`).
- **Rozdzielanie doświadczenia (Party Exp):**
  - Poprawka rozdzielania expa w grupie z botami (`char.cpp`, `playerbot_manager.cpp`).

## Status w projekcie
Poprawka została włączona do oficjalnego kodu bazowego Upstream (od wersji v2.32.0). Zachowana w celach referencyjnych i audytu.
