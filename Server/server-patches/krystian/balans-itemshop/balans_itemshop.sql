-- ============================================================================
-- MT2Plus: Balans i Rozbudowa Sekcji 'Za Smocze Znaki' (DRAGON_MARK)
-- Autor: Krystian
-- Data: 2026-11-05
-- Zakres:
--   Modyfikuje WYLACZNIE kategorie lojalnosciowa 'Za Smocze Znaki' (indeksy 701-730).
--   Wszystkie pozostale kategorie ItemShopu (SM) pozostaja w 100% w oryginalnym stanie.
-- ============================================================================

USE common;

DELETE FROM itemshop_items WHERE `currency` = 'DRAGON_MARK' OR `index` BETWEEN 701 AND 799;

INSERT INTO itemshop_items (`index`, `vnum`, `count`, `price`, `currency`, `minLevel`, `socket0`, `socket1`, `socket2`) VALUES
(701, 70038, 50, 15, 'DRAGON_MARK', 0, 0, 0, 0),   -- Peleryna Mestwa x50
(702, 70038, 200, 45, 'DRAGON_MARK', 0, 0, 0, 0),  -- Peleryna Mestwa x200
(703, 70102, 5, 20, 'DRAGON_MARK', 0, 0, 0, 0),    -- Fasolka Zen x5
(704, 71003, 1, 35, 'DRAGON_MARK', 0, 0, 0, 0),    -- Zwoj Powrotu Umiejetnosci x1
(705, 71002, 1, 45, 'DRAGON_MARK', 0, 0, 0, 0),    -- Zwoj Powrotu Statusu x1
(706, 71050, 10, 15, 'DRAGON_MARK', 0, 0, 0, 0),   -- Mikstura Szybkosci x10
(707, 71034, 10, 15, 'DRAGON_MARK', 0, 0, 0, 0),   -- Mikstura Ataku (+15) x10
(708, 27989, 1, 40, 'DRAGON_MARK', 0, 0, 0, 0),    -- Wykrywacz Kamieni Metin x1
(709, 71001, 5, 40, 'DRAGON_MARK', 0, 0, 0, 0),    -- Zwoj Egzorcyzmu x5
(710, 71094, 2, 50, 'DRAGON_MARK', 0, 0, 0, 0),    -- Rada Pustelnika x2
(711, 50513, 1, 60, 'DRAGON_MARK', 0, 0, 0, 0),    -- Kamien Duchowy x1
(712, 71035, 5, 30, 'DRAGON_MARK', 0, 0, 0, 0),    -- Eliksir Poszukiwacza x5
(713, 25040, 5, 35, 'DRAGON_MARK', 0, 0, 0, 0),    -- Zwoj Blogoslawienstwa x5
(714, 71083, 2, 45, 'DRAGON_MARK', 0, 0, 0, 0),    -- Ksiega Obrobki Kamienia x2
(715, 71026, 1, 120, 'DRAGON_MARK', 0, 0, 0, 0),   -- Magiczny Metal x1
(716, 70035, 2, 50, 'DRAGON_MARK', 0, 0, 0, 0),    -- Magiczna Ruda Miedzi x2
(717, 27992, 1, 40, 'DRAGON_MARK', 0, 0, 0, 0),    -- Biala Perla x1
(718, 27993, 1, 30, 'DRAGON_MARK', 0, 0, 0, 0),    -- Niebieska Perla x1
(719, 27994, 1, 20, 'DRAGON_MARK', 0, 0, 0, 0),    -- Krwawa Perla x1
(720, 71015, 1, 25, 'DRAGON_MARK', 0, 0, 0, 0),    -- Pierscien Doswiadczenia x1
(721, 71016, 1, 35, 'DRAGON_MARK', 0, 0, 0, 0),    -- Rekawica Zlodzieja x1
(722, 71044, 10, 35, 'DRAGON_MARK', 0, 0, 0, 0),   -- Dlon Krytyka x10
(723, 71045, 10, 35, 'DRAGON_MARK', 0, 0, 0, 0),   -- Dlon Przebicia x10
(724, 71027, 5, 30, 'DRAGON_MARK', 0, 0, 0, 0),    -- Zycie Boga Smokow x5
(725, 71028, 5, 30, 'DRAGON_MARK', 0, 0, 0, 0),    -- Atak Boga Smokow x5
(726, 71030, 5, 30, 'DRAGON_MARK', 0, 0, 0, 0),    -- Obrona Boga Smokow x5
(727, 51501, 5, 45, 'DRAGON_MARK', 0, 0, 0, 0),    -- Cor Draconis surowe x5
(728, 100300, 3, 35, 'DRAGON_MARK', 0, 0, 0, 0),   -- Zielona Smocza Fasola x3
(729, 22000, 10, 15, 'DRAGON_MARK', 0, 0, 0, 0),   -- Zwoj Powrotu Do Miasta x10
(730, 22010, 5, 25, 'DRAGON_MARK', 0, 0, 0, 0);   -- Zwoj Powrotu x5
