import app
import chr
import item
import localeInfo
import nonplayer
import player
import ui
import uiCommon
import uiToolTip
import wndMgr
from farmsession import FarmSessionManager, FormatNumber, FormatTime, MODE_MARKET, MODE_NPC

try:
	long
except NameError:
	long = int

try:
	xrange
except NameError:
	xrange = range

# Kolory stylu Metin2
COLOR_GOLD = 0xFFFFD700
COLOR_TITLE = 0xFFE5D4A3
COLOR_TEXT_NORMAL = 0xFFE0E0E0
COLOR_TEXT_DIM = 0xFF888888
COLOR_TEXT_MUTED = 0xFF555555
COLOR_GREEN = 0xFF85E085
COLOR_ORANGE = 0xFFFFA040

ROW_HEIGHT = 42
VISIBLE_ROWS = 9
PANEL_WIDTH = 620
PANEL_HEIGHT = 490


def ParseMoneyInput(text):
	"""Przelicza wprowadzony tekst z obsluga k, kk, m na kwote Yang."""
	if not text:
		return 0
	clean = str(text).strip().lower().replace(" ", "").replace(".", "").replace(",", "")
	multiplier = 1
	if clean.endswith("kkk") or clean.endswith("b"):
		multiplier = 1000000000
		clean = clean[:-3] if clean.endswith("kkk") else clean[:-1]
	elif clean.endswith("kk") or clean.endswith("m"):
		multiplier = 1000000
		clean = clean[:-2] if clean.endswith("kk") else clean[:-1]
	elif clean.endswith("k"):
		multiplier = 1000
		clean = clean[:-1]
	try:
		return max(0, long(float(clean) * multiplier))
	except Exception:
		return 0


def SetModeButtonVisual(button, selected):
	"""Ustawia stan wcisniety/niewcisniety dla przycisku wyboru trybu."""
	if selected:
		button.Down()
		button.SetTextColor(COLOR_GOLD)
	else:
		button.SetUp()
		button.SetTextColor(COLOR_TEXT_NORMAL)
	if hasattr(button, "ButtonText") and button.ButtonText:
		button.ButtonText.SetPosition(button.GetWidth() / 2, button.GetHeight() / 2)


