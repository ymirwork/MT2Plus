# MT2009_PLUS_FARM_SESSION_V1: Menadzer Sesji Farmienia (Autor: Krystian / Antigravity).
# Sledzi:
#  - Czas trwania sesji (stoper z pauza i wznawianiem)
#  - Zniszczone Kamienie Metin, pokonani Bossowie i laczna liczba zabojstw
#  - Zebrane surowe Yang oraz dokladna liste i ilosci podniesionych przedmiotow
#  - Szacowana wartosc w dwoch trybach:
#      * Rynkowa: sugerowana cena z rynku/sklepow offline lub wlasna wycena gracza
#      * NPC: cena sprzedazy do handlarza z uwzglednieniem podatku handlowego (3%)
#  - Statystyki tempa: Zarobek / godz., Metiny / godz., EXP / godz.
#  - Trwalosc: stan sesji i wlasne wyceny zapamietywane w katalogu autohunt/

import os
import json
import time
import app
import player
import item
import nonplayer
import chr
import clientclock
import localeInfo
import chat

try:
	long
except NameError:
	long = int

try:
	xrange
except NameError:
	xrange = range

try:
	from farmsession_prices import MARKET_PRICES
except Exception:
	MARKET_PRICES = {}

CONFIG_DIR = "autohunt"
PRICES_FILE = os.path.join(CONFIG_DIR, "farmsession_prices.json")
STATE_FILE = os.path.join(CONFIG_DIR, "farmsession_state.json")
HISTORY_FILE = os.path.join(CONFIG_DIR, "farmsessions_history.json")

MODE_MARKET = "MARKET"
MODE_NPC = "NPC"

# Mapowanie identyfikatorow map silnika na przyjazne polskie nazwy instancji
MAP_NAME_OVERRIDES = {
	"metin2_map_spiderdungeon": "Loch Pajakow V1",
	"metin2_map_spiderdungeon_02": "Loch Pajakow V2",
	"metin2_map_spiderdungeon_03": "Loch Pajakow V3",
	"metin2_map_deviltower1": "Wieza Demonow",
	"metin2_map_devilsCatacomb": "Diabelskie Katakumby",
	"metin2_map_n_desert_01": "Pustynia Yongbi",
	"metin2_map_n_flame_01": "Ognista Ziemia",
	"metin2_map_milgyo": "Dolina Orkow",
	"metin2_map_skipia_dungeon_01": "Grota Wygnancow V1",
	"metin2_map_skipia_dungeon_02": "Grota Wygnancow V2",
	"metin2_map_skipia_dungeon_boss": "Komnata Smoka",
	"metin2_map_reddragon": "Twierdza Razadora",
	"metin2_map_nemere": "Straznica Nemere",
	"metin2_map_dawnmist": "Przyladek Smoczego Ognia",
	"metin2_map_thunder": "Zatoka Nefrytowa",
	"metin2_map_bay": "Gory Grzmotu",
	"metin2_map_colosseum": "Koloseum",
	"metin2_map_a1": "Yongan (M1 Jinno)",
	"metin2_map_b1": "Joan (M1 Shinsoo)",
	"metin2_map_c1": "Pyungmoo (M1 Chunjo)",
	"metin2_map_a3": "Yayang (M2 Jinno)",
	"metin2_map_b3": "Bakra (M2 Shinsoo)",
	"metin2_map_c3": "Bokjung (M2 Chunjo)",
}