class DropRow(ui.Window):
	"""Pojedynczy wiersz zebranego przedmiotu na liscie."""
	def __init__(self, parent, session, on_edit_price, on_toggle_hide):
		ui.Window.__init__(self)
		self.parent = parent
		self.session = session
		self.on_edit_price = on_edit_price
		self.on_toggle_hide = on_toggle_hide
		self.vnum = 0
		self.count = 0
		self.price = 0
		self.is_hidden = False

		self.SetSize(370, ROW_HEIGHT - 2)

		# Tlo wiersza
		self.bg = ui.Bar()
		self.bg.SetParent(self)
		self.bg.SetPosition(0, 0)
		self.bg.SetSize(370, ROW_HEIGHT - 2)
		self.bg.SetColor(0xFF1E1B18)
		self.bg.Show()

		# Tlo slotu przedmiotu
		self.slotBg = ui.ImageBox()
		self.slotBg.SetParent(self)
		self.slotBg.SetPosition(4, 3)
		self.slotBg.LoadImage("d:/ymir work/ui/public/slot_base.sub")
		self.slotBg.Show()

		# Ikona przedmiotu (ExpandedImageBox dla poprawnego skalowania 2- i 3-slotowych broni/zbroi)
		self.itemIcon = ui.ExpandedImageBox()
		self.itemIcon.SetParent(self.slotBg)
		self.itemIcon.SetPosition(0, 0)
		self.itemIcon.Show()

		# Obszar najazdu myszki na ikone dla dymka przedmiotu
		self.slotHover = ui.Window()
		self.slotHover.SetParent(self)
		self.slotHover.SetPosition(4, 3)
		self.slotHover.SetSize(32, 32)
		self.slotHover.Show()

		# Nazwa i ilosc: np. "39x Zlote zapiecie"
		self.nameText = ui.TextLine()
		self.nameText.SetParent(self)
		self.nameText.SetPosition(44, 6)
		self.nameText.SetPackedFontColor(COLOR_TEXT_NORMAL)
		self.nameText.SetText("")
		self.nameText.Show()

		# Wartosc sumaryczna w Yang
		self.valueText = ui.TextLine()
		self.valueText.SetParent(self)
		self.valueText.SetPosition(44, 22)
		self.valueText.SetPackedFontColor(COLOR_GOLD)
		self.valueText.SetText("")
		self.valueText.Show()

		# Przycisk Cena (edycja wlasnej ceny rynkowej)
		self.priceBtn = ui.Button()
		self.priceBtn.SetParent(self)
		self.priceBtn.SetPosition(248, 8)
		self.priceBtn.SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
		self.priceBtn.SetOverVisual("d:/ymir work/ui/public/small_button_02.sub")
		self.priceBtn.SetDownVisual("d:/ymir work/ui/public/small_button_03.sub")
		self.priceBtn.SetText("Cena")
		self.priceBtn.SetEvent(ui.__mem_func__(self.__OnEditPrice))
		self.priceBtn.Show()

		# Przycisk Wyklucz / Wlicz (pelna szerokosc, czytelny napis bez nachodzenia)
		self.hideBtn = ui.Button()
		self.hideBtn.SetParent(self)
		self.hideBtn.SetPosition(296, 8)
		self.hideBtn.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		self.hideBtn.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		self.hideBtn.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		self.hideBtn.SetText("Wyklucz")
		self.hideBtn.SetEvent(ui.__mem_func__(self.__OnToggleHide))
		self.hideBtn.Show()

	def SetData(self, vnum, count, is_hidden):
		self.vnum = vnum
		self.count = count
		self.is_hidden = is_hidden

		# Ustawienie ikony i nazwy
		try:
			item.SelectItem(vnum)
			name = item.GetItemName()
			icon = item.GetIconImageFileName()
			self.itemIcon.SetScale(1.0, 1.0)
			self.itemIcon.LoadImage(icon)
			w = self.itemIcon.GetWidth()
			h = self.itemIcon.GetHeight()
			if w > 32 or h > 32:
				biggest = max(w, h)
				scale = 30.0 / float(biggest)
				self.itemIcon.SetScale(scale, scale)
				self.itemIcon.SetPosition(int((32 - w * scale) / 2), int((32 - h * scale) / 2))
			else:
				self.itemIcon.SetScale(1.0, 1.0)
				self.itemIcon.SetPosition(0, 0)
		except Exception:
			name = "Przedmiot %d" % vnum

		self.nameText.SetText("%dx %s" % (count, name))

		# Obliczenie wartosci pozycji w zaleznosci od biezacego trybu (Rynkowa / NPC)
		mode = self.session.GetPriceMode()
		pricePerUnit = self.session.GetItemPrice(vnum, mode)
		self.price = pricePerUnit * long(count)

		if is_hidden:
			self.bg.SetColor(0xFF141210)
			self.nameText.SetPackedFontColor(COLOR_TEXT_MUTED)
			self.valueText.SetPackedFontColor(COLOR_TEXT_MUTED)
			self.valueText.SetText("Wykluczony z sumy")
			self.hideBtn.SetText("Wlicz")
		else:
			self.bg.SetColor(0xFF1E1B18)
			self.nameText.SetPackedFontColor(COLOR_TEXT_NORMAL)
			self.hideBtn.SetText("Wyklucz")

			if pricePerUnit > 0:
				if mode == MODE_NPC:
					self.valueText.SetPackedFontColor(COLOR_ORANGE)
					self.valueText.SetText("%s Yang (NPC netto)" % localeInfo.MoneyFormat(self.price))
				else:
					self.valueText.SetPackedFontColor(COLOR_GOLD)
					self.valueText.SetText("%s Yang" % localeInfo.MoneyFormat(self.price))
			else:
				self.valueText.SetPackedFontColor(COLOR_TEXT_DIM)
				self.valueText.SetText("Cena nieznana (kliknij Cena)")

	def __OnEditPrice(self):
		if self.vnum and self.on_edit_price:
			self.on_edit_price(self.vnum)

	def __OnToggleHide(self):
		if self.vnum and self.on_toggle_hide:
			self.on_toggle_hide(self.vnum)

	def OnUpdate(self):
		if self.slotHover.IsIn():
			if self.vnum:
				self.parent.ShowItemToolTip(self.vnum)
		else:
			if self.parent.curHoverVnum == self.vnum:
				self.parent.HideItemToolTip()


class FarmSessionWindow(ui.BoardWithTitleBar):
	"""Glowne okno Sesji Farmienia."""
	def __init__(self):
		ui.BoardWithTitleBar.__init__(self)
		self.session = FarmSessionManager.Instance()
		self.curHoverVnum = 0
		self.tooltipItem = uiToolTip.ItemToolTip()
		self.tooltipItem.HideToolTip()
		self.inputDialog = None
		self.filterQuery = ""
		self.showHiddenOnly = False
		self.scrollIndex = 0
		self.rows = []
		self.hudWindow = None

		self.__BuildUI()
		self.session.RegisterCallback(self.OnSessionUpdated)

	def __del__(self):
		ui.BoardWithTitleBar.__del__(self)
		self.session.UnregisterCallback(self.OnSessionUpdated)

	def Close(self):
		if self.inputDialog:
			self.inputDialog.Close()
			self.inputDialog = None
		self.HideItemToolTip()
		self.Hide()

	def Destroy(self):
		self.Close()
		self.session.UnregisterCallback(self.OnSessionUpdated)
		self.tooltipItem = None
		self.rows = []

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def SetHUD(self, hud):
		self.hudWindow = hud

	def __BuildUI(self):
		self.SetSize(PANEL_WIDTH, PANEL_HEIGHT)
		self.SetCenterPosition()
		self.AddFlag("movable")
		self.AddFlag("float")
		self.SetTitleName("Sesja Farmienia")
		self.SetCloseEvent(ui.__mem_func__(self.Close))

		# ---------------- HEADER (Pasek narzedzi) ----------------
		headerY = 34

		# Zegar i stoper
		self.timerTitle = ui.TextLine()
		self.timerTitle.SetParent(self)
		self.timerTitle.SetPosition(18, headerY + 4)
		self.timerTitle.SetPackedFontColor(COLOR_TITLE)
		self.timerTitle.SetText("Czas:")
		self.timerTitle.Show()

		self.timerText = ui.TextLine()
		self.timerText.SetParent(self)
		self.timerText.SetPosition(56, headerY + 4)
		self.timerText.SetPackedFontColor(COLOR_GOLD)
		self.timerText.SetText("00:00:00")
		self.timerText.Show()

		# Przycisk Pauza / Wznow
		self.pauseBtn = ui.Button()
		self.pauseBtn.SetParent(self)
		self.pauseBtn.SetPosition(120, headerY)
		self.pauseBtn.SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
		self.pauseBtn.SetOverVisual("d:/ymir work/ui/public/small_button_02.sub")
		self.pauseBtn.SetDownVisual("d:/ymir work/ui/public/small_button_03.sub")
		self.pauseBtn.SetText("Wstrzymaj")
		self.pauseBtn.SetEvent(ui.__mem_func__(self.__OnTogglePause))
		self.pauseBtn.Show()

		# Przycisk Reset
		self.resetBtn = ui.Button()
		self.resetBtn.SetParent(self)
		self.resetBtn.SetPosition(166, headerY)
		self.resetBtn.SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
		self.resetBtn.SetOverVisual("d:/ymir work/ui/public/small_button_02.sub")
		self.resetBtn.SetDownVisual("d:/ymir work/ui/public/small_button_03.sub")
		self.resetBtn.SetText("Reset")
		self.resetBtn.SetEvent(ui.__mem_func__(self.__OnReset))
		self.resetBtn.Show()

		# Pasek wyszukiwania
		self.searchLabel = ui.TextLine()
		self.searchLabel.SetParent(self)
		self.searchLabel.SetPosition(220, headerY + 4)
		self.searchLabel.SetPackedFontColor(COLOR_TITLE)
		self.searchLabel.SetText("Szukaj:")
		self.searchLabel.Show()

		self.searchBox = ui.Bar()
		self.searchBox.SetParent(self)
		self.searchBox.SetPosition(266, headerY + 1)
		self.searchBox.SetSize(180, 20)
		self.searchBox.SetColor(0xFF141210)
		self.searchBox.Show()

		self.searchEdit = ui.EditLine()
		self.searchEdit.SetParent(self.searchBox)
		self.searchEdit.SetPosition(4, 3)
		self.searchEdit.SetSize(172, 16)
		self.searchEdit.SetMax(24)
		self.searchEdit.SetText("")
		self.searchEdit.Show()

		# Przycisk przelaczania widoku ukrytych
		self.viewFilterBtn = ui.Button()
		self.viewFilterBtn.SetParent(self)
		self.viewFilterBtn.SetPosition(454, headerY)
		self.viewFilterBtn.SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
		self.viewFilterBtn.SetOverVisual("d:/ymir work/ui/public/small_button_02.sub")
		self.viewFilterBtn.SetDownVisual("d:/ymir work/ui/public/small_button_03.sub")
		self.viewFilterBtn.SetText("Filtry")
		self.viewFilterBtn.SetEvent(ui.__mem_func__(self.__OnToggleViewFilter))
		self.viewFilterBtn.Show()

		# Przycisk przelaczenia na mini-HUD
		self.hudToggleBtn = ui.Button()
		self.hudToggleBtn.SetParent(self)
		self.hudToggleBtn.SetPosition(500, headerY)
		self.hudToggleBtn.SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
		self.hudToggleBtn.SetOverVisual("d:/ymir work/ui/public/small_button_02.sub")
		self.hudToggleBtn.SetDownVisual("d:/ymir work/ui/public/small_button_03.sub")
		self.hudToggleBtn.SetText("Mini HUD")
		self.hudToggleBtn.SetEvent(ui.__mem_func__(self.__OnToggleHUD))
		self.hudToggleBtn.Show()

		# Przycisk Udostepnij na czat
		self.shareBtn = ui.Button()
		self.shareBtn.SetParent(self)
		self.shareBtn.SetPosition(548, headerY)
		self.shareBtn.SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
		self.shareBtn.SetOverVisual("d:/ymir work/ui/public/small_button_02.sub")
		self.shareBtn.SetDownVisual("d:/ymir work/ui/public/small_button_03.sub")
		self.shareBtn.SetText("Czat")
		self.shareBtn.SetEvent(ui.__mem_func__(self.__OnShareChat))
		self.shareBtn.Show()

		# ---------------- LEWY PANEL (Zrodla i Finanse) ----------------
		leftX = 14
		startY = 68

		self.leftBg = ui.ThinBoard()
		self.leftBg.SetParent(self)
		self.leftBg.SetPosition(leftX, startY)
		self.leftBg.SetSize(186, PANEL_HEIGHT - startY - 14)
		self.leftBg.Show()

		# Kafelki zrodel
		self.cardAll = self.__CreateStatCard(10, 8, "Wszystkie zrodla:", "0")
		self.cardMetin = self.__CreateStatCard(10, 48, "Kamienie Metin:", "0")
		self.cardBoss = self.__CreateStatCard(10, 88, "Pokonani Bossowie:", "0")
		self.cardExp = self.__CreateStatCard(10, 128, "Zdobyty EXP:", "0")

		# Przelacznik trybu wyceny: Rynkowa vs NPC
		self.lblModeTitle = self.__CreateText(10, 170, "Tryb wyceny:", COLOR_TITLE)

		self.btnModeMarket = ui.RadioButton()
		self.btnModeMarket.SetParent(self.leftBg)
		self.btnModeMarket.SetPosition(20, 188)
		self.btnModeMarket.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		self.btnModeMarket.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		self.btnModeMarket.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		self.btnModeMarket.SetText("Rynkowa")
		self.btnModeMarket.SetEvent(ui.__mem_func__(self.__OnSelectMarketMode))
		self.btnModeMarket.Show()

		self.btnModeNPC = ui.RadioButton()
		self.btnModeNPC.SetParent(self.leftBg)
		self.btnModeNPC.SetPosition(105, 188)
		self.btnModeNPC.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		self.btnModeNPC.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		self.btnModeNPC.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		self.btnModeNPC.SetText("NPC")
		self.btnModeNPC.SetEvent(ui.__mem_func__(self.__OnSelectNPCMode))
		self.btnModeNPC.Show()

		# Sekcja finansowa
		finY = 222
		self.lblRawYang = self.__CreateText(10, finY, "Surowe Yang:", COLOR_TITLE)
		self.valRawYang = self.__CreateText(10, finY + 14, "0 Yang", COLOR_TEXT_NORMAL)

		self.lblLoot = self.__CreateText(10, finY + 34, "Wartosc lupow (Rynkowa):", COLOR_TITLE)
		self.valLoot = self.__CreateText(10, finY + 48, "0 Yang", COLOR_TEXT_NORMAL)

		self.lblTotal = self.__CreateText(10, finY + 70, "Szacowana wartosc:", COLOR_GOLD)
		self.valTotal = self.__CreateText(10, finY + 84, "0 Yang", COLOR_GOLD)

		# Tempo zarobku i metinow (Propozycja 1 i 4)
		self.lblRateTitle = self.__CreateText(10, finY + 108, "Tempo sesji:", COLOR_TITLE)
		self.valYangRate = self.__CreateText(10, finY + 122, "~0 Yang / h", COLOR_GREEN)
		self.valMetinRate = self.__CreateText(10, finY + 138, "~0 Metin / h", COLOR_GREEN)
		self.valExpRate = self.__CreateText(10, finY + 154, "~0 EXP / h", COLOR_GREEN)

		# ---------------- PRAWY PANEL (Lista zdobytych lupow) ----------------
		rightX = 208
		rightWidth = PANEL_WIDTH - rightX - 14

		self.rightBg = ui.ThinBoard()
		self.rightBg.SetParent(self)
		self.rightBg.SetPosition(rightX, startY)
		self.rightBg.SetSize(rightWidth, PANEL_HEIGHT - startY - 14)
		self.rightBg.Show()

		# Scrollbar dla listy
		self.scrollBar = ui.ScrollBar()
		self.scrollBar.SetParent(self.rightBg)
		self.scrollBar.SetPosition(rightWidth - 18, 6)
		self.scrollBar.SetScrollBarSize(PANEL_HEIGHT - startY - 26)
		self.scrollBar.SetScrollEvent(ui.__mem_func__(self.__OnScroll))
		self.scrollBar.Show()

		# Wiersze listy
		self.rowContainer = ui.Window()
		self.rowContainer.SetParent(self.rightBg)
		self.rowContainer.SetPosition(6, 6)
		self.rowContainer.SetSize(rightWidth - 26, PANEL_HEIGHT - startY - 26)
		self.rowContainer.Show()

		for i in xrange(VISIBLE_ROWS):
			row = DropRow(self, self.session, self.OpenPriceDialog, self.ToggleHideItem)
			row.SetParent(self.rowContainer)
			row.SetPosition(0, i * ROW_HEIGHT)
			row.Hide()
			self.rows.append(row)

		self.Refresh()

	def __CreateStatCard(self, x, y, title, val):
		card = ui.Bar()
		card.SetParent(self.leftBg)
		card.SetPosition(x, y)
		card.SetSize(166, 36)
		card.SetColor(0xFF1B1815)
		card.Show()

		tLabel = ui.TextLine()
		tLabel.SetParent(card)
		tLabel.SetPosition(6, 3)
		tLabel.SetPackedFontColor(COLOR_TITLE)
		tLabel.SetText(title)
		tLabel.Show()

		tVal = ui.TextLine()
		tVal.SetParent(card)
		tVal.SetPosition(6, 17)
		tVal.SetPackedFontColor(COLOR_GOLD)
		tVal.SetText(val)
		tVal.Show()
		return (card, tLabel, tVal)

	def __CreateText(self, x, y, text, color):
		line = ui.TextLine()
		line.SetParent(self.leftBg)
		line.SetPosition(x, y)
		line.SetPackedFontColor(color)
		line.SetText(text)
		line.Show()
		return line

	def __OnSelectMarketMode(self):
		self.session.SetPriceMode(MODE_MARKET)

	def __OnSelectNPCMode(self):
		self.session.SetPriceMode(MODE_NPC)

	def ShowItemToolTip(self, vnum):
		self.curHoverVnum = vnum
		self.tooltipItem.ClearToolTip()
		self.tooltipItem.AddItemData(vnum, 0, 0)
		self.tooltipItem.ShowToolTip()

	def HideItemToolTip(self):
		self.curHoverVnum = 0
		self.tooltipItem.HideToolTip()

	def __OnTogglePause(self):
		self.session.TogglePause()
		self.pauseBtn.SetText("Wznow" if self.session.is_paused else "Wstrzymaj")

	def __OnReset(self):
		self.session.Reset()
		self.pauseBtn.SetText("Wstrzymaj")

	def __OnToggleViewFilter(self):
		self.showHiddenOnly = not self.showHiddenOnly
		self.viewFilterBtn.SetText("Ukryte" if self.showHiddenOnly else "Filtry")
		self.RefreshList()

	def __OnToggleHUD(self):
		if self.hudWindow:
			self.hudWindow.Show()
			self.Hide()

	def __OnShareChat(self):
		"""Wysyla podsumowanie sesji na czat gry."""
		durationStr = FormatTime(self.session.GetDuration())
		metins = self.session.kills_metin
		bosses = self.session.kills_boss
		modeStr = "Rynkowa" if self.session.GetPriceMode() == MODE_MARKET else "NPC"
		totalVal = localeInfo.MoneyFormat(self.session.GetTotalValue())
		rateStr = localeInfo.MoneyFormat(self.session.GetYangPerHour())
		msg = "[Sesja Farmienia] Czas: %s | Metiny: %d | Bossy: %d | Zarobek (%s): %s Yang (~%s/h)" % (
			durationStr, metins, bosses, modeStr, totalVal, rateStr
		)
		import chat
		chat.AppendChat(chat.CHAT_TYPE_INFO, msg)

	def OpenPriceDialog(self, vnum):
		"""Otwiera dialog wprowadzenia wlasnej ceny za sztuke."""
		try:
			item.SelectItem(vnum)
			itemName = item.GetItemName()
		except Exception:
			itemName = "Przedmiot %d" % vnum

		dlg = uiCommon.InputDialog()
		dlg.SetTitle("Wycena rynkowa: %s" % itemName)
		dlg.SetMaxLength(18)
		curPrice = self.session.GetItemPrice(vnum, MODE_MARKET)
		dlg.SetText(str(curPrice) if curPrice > 0 else "")

		def OnAccept():
			text = dlg.GetText()
			newPrice = ParseMoneyInput(text)
			self.session.SetCustomPrice(vnum, newPrice)
			dlg.Close()
			self.inputDialog = None

		def OnCancel():
			dlg.Close()
			self.inputDialog = None

		dlg.SetAcceptEvent(OnAccept)
		dlg.SetCancelEvent(OnCancel)
		dlg.Open()
		self.inputDialog = dlg

	def ToggleHideItem(self, vnum):
		self.session.ToggleItemHidden(vnum)

	def __OnScroll(self):
		items = self.GetFilteredItems()
		maxScroll = max(0, len(items) - VISIBLE_ROWS)
		self.scrollIndex = int(round(self.scrollBar.GetPos() * maxScroll))
		self.RefreshList()

	def OnRunMouseWheel(self, length):
		if length > 0:
			self.scrollBar.OnUp()
		else:
			self.scrollBar.OnDown()
		return True

	def GetFilteredItems(self):
		"""Zwraca posortowana liste (vnum, count, hidden) pasujaca do filtra wyszukiwania."""
		query = self.searchEdit.GetText().strip().lower()
		result = []
		for vnum, data in self.session.items.items():
			count = data.get("count", 0)
			hidden = data.get("hidden", False)

			if self.showHiddenOnly and not hidden:
				continue

			if query:
				try:
					item.SelectItem(vnum)
					name = item.GetItemName().lower()
				except Exception:
					name = ""
				if query not in name and query not in str(vnum):
					continue

			result.append((vnum, count, hidden))

		# Sortowanie malejaco po lacznej wartosci danej pozycji w biezacym trybie
		mode = self.session.GetPriceMode()
		def SortKey(itemTuple):
			v, cnt, h = itemTuple
			return self.session.GetItemPrice(v, mode) * long(cnt)

		result.sort(key=SortKey, reverse=True)
		return result

	def RefreshList(self):
		items = self.GetFilteredItems()
		totalCount = len(items)
		maxScroll = max(0, totalCount - VISIBLE_ROWS)

		if maxScroll > 0:
			self.scrollBar.Show()
			self.scrollBar.SetMiddleBarSize(float(VISIBLE_ROWS) / float(totalCount))
		else:
			self.scrollBar.Hide()
			self.scrollIndex = 0

		visible = items[self.scrollIndex:self.scrollIndex + VISIBLE_ROWS]
		for i in xrange(VISIBLE_ROWS):
			row = self.rows[i]
			if i < len(visible):
				vnum, cnt, hidden = visible[i]
				row.SetData(vnum, cnt, hidden)
				row.Show()
			else:
				row.Hide()

	def Refresh(self):
		mode = self.session.GetPriceMode()

		# Wizualizacja przyciskow wyboru trybu
		SetModeButtonVisual(self.btnModeMarket, mode == MODE_MARKET)
		SetModeButtonVisual(self.btnModeNPC, mode == MODE_NPC)

		# Odswiezenie licznikow w lewym panelu
		self.cardAll[2].SetText(FormatNumber(self.session.kills_total))
		self.cardMetin[2].SetText(str(self.session.kills_metin))
		self.cardBoss[2].SetText(str(self.session.kills_boss))
		self.cardExp[2].SetText("%s EXP" % FormatNumber(self.session.exp_gained))

		# Sekcja finansowa
		self.valRawYang.SetText("%s Yang" % localeInfo.MoneyFormat(self.session.GetRawYang()))

		if mode == MODE_NPC:
			self.lblLoot.SetText("Wartosc lupow (NPC -3%):")
			self.lblTotal.SetText("Lacznie (NPC netto):")
		else:
			self.lblLoot.SetText("Wartosc lupow (Rynkowa):")
			self.lblTotal.SetText("Szacowana wartosc:")

		self.valLoot.SetText("%s Yang" % localeInfo.MoneyFormat(self.session.GetItemsValue()))
		self.valTotal.SetText("%s Yang" % localeInfo.MoneyFormat(self.session.GetTotalValue()))

		# Wskazniki tempa sesji (Propozycja 1 i 4)
		yangRate = self.session.GetYangPerHour()
		metinRate = self.session.GetMetinsPerHour()
		expRate = self.session.GetExpPerHour()

		self.valYangRate.SetText("~%s Yang / h" % FormatNumber(yangRate))
		self.valMetinRate.SetText("~%.1f Metin / h" % metinRate)
		self.valExpRate.SetText("~%s EXP / h" % FormatNumber(expRate))

		self.RefreshList()

	def OnSessionUpdated(self):
		self.Refresh()

	def OnUpdate(self):
		# Aktualizacja stopera w naglowku
		self.timerText.SetText(FormatTime(self.session.GetDuration()))

		# Odswiezenie filtra w czasie rzeczywistym
		query = self.searchEdit.GetText()
		if query != self.filterQuery:
			self.filterQuery = query
			self.scrollIndex = 0
			self.RefreshList()