# Domyslny cennik bazowy dla popularnych dropow (gdy brak wlasnej ceny gracza i ceny rynkowej)
BASE_PRICES = {
	# Sztabki zlota
	80003: 50000,       # Sztabka zlota 50k
	80004: 100000,      # Sztabka zlota 100k
	80005: 500000,      # Sztabka zlota 500k
	80006: 1000000,     # Sztabka zlota 1kk
	80007: 2000000,     # Sztabka zlota 2kk
	# Kamienie / Zaczarowania / Wzmocnienia
	71084: 500000,      # Zaczarowanie Przedmiotu
	71085: 1000000,     # Wzmocnienie Przedmiotu
	71151: 150000,      # Zielony Czar
	71152: 300000,      # Zielona Sila
	71284: 2500000,     # Zolte Zaczarowanie
	71285: 5000000,     # Zolte Wzmocnienie
	# Popularne ulepszacze i dropy
	27987: 1500000,     # Malza
	27992: 8000000,     # Biala Perla
	27993: 5000000,     # Niebieska Perla
	27994: 3000000,     # Krwawa Perla
	25040: 1000000,     # Zwoj Blogoslawienstwa
	70038: 5000000,     # Magiczny Metal
	50300: 500000,      # Ksiega Umiejetnosci (srednia)
	51001: 200000,      # Fragment Energii
	30006: 100000,      # Kawalek Klejnotu
	30015: 150000,      # Zloty Pierscien / Zapiecie
}


def FormatNumber(val):
	"""Formatuje liczbe w notacji K / M / B lub standardowej."""
	try:
		n = long(val)
	except (ValueError, TypeError):
		return "0"

	if n >= 1000000000:
		return "%.2f B" % (float(n) / 1000000000.0)
	elif n >= 1000000:
		return "%.1f M" % (float(n) / 1000000.0)
	elif n >= 10000:
		return "%.1f K" % (float(n) / 1000.0)
	return localeInfo.MoneyFormat(n)


def FormatTime(seconds):
	"""Formatuje sekundy do postaci HH:MM:SS."""
	sec = int(max(0, seconds))
	h = sec // 3600
	m = (sec % 3600) // 60
	s = sec % 60
	return "%02d:%02d:%02d" % (h, m, s)


class FarmSessionManager(object):
	_instance = None

	@classmethod
	def Instance(cls):
		if cls._instance is None:
			cls._instance = FarmSessionManager()
		return cls._instance

	def __init__(self):
		self.is_active = True
		self.is_paused = False
		self.start_time = clientclock.Now()
		self.total_paused_duration = 0.0
		self.last_pause_time = 0.0
		self.custom_session_name = None

		# Tryb wyceny: MARKET (rynkowa ze sklepow) lub NPC (sprzedaz u handlarza z podatkiem 3%)
		self.price_mode = MODE_MARKET

		# Statystyki finansowe
		self.raw_yang = 0

		# Liczniki zrodel
		self.kills_total = 0
		self.kills_metin = 0
		self.kills_boss = 0

		# EXP
		self.exp_start = 0
		self.exp_gained = 0
		self.last_exp = 0
		self.last_level = 0

		# Dropy: {vnum: {"count": count, "custom_price": None, "hidden": False}}
		self.items = {}

		# Baza cen uzytkownika: {vnum: price}
		self.custom_prices = {}

		# Snapshot ekwipunku do wykrywania przyrostow
		self.inv_snapshot = {}
		self.pending_pickup_vnum = None
		self.pending_pickup_time = 0.0

		# Subskrybenci zdarzen UI
		self.ui_update_callbacks = []

		self.__LoadCustomPrices()
		self.__InitExp()

	def RegisterCallback(self, cb):
		if cb not in self.ui_update_callbacks:
			self.ui_update_callbacks.append(cb)

	def UnregisterCallback(self, cb):
		if cb in self.ui_update_callbacks:
			self.ui_update_callbacks.remove(cb)

	def NotifyUI(self):
		for cb in list(self.ui_update_callbacks):
			try:
				cb()
			except Exception:
				pass

	def __InitExp(self):
		try:
			self.last_exp = long(player.GetEXP())
			self.exp_start = self.last_exp
			self.last_level = int(player.GetStatus(player.LEVEL))
		except Exception:
			pass

	# ----------------- KONTROLA SESJI -----------------

	def Start(self):
		self.is_active = True
		self.is_paused = False
		self.start_time = clientclock.Now()
		self.total_paused_duration = 0.0
		self.last_pause_time = 0.0
		self.custom_session_name = None
		self.NotifyUI()

	def Pause(self):
		if not self.is_paused:
			self.is_paused = True
			self.last_pause_time = clientclock.Now()
			self.NotifyUI()

	def Resume(self):
		if self.is_paused:
			self.is_paused = False
			if self.last_pause_time > 0.0:
				self.total_paused_duration += max(0.0, clientclock.Now() - self.last_pause_time)
				self.last_pause_time = 0.0
			self.NotifyUI()

	def TogglePause(self):
		if self.is_paused:
			self.Resume()
		else:
			self.Pause()

	def Reset(self):
		self.is_active = True
		self.is_paused = False
		self.start_time = clientclock.Now()
		self.total_paused_duration = 0.0
		self.last_pause_time = 0.0
		self.custom_session_name = None
		self.raw_yang = 0
		self.kills_total = 0
		self.kills_metin = 0
		self.kills_boss = 0
		self.items.clear()
		self.__InitExp()
		self.exp_gained = 0
		self.UpdateInventorySnapshot()
		self.NotifyUI()

	def GetDuration(self):
		"""Zwraca aktywny czas trwania sesji w sekundach (bez pauz)."""
		if not self.is_active:
			return 0.0
		now = clientclock.Now()
		if self.is_paused:
			current_pause = max(0.0, now - self.last_pause_time) if self.last_pause_time > 0.0 else 0.0
			return max(0.0, self.last_pause_time - self.start_time - self.total_paused_duration)
		else:
			return max(0.0, now - self.start_time - self.total_paused_duration)

	# ----------------- TRYBY WYCENY (RYNKOWA / NPC) -----------------

	def SetPriceMode(self, mode):
		"""Przelacza tryb wyceny: MODE_MARKET lub MODE_NPC."""
		if mode in (MODE_MARKET, MODE_NPC):
			self.price_mode = mode
			self.NotifyUI()

	def GetPriceMode(self):
		return self.price_mode

	def GetItemPrice(self, vnum, mode=None):
		"""Zwraca cene za 1 sztuke w zaleznosci od wybranego trybu."""
		vnum = int(vnum)
		if mode is None:
			mode = self.price_mode

		if mode == MODE_NPC:
			return self.GetNPCPrice(vnum)
		else:
			return self.GetMarketPrice(vnum)

	def GetNPCPrice(self, vnum):
		"""Zwraca cene sprzedazy u NPC po potraceniu podatku handlowego 3%."""
		try:
			item.SelectItem(vnum)
			sellPrice = item.GetISellItemPrice()
			if sellPrice <= 0:
				buyPrice = item.GetIBuyItemPrice()
				if buyPrice > 0:
					sellPrice = buyPrice // 5

			# Sztabki zlota u NPC maja wartosc nominalna
			if vnum in (80003, 80004, 80005, 80006, 80007):
				nominal = {
					80003: 50000,
					80004: 100000,
					80005: 500000,
					80006: 1000000,
					80007: 2000000,
				}
				sellPrice = nominal.get(vnum, sellPrice)

			if sellPrice <= 0:
				return 0

			# Podatek od sprzedazy u NPC: 3% (kwota netto = 97%)
			tax = (sellPrice * 3) // 100
			netPrice = max(0, sellPrice - tax)
			return netPrice
		except Exception:
			return 0

	def GetMarketPrice(self, vnum):
		"""Zwraca sugerowana cene rynkowa (sklep offline / rynek botow)."""
		# 1. Wlasna cena gracza z bazy sesji
		if vnum in self.custom_prices:
			return long(self.custom_prices[vnum])

		# 2. Cennik rynkowy ze sklepow offline i rynku botow (ponad 3200 pozycji)
		if vnum in MARKET_PRICES:
			return long(MARKET_PRICES[vnum])

		# 3. Domyslna baza popularnych dropow
		if vnum in BASE_PRICES:
			return long(BASE_PRICES[vnum])

		# 4. Sprawdzenie cen ze sklepu offline / rynku gry
		try:
			import offlineShopBuilder
			p = offlineShopBuilder.GetPrivateShopItemPrice(vnum, 1)
			if p > 0:
				return long(p)
		except Exception:
			pass

		# 5. Wartosc bazowa sprzedazy NPC jako rezerwowy fallback
		try:
			item.SelectItem(vnum)
			buyPrice = item.GetIBuyItemPrice()
			if buyPrice > 0:
				return long(buyPrice)
		except Exception:
			pass

		return 0

	def SetCustomPrice(self, vnum, price):
		"""Ustawia wlasna cene rynkowa za sztuke wprowadzona przez gracza."""
		vnum = int(vnum)
		price = max(0, long(price))
		self.custom_prices[vnum] = price
		if vnum in self.items:
			self.items[vnum]["custom_price"] = price
		self.__SaveCustomPrices()
		self.NotifyUI()

	def ToggleItemHidden(self, vnum):
		"""Przelacza wykluczenie przedmiotu z wyceny."""
		vnum = int(vnum)
		if vnum in self.items:
			self.items[vnum]["hidden"] = not self.items[vnum].get("hidden", False)
			self.NotifyUI()

	def IsItemHidden(self, vnum):
		if vnum in self.items:
			return self.items[vnum].get("hidden", False)
		return False

	def GetRawYang(self):
		return self.raw_yang

	def GetItemsValue(self, mode=None):
		"""Suma wartosci zebranych lupow w danym trybie (z wylaczeniem pozycji wykluczonych)."""
		total = 0
		for vnum, data in self.items.items():
			if data.get("hidden", False):
				continue
			count = data.get("count", 0)
			price = self.GetItemPrice(vnum, mode)
			total += long(count) * price
		return total

	def GetTotalValue(self, mode=None):
		"""Laczna szacowana wartosc = Surowe Yang + Wartosc Lupow."""
		return self.GetRawYang() + self.GetItemsValue(mode)

	def GetYangPerHour(self, mode=None):
		"""Propozycja 1: Wskaznik tempa zarobku na godzine."""
		duration = self.GetDuration()
		if duration < 10.0:
			return 0
		hours = duration / 3600.0
		return long(float(self.GetTotalValue(mode)) / hours)

	def GetMetinsPerHour(self):
		"""Propozycja 1: Liczba zniszczonych Metinow na godzine."""
		duration = self.GetDuration()
		if duration < 10.0:
			return 0.0
		hours = duration / 3600.0
		return float(self.kills_metin) / hours

	def GetExpPerHour(self):
		"""Propozycja 4: Zdobyty EXP na godzine."""
		duration = self.GetDuration()
		if duration < 10.0:
			return 0
		hours = duration / 3600.0
		return long(float(self.exp_gained) / hours)

	# ----------------- REJESTRACJA ZDARZEN Z GRY -----------------

	def OnPickMoney(self, money):
		"""Zdarzenie podniesienia Yang z ziemi."""
		if self.is_paused:
			return
		try:
			amount = long(money)
			if amount > 0:
				self.raw_yang += amount
				self.NotifyUI()
		except Exception:
			pass

	def OnPickupSound(self, vnum):
		"""Zdarzenie komendy serwera PickupSound <vnum>."""
		if self.is_paused:
			return
		try:
			vnum = int(vnum)
			if vnum == 1:
				return
			self.pending_pickup_vnum = vnum
			self.pending_pickup_time = clientclock.Now()
			self.CheckInventoryGain(vnum)
		except Exception:
			pass

	def AddItem(self, vnum, count=1):
		"""Dodaje podniesiony przedmiot do sesji."""
		if self.is_paused or count <= 0:
			return
		vnum = int(vnum)
		if vnum not in self.items:
			self.items[vnum] = {
				"count": count,
				"custom_price": self.custom_prices.get(vnum, None),
				"hidden": False
			}
		else:
			self.items[vnum]["count"] += count
		self.NotifyUI()

	def __GetCurrentInventoryCounts(self):
		"""Zwraca slownik {vnum: laczna_liczba_sztuk_w_calym_ekwipunku}."""
		counts = {}
		totalSlots = getattr(player, "INVENTORY_DEFAULT_MAX_NUM", 180)
		for slot in xrange(totalSlots):
			vnum = player.GetItemIndex(slot)
			if vnum > 0:
				cnt = max(1, player.GetItemCount(slot))
				counts[vnum] = counts.get(vnum, 0) + cnt
		return counts

	def CheckInventoryGain(self, expected_vnum=None):
		"""Porownuje calkowity stan ekwipunku ze snapshotem i wykrywa autentyczne przyrosty."""
		if self.is_paused:
			return

		# Okna handlu / magazynu / sklepu / sortowania - tylko synchronizujemy baze
		try:
			import shop
			if shop.IsOpen():
				self.UpdateInventorySnapshot()
				return
		except Exception:
			pass
		try:
			import safebox
			if safebox.IsOpen():
				self.UpdateInventorySnapshot()
				return
		except Exception:
			pass
		try:
			import exchange
			if exchange.isTrading():
				self.UpdateInventorySnapshot()
				return
		except Exception:
			pass
		try:
			import inventoryarrange
			if inventoryarrange.IsPending():
				self.UpdateInventorySnapshot()
				return
		except Exception:
			pass

		current = self.__GetCurrentInventoryCounts()

		if not self.inv_snapshot:
			self.inv_snapshot = current
			return

		gains = {}
		for vnum, cnt in current.items():
			oldCnt = self.inv_snapshot.get(vnum, 0)
			if cnt > oldCnt:
				gains[vnum] = cnt - oldCnt

		self.inv_snapshot = current

		if gains:
			for vnum, count in gains.items():
				self.AddItem(vnum, count)
		elif expected_vnum and expected_vnum > 0:
			self.AddItem(expected_vnum, 1)

	def UpdateInventorySnapshot(self):
		"""Uaktualnia bazowy stan liczby przedmiotow w ekwipunku."""
		self.inv_snapshot = self.__GetCurrentInventoryCounts()

	def OnTargetKilled(self, vid):
		"""Zdarzenie smierci celu gracza (HP <= 0)."""
		if self.is_paused or not vid:
			return
		try:
			instanceType = chr.GetInstanceType(vid)
			isStone = instanceType == getattr(chr, "INSTANCE_TYPE_STONE", 2)
			grade = nonplayer.GetGradeByVID(vid)
			isBoss = grade >= getattr(nonplayer, "MOB_RANK_BOSS", 4) or grade >= getattr(nonplayer, "BOSS", 4)

			if isStone:
				self.kills_metin += 1
				self.kills_total += 1
			elif isBoss:
				self.kills_boss += 1
				self.kills_total += 1
			elif instanceType == chr.INSTANCE_TYPE_ENEMY:
				self.kills_total += 1

			self.NotifyUI()
		except Exception:
			pass

	def OnExpUpdate(self):
		"""Sprawdzenie przyrostu punktow doswiadczenia (EXP) i awansu poziomu."""
		if self.is_paused:
			return
		try:
			cur_exp = long(player.GetEXP())
			cur_level = int(player.GetStatus(player.LEVEL))

			if cur_level == self.last_level:
				if cur_exp > self.last_exp:
					diff = cur_exp - self.last_exp
					self.exp_gained += diff
					self.last_exp = cur_exp
					self.NotifyUI()
				elif cur_exp < self.last_exp:
					self.last_exp = cur_exp
			elif cur_level > self.last_level:
				self.last_level = cur_level
				self.last_exp = cur_exp
				self.NotifyUI()
		except Exception:
			pass

	# ----------------- SERIALIZACJA I TRWALOSC -----------------

	def __LoadCustomPrices(self):
		if not os.path.exists(PRICES_FILE):
			return
		try:
			with open(PRICES_FILE, "r") as f:
				data = json.load(f)
				for k, v in data.items():
					self.custom_prices[int(k)] = long(v)
		except Exception:
			pass

	def __SaveCustomPrices(self):
		try:
			if not os.path.exists(CONFIG_DIR):
				os.makedirs(CONFIG_DIR)
			with open(PRICES_FILE, "w") as f:
				json.dump(self.custom_prices, f, indent=2)
		except Exception:
			pass

	# ----------------- ZAPISYWANIE I HISTORIA SESJI -----------------

	def SetSessionName(self, name):
		"""Ustawia wlasna nazwe dla biezacej sesji."""
		self.custom_session_name = str(name).strip() if name else None
		self.NotifyUI()

	def GetCurrentMapTitle(self):
		"""Zwraca czytelna polska nazwe aktualnej mapy."""
		try:
			import background
			mapName = background.GetCurrentMapName()
			if mapName:
				if mapName in MAP_NAME_OVERRIDES:
					return MAP_NAME_OVERRIDES[mapName]
				if hasattr(localeInfo, "MINIMAP_ZONE_NAME_DICT"):
					val = localeInfo.MINIMAP_ZONE_NAME_DICT.get(mapName, None)
					if val:
						return val
				return mapName
		except Exception:
			pass
		return "Sesja farmienia"

	def GetDefaultSessionName(self):
		"""Zwraca domyslna sugerowana nazwe sesji na podstawie aktualnej mapy i godziny."""
		if self.custom_session_name:
			return self.custom_session_name

		mapTitle = self.GetCurrentMapTitle()
		try:
			timeStr = time.strftime("%H:%M")
			return "%s (%s)" % (mapTitle, timeStr)
		except Exception:
			return mapTitle

	def GetSessionSnapshot(self, name=None):
		"""Tworzy pelny slownik z danymi biezacej sesji do zapisu lub porownania."""
		if not name:
			name = self.GetDefaultSessionName()

		mapTitle = self.GetCurrentMapTitle()

		itemsDict = {}
		for vnum, data in self.items.items():
			itemsDict[str(vnum)] = {
				"count": int(data.get("count", 0)),
				"custom_price": data.get("custom_price"),
				"hidden": bool(data.get("hidden", False))
			}

		duration = self.GetDuration()
		snapshot = {
			"id": str(long(time.time() * 1000)),
			"name": str(name),
			"map_name": str(mapTitle),
			"date": time.strftime("%Y-%m-%d %H:%M"),
			"duration": float(duration),
			"raw_yang": long(self.raw_yang),
			"kills_total": int(self.kills_total),
			"kills_metin": int(self.kills_metin),
			"kills_boss": int(self.kills_boss),
			"exp_gained": long(self.exp_gained),
			"price_mode": str(self.price_mode),
			"items": itemsDict,
			"total_value": long(self.GetTotalValue()),
			"yang_per_hour": long(self.GetYangPerHour()),
			"metin_per_hour": float(self.GetMetinsPerHour()),
			"exp_per_hour": long(self.GetExpPerHour())
		}
		return snapshot

	def SaveSession(self, name=None):
		"""Zapisuje biezaca sesje do pliku historii."""
		if not name:
			name = self.GetDefaultSessionName()
		snapshot = self.GetSessionSnapshot(name)
		sessions = self.GetSavedSessions()
		sessions.append(snapshot)
		self.__WriteSavedSessions(sessions)
		return snapshot

	def GetSavedSessions(self):
		"""Wczytuje liste wszystkich zapisanych sesji z pliku."""
		if not os.path.exists(HISTORY_FILE):
			return []
		try:
			with open(HISTORY_FILE, "r") as f:
				data = json.load(f)
				if isinstance(data, list):
					return data
				return []
		except Exception:
			return []

	def __WriteSavedSessions(self, sessions):
		try:
			if not os.path.exists(CONFIG_DIR):
				os.makedirs(CONFIG_DIR)
			with open(HISTORY_FILE, "w") as f:
				json.dump(sessions, f, indent=2)
			return True
		except Exception:
			return False

	def DeleteSavedSession(self, session_id):
		"""Usuwa sesje o podanym ID z pliku historii."""
		sessions = self.GetSavedSessions()
		sessions = [s for s in sessions if str(s.get("id")) != str(session_id)]
		self.__WriteSavedSessions(sessions)

	def RenameSavedSession(self, session_id, new_name):
		"""Zmienia nazwe sesji o podanym ID."""
		sessions = self.GetSavedSessions()
		for s in sessions:
			if str(s.get("id")) == str(session_id):
				s["name"] = str(new_name)
				break
		self.__WriteSavedSessions(sessions)

	def CalculateSnapshotMetrics(self, session_data, mode=None):
		"""Wylicza metryki i zysk sesji w zaleznosci od wybranego trybu wyceny (Rynkowa / NPC)."""
		if mode is None:
			mode = session_data.get("price_mode", MODE_MARKET)

		raw_yang = long(session_data.get("raw_yang", 0))
		duration = float(session_data.get("duration", 0.0))
		kills_metin = int(session_data.get("kills_metin", 0))
		kills_boss = int(session_data.get("kills_boss", 0))
		kills_total = int(session_data.get("kills_total", 0))
		exp_gained = long(session_data.get("exp_gained", 0))

		items_val = 0
		items = session_data.get("items", {})
		for vnum_str, item_info in items.items():
			try:
				vnum = int(vnum_str)
				if item_info.get("hidden", False):
					continue
				count = long(item_info.get("count", 0))
				custom_p = item_info.get("custom_price")
				if custom_p is not None and mode == MODE_MARKET:
					price = long(custom_p)
				else:
					price = self.GetItemPrice(vnum, mode)
				items_val += count * price
			except Exception:
				pass

		total_val = raw_yang + items_val
		hours = duration / 3600.0 if duration >= 10.0 else 0.0
		yang_per_h = long(float(total_val) / hours) if hours > 0 else 0
		metin_per_h = float(kills_metin) / hours if hours > 0 else 0.0
		exp_per_h = long(float(exp_gained) / hours) if hours > 0 else 0

		return {
			"name": session_data.get("name", "Sesja"),
			"map_name": session_data.get("map_name", ""),
			"date": session_data.get("date", ""),
			"total_value": total_val,
			"raw_yang": raw_yang,
			"items_value": items_val,
			"yang_per_hour": yang_per_h,
			"metin_per_hour": metin_per_h,
			"exp_per_hour": exp_per_h,
			"duration": duration,
			"kills_metin": kills_metin,
			"kills_boss": kills_boss,
			"kills_total": kills_total,
			"exp_gained": exp_gained,
		}

	def CompareSessions(self, sessionA, sessionB, mode=None):
		"""Zestawia i porownuje dwie sesje, wyliczajac delty wskaznikow i roznice w dropie."""
		metricsA = self.CalculateSnapshotMetrics(sessionA, mode)
		metricsB = self.CalculateSnapshotMetrics(sessionB, mode)

		delta_total = metricsB["total_value"] - metricsA["total_value"]
		delta_rate = metricsB["yang_per_hour"] - metricsA["yang_per_hour"]
		if metricsA["yang_per_hour"] > 0:
			delta_rate_pct = (float(delta_rate) / float(metricsA["yang_per_hour"])) * 100.0
		else:
			delta_rate_pct = 0.0

		delta_metins_rate = metricsB["metin_per_hour"] - metricsA["metin_per_hour"]
		delta_bosses = metricsB["kills_boss"] - metricsA["kills_boss"]
		delta_exp_rate = metricsB["exp_per_hour"] - metricsA["exp_per_hour"]

		itemsA = sessionA.get("items", {})
		itemsB = sessionB.get("items", {})
		all_vnums = set([int(k) for k in itemsA.keys()] + [int(k) for k in itemsB.keys()])

		drop_comparison = []
		for vnum in all_vnums:
			infoA = itemsA.get(str(vnum), {})
			infoB = itemsB.get(str(vnum), {})
			cntA = int(infoA.get("count", 0))
			cntB = int(infoB.get("count", 0))
			delta_cnt = cntB - cntA

			price = self.GetItemPrice(vnum, mode)
			valA = cntA * price
			valB = cntB * price
			delta_val = valB - valA

			drop_comparison.append({
				"vnum": vnum,
				"count_a": cntA,
				"count_b": cntB,
				"delta_count": delta_cnt,
				"price": price,
				"val_a": valA,
				"val_b": valB,
				"delta_val": delta_val,
			})

		drop_comparison.sort(key=lambda x: abs(x["delta_val"]), reverse=True)

		return {
			"metricsA": metricsA,
			"metricsB": metricsB,
			"delta_total": delta_total,
			"delta_rate": delta_rate,
			"delta_rate_pct": delta_rate_pct,
			"delta_metins_rate": delta_metins_rate,
			"delta_bosses": delta_bosses,
			"delta_exp_rate": delta_exp_rate,
			"drops": drop_comparison,
		}