class FarmSessionHUD(ui.ThinBoard):
	"""Kompaktowy mini-widzet HUD (Propozycja 2)."""
	def __init__(self, mainWindow):
		ui.ThinBoard.__init__(self)
		self.mainWindow = mainWindow
		self.session = FarmSessionManager.Instance()
		self.SetSize(176, 52)
		self.SetPosition(wndMgr.GetScreenWidth() - 180, 200)
		self.AddFlag("movable")
		self.AddFlag("float")

		self.title = ui.TextLine()
		self.title.SetParent(self)
		self.title.SetPosition(8, 6)
		self.title.SetPackedFontColor(COLOR_TITLE)
		self.title.SetText("Sesja:")
		self.title.Show()

		self.timerText = ui.TextLine()
		self.timerText.SetParent(self)
		self.timerText.SetPosition(48, 6)
		self.timerText.SetPackedFontColor(COLOR_GOLD)
		self.timerText.SetText("00:00:00")
		self.timerText.Show()

		self.totalText = ui.TextLine()
		self.totalText.SetParent(self)
		self.totalText.SetPosition(8, 20)
		self.totalText.SetPackedFontColor(COLOR_GOLD)
		self.totalText.SetText("0 Yang")
		self.totalText.Show()

		self.rateText = ui.TextLine()
		self.rateText.SetParent(self)
		self.rateText.SetPosition(8, 34)
		self.rateText.SetPackedFontColor(COLOR_GREEN)
		self.rateText.SetText("~0 / h")
		self.rateText.Show()

		# Przycisk otwarcia pelnego okna
		self.expandBtn = ui.Button()
		self.expandBtn.SetParent(self)
		self.expandBtn.SetPosition(144, 6)
		self.expandBtn.SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
		self.expandBtn.SetOverVisual("d:/ymir work/ui/public/small_button_02.sub")
		self.expandBtn.SetDownVisual("d:/ymir work/ui/public/small_button_03.sub")
		self.expandBtn.SetText("^")
		self.expandBtn.SetEvent(ui.__mem_func__(self.__OnExpand))
		self.expandBtn.Show()

		# Przycisk pauzy
		self.pauseBtn = ui.Button()
		self.pauseBtn.SetParent(self)
		self.pauseBtn.SetPosition(144, 28)
		self.pauseBtn.SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
		self.pauseBtn.SetOverVisual("d:/ymir work/ui/public/small_button_02.sub")
		self.pauseBtn.SetDownVisual("d:/ymir work/ui/public/small_button_03.sub")
		self.pauseBtn.SetText("||")
		self.pauseBtn.SetEvent(ui.__mem_func__(self.__OnTogglePause))
		self.pauseBtn.Show()

		self.Hide()

	def Destroy(self):
		self.Hide()
		self.mainWindow = None

	def __OnExpand(self):
		self.Hide()
		if self.mainWindow:
			self.mainWindow.Show()

	def __OnTogglePause(self):
		self.session.TogglePause()
		self.pauseBtn.SetText(">" if self.session.is_paused else "||")

	def OnUpdate(self):
		self.timerText.SetText(FormatTime(self.session.GetDuration()))
		self.totalText.SetText("%s Yang" % FormatNumber(self.session.GetTotalValue()))
		self.rateText.SetText("~%s / h" % FormatNumber(self.session.GetYangPerHour()))
