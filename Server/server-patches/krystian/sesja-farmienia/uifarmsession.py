import app
import chr
import chat
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
COLOR_RED = 0xFFFF6060
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
		self.compareWindow = None

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
		if self.compareWindow:
			self.compareWindow.Destroy()
			self.compareWindow = None

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
		self.cardAll = self.__CreateStatCard(10, 6, "Wszystkie zrodla:", "0")
		self.cardMetin = self.__CreateStatCard(10, 42, "Kamienie Metin:", "0")
		self.cardBoss = self.__CreateStatCard(10, 78, "Pokonani Bossowie:", "0")
		self.cardExp = self.__CreateStatCard(10, 114, "Zdobyty EXP:", "0")

		# Przelacznik trybu wyceny: Rynkowa vs NPC
		self.lblModeTitle = self.__CreateText(10, 152, "Tryb wyceny:", COLOR_TITLE)

		self.btnModeMarket = ui.RadioButton()
		self.btnModeMarket.SetParent(self.leftBg)
		self.btnModeMarket.SetPosition(20, 168)
		self.btnModeMarket.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		self.btnModeMarket.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		self.btnModeMarket.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		self.btnModeMarket.SetText("Rynkowa")
		if hasattr(self.btnModeMarket, "ButtonText") and self.btnModeMarket.ButtonText:
			self.btnModeMarket.ButtonText.SetPosition(self.btnModeMarket.GetWidth() / 2, self.btnModeMarket.GetHeight() / 2)
		self.btnModeMarket.SetEvent(ui.__mem_func__(self.__OnSelectMarketMode))
		self.btnModeMarket.Show()

		self.btnModeNPC = ui.RadioButton()
		self.btnModeNPC.SetParent(self.leftBg)
		self.btnModeNPC.SetPosition(105, 168)
		self.btnModeNPC.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		self.btnModeNPC.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		self.btnModeNPC.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		self.btnModeNPC.SetText("NPC")
		if hasattr(self.btnModeNPC, "ButtonText") and self.btnModeNPC.ButtonText:
			self.btnModeNPC.ButtonText.SetPosition(self.btnModeNPC.GetWidth() / 2, self.btnModeNPC.GetHeight() / 2)
		self.btnModeNPC.SetEvent(ui.__mem_func__(self.__OnSelectNPCMode))
		self.btnModeNPC.Show()

		# Sekcja finansowa
		finY = 196
		self.lblRawYang = self.__CreateText(10, finY, "Surowe Yang:", COLOR_TITLE)
		self.valRawYang = self.__CreateText(10, finY + 13, "0 Yang", COLOR_TEXT_NORMAL)

		self.lblLoot = self.__CreateText(10, finY + 29, "Wartosc lupow (Rynkowa):", COLOR_TITLE)
		self.valLoot = self.__CreateText(10, finY + 42, "0 Yang", COLOR_TEXT_NORMAL)

		self.lblTotal = self.__CreateText(10, finY + 59, "Szacowana wartosc:", COLOR_GOLD)
		self.valTotal = self.__CreateText(10, finY + 72, "0 Yang", COLOR_GOLD)

		# Tempo zarobku i metinow (Propozycja 1 i 4)
		self.lblRateTitle = self.__CreateText(10, finY + 92, "Tempo sesji:", COLOR_TITLE)
		self.valYangRate = self.__CreateText(10, finY + 105, "~0 Yang / h", COLOR_GREEN)
		self.valMetinRate = self.__CreateText(10, finY + 119, "~0 Metin / h", COLOR_GREEN)
		self.valExpRate = self.__CreateText(10, finY + 133, "~0 EXP / h", COLOR_GREEN)

		# Zarzadzanie sesja (Zapisz / Porownaj)
		self.lblSessionTitle = self.__CreateText(10, 350, "Zarzadzanie sesja:", COLOR_TITLE)

		self.btnSaveSession = ui.Button()
		self.btnSaveSession.SetParent(self.leftBg)
		self.btnSaveSession.SetPosition(20, 370)
		self.btnSaveSession.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		self.btnSaveSession.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		self.btnSaveSession.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		self.btnSaveSession.SetText("Zapisz")
		if hasattr(self.btnSaveSession, "ButtonText") and self.btnSaveSession.ButtonText:
			self.btnSaveSession.ButtonText.SetPosition(self.btnSaveSession.GetWidth() / 2, self.btnSaveSession.GetHeight() / 2)
		self.btnSaveSession.SetEvent(ui.__mem_func__(self.OpenSaveDialog))
		self.btnSaveSession.Show()

		self.btnCompare = ui.Button()
		self.btnCompare.SetParent(self.leftBg)
		self.btnCompare.SetPosition(105, 370)
		self.btnCompare.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		self.btnCompare.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		self.btnCompare.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		self.btnCompare.SetText("Porownaj")
		if hasattr(self.btnCompare, "ButtonText") and self.btnCompare.ButtonText:
			self.btnCompare.ButtonText.SetPosition(self.btnCompare.GetWidth() / 2, self.btnCompare.GetHeight() / 2)
		self.btnCompare.SetEvent(ui.__mem_func__(self.OpenCompareWindow))
		self.btnCompare.Show()

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
		priceStr = str(curPrice) if curPrice > 0 else ""

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
		if hasattr(dlg, "SetText"):
			dlg.SetText(priceStr)
		if hasattr(dlg, "inputValue") and dlg.inputValue:
			dlg.inputValue.SetText(priceStr)
		self.inputDialog = dlg

	def ToggleHideItem(self, vnum):
		self.session.ToggleItemHidden(vnum)

	def OpenSaveDialog(self):
		"""Otwiera dialog zapisu biezacej sesji z sugerowana nazwa mapy."""
		defaultName = self.session.GetDefaultSessionName()

		dlg = uiCommon.InputDialog()
		dlg.SetTitle("Zapisz Sesje Farmienia")
		dlg.SetMaxLength(40)

		def OnAccept():
			name = dlg.GetText().strip()
			if not name:
				name = defaultName
			self.session.SaveSession(name)
			dlg.Close()
			self.inputDialog = None
			chat.AppendChat(chat.CHAT_TYPE_INFO, "[Sesja Farmienia] Pomyslnie zapisano sesje: %s" % name)
			if self.compareWindow and self.compareWindow.IsShow():
				self.compareWindow.RefreshSessions()

		def OnCancel():
			dlg.Close()
			self.inputDialog = None

		dlg.SetAcceptEvent(OnAccept)
		dlg.SetCancelEvent(OnCancel)
		dlg.Open()
		if hasattr(dlg, "SetText"):
			dlg.SetText(defaultName)
		if hasattr(dlg, "inputValue") and dlg.inputValue:
			try:
				dlg.inputValue.SetText(defaultName)
			except Exception:
				pass
		self.inputDialog = dlg

	def OpenCompareWindow(self):
		"""Otwiera okno porownania sesji farmienia."""
		if not self.compareWindow:
			self.compareWindow = FarmSessionCompareWindow(self.session)
		self.compareWindow.RefreshSessions()
		self.compareWindow.Show()
		self.compareWindow.SetTop()

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


# =====================================================================
# MODUL POROWNYWANIA SESJI FARMIENIA (FARM SESSION COMPARISON VIEW)
# =====================================================================

COMPARE_PANEL_WIDTH = 680
COMPARE_PANEL_HEIGHT = 530
COMPARE_VISIBLE_ROWS = 7
COMPARE_ROW_HEIGHT = 38


class CompareDropRow(ui.Window):
	"""Pojedynczy wiersz porownania dropu pomiedzy sesja A a sesja B."""
	def __init__(self, parent):
		ui.Window.__init__(self)
		self.parent = parent
		self.vnum = 0
		self.countA = 0
		self.countB = 0
		self.deltaCount = 0
		self.deltaVal = 0

		self.SetSize(620, 36)

		# Tlo wiersza
		self.bg = ui.Bar()
		self.bg.SetParent(self)
		self.bg.SetPosition(0, 0)
		self.bg.SetSize(620, 36)
		self.bg.SetColor(0xFF1E1B18)
		self.bg.Show()

		# Slot przedmiotu
		self.slotBg = ui.ImageBox()
		self.slotBg.SetParent(self)
		self.slotBg.SetPosition(4, 2)
		self.slotBg.LoadImage("d:/ymir work/ui/public/slot_base.sub")
		self.slotBg.Show()

		# Ikona przedmiotu (ExpandedImageBox ze skalowaniem dla 2- i 3-slotowych broni)
		self.itemIcon = ui.ExpandedImageBox()
		self.itemIcon.SetParent(self.slotBg)
		self.itemIcon.SetPosition(0, 0)
		self.itemIcon.Show()

		# Obszar najazdu dla tooltipu przedmiotu
		self.slotHover = ui.Window()
		self.slotHover.SetParent(self)
		self.slotHover.SetPosition(4, 2)
		self.slotHover.SetSize(32, 32)
		self.slotHover.OnMouseOverIn = lambda: self.parent.ShowItemToolTip(self.vnum)
		self.slotHover.OnMouseOverOut = lambda: self.parent.HideItemToolTip()
		self.slotHover.Show()

		# Nazwa przedmiotu
		self.nameText = ui.TextLine()
		self.nameText.SetParent(self)
		self.nameText.SetPosition(42, 10)
		self.nameText.SetPackedFontColor(COLOR_TEXT_NORMAL)
		self.nameText.Show()

		# Ilosc w Sesji A
		self.cntAText = ui.TextLine()
		self.cntAText.SetParent(self)
		self.cntAText.SetPosition(250, 10)
		self.cntAText.SetPackedFontColor(COLOR_TEXT_DIM)
		self.cntAText.Show()

		# Ilosc w Sesji B
		self.cntBText = ui.TextLine()
		self.cntBText.SetParent(self)
		self.cntBText.SetPosition(340, 10)
		self.cntBText.SetPackedFontColor(COLOR_TEXT_NORMAL)
		self.cntBText.Show()

		# Roznica sztuk (Delta Count)
		self.deltaCntText = ui.TextLine()
		self.deltaCntText.SetParent(self)
		self.deltaCntText.SetPosition(430, 10)
		self.deltaCntText.Show()

		# Roznica wartosci w Yang
		self.deltaValText = ui.TextLine()
		self.deltaValText.SetParent(self)
		self.deltaValText.SetPosition(530, 10)
		self.deltaValText.Show()

	def SetData(self, data):
		self.vnum = data.get("vnum", 0)
		self.countA = data.get("count_a", 0)
		self.countB = data.get("count_b", 0)
		self.deltaCount = data.get("delta_count", 0)
		self.deltaVal = data.get("delta_val", 0)

		try:
			item.SelectItem(self.vnum)
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
			name = "Przedmiot %d" % self.vnum

		if len(name) > 24:
			name = name[:22] + ".."
		self.nameText.SetText(name)

		self.cntAText.SetText("%d szt." % self.countA if self.countA > 0 else "-")
		self.cntBText.SetText("%d szt." % self.countB if self.countB > 0 else "-")

		# Format delty ilosci
		if self.deltaCount > 0:
			self.deltaCntText.SetPackedFontColor(COLOR_GREEN)
			self.deltaCntText.SetText("+%d szt." % self.deltaCount)
		elif self.deltaCount < 0:
			self.deltaCntText.SetPackedFontColor(COLOR_RED)
			self.deltaCntText.SetText("%d szt." % self.deltaCount)
		else:
			self.deltaCntText.SetPackedFontColor(COLOR_TEXT_DIM)
			self.deltaCntText.SetText("= 0 szt.")

		# Format delty wartosci w Yang
		if self.deltaVal > 0:
			self.deltaValText.SetPackedFontColor(COLOR_GREEN)
			self.deltaValText.SetText("+%s" % FormatNumber(self.deltaVal))
		elif self.deltaVal < 0:
			self.deltaValText.SetPackedFontColor(COLOR_RED)
			self.deltaValText.SetText("-%s" % FormatNumber(abs(self.deltaVal)))
		else:
			self.deltaValText.SetPackedFontColor(COLOR_TEXT_DIM)
			self.deltaValText.SetText("0 Yang")


class FarmSessionCompareWindow(ui.BoardWithTitleBar):
	"""Okno porownania i analizy dwoch sesji farmienia."""
	def __init__(self, session_manager):
		ui.BoardWithTitleBar.__init__(self)
		self.session = session_manager
		self.sessionList = []
		self.indexA = 0
		self.indexB = 0
		self.price_mode = MODE_MARKET
		self.comparisonData = None
		self.scrollIndex = 0
		self.rows = []
		self.tooltipItem = uiToolTip.ItemToolTip()
		self.tooltipItem.HideToolTip()
		self.inputDialog = None
		self.questionDialog = None

		self.__BuildUI()

	def __del__(self):
		ui.BoardWithTitleBar.__del__(self)

	def Close(self):
		if self.inputDialog:
			self.inputDialog.Close()
			self.inputDialog = None
		if self.questionDialog:
			self.questionDialog.Close()
			self.questionDialog = None
		self.HideItemToolTip()
		self.Hide()

	def Destroy(self):
		self.Close()
		self.tooltipItem = None
		self.rows = []

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def ShowItemToolTip(self, vnum):
		if vnum <= 0:
			return
		self.tooltipItem.ClearToolTip()
		self.tooltipItem.AddItemData(vnum, 0, 0)
		self.tooltipItem.ShowToolTip()

	def HideItemToolTip(self):
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

	def __BuildUI(self):
		self.SetSize(COMPARE_PANEL_WIDTH, COMPARE_PANEL_HEIGHT)
		self.SetCenterPosition()
		self.AddFlag("movable")
		self.AddFlag("float")
		self.SetTitleName("Porownanie Sesji Farmienia")
		self.SetCloseEvent(ui.__mem_func__(self.Close))

		# ---------------- GORNY PASEK WYBORU SESJI ----------------
		# Sesja A (Lewa strona)
		self.boxA = ui.ThinBoard()
		self.boxA.SetParent(self)
		self.boxA.SetPosition(14, 34)
		self.boxA.SetSize(306, 66)
		self.boxA.Show()

		self.titleA = ui.TextLine()
		self.titleA.SetParent(self.boxA)
		self.titleA.SetPosition(10, 6)
		self.titleA.SetPackedFontColor(COLOR_TITLE)
		self.titleA.SetText("Sesja A (Baza / Odniesienie):")
		self.titleA.Show()

		self.btnPrevA = ui.Button()
		self.btnPrevA.SetParent(self.boxA)
		self.btnPrevA.SetPosition(8, 24)
		self.btnPrevA.SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
		self.btnPrevA.SetOverVisual("d:/ymir work/ui/public/small_button_02.sub")
		self.btnPrevA.SetDownVisual("d:/ymir work/ui/public/small_button_03.sub")
		self.btnPrevA.SetText("<")
		if hasattr(self.btnPrevA, "ButtonText") and self.btnPrevA.ButtonText:
			self.btnPrevA.ButtonText.SetPosition(self.btnPrevA.GetWidth() / 2, self.btnPrevA.GetHeight() / 2)
		self.btnPrevA.SetEvent(ui.__mem_func__(self.__OnPrevA))
		self.btnPrevA.Show()

		self.nameTextA = ui.TextLine()
		self.nameTextA.SetParent(self.boxA)
		self.nameTextA.SetPosition(56, 26)
		self.nameTextA.SetPackedFontColor(COLOR_GOLD)
		self.nameTextA.SetText("---")
		self.nameTextA.Show()

		self.btnNextA = ui.Button()
		self.btnNextA.SetParent(self.boxA)
		self.btnNextA.SetPosition(256, 24)
		self.btnNextA.SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
		self.btnNextA.SetOverVisual("d:/ymir work/ui/public/small_button_02.sub")
		self.btnNextA.SetDownVisual("d:/ymir work/ui/public/small_button_03.sub")
		self.btnNextA.SetText(">")
		if hasattr(self.btnNextA, "ButtonText") and self.btnNextA.ButtonText:
			self.btnNextA.ButtonText.SetPosition(self.btnNextA.GetWidth() / 2, self.btnNextA.GetHeight() / 2)
		self.btnNextA.SetEvent(ui.__mem_func__(self.__OnNextA))
		self.btnNextA.Show()

		self.infoTextA = ui.TextLine()
		self.infoTextA.SetParent(self.boxA)
		self.infoTextA.SetPosition(10, 46)
		self.infoTextA.SetPackedFontColor(COLOR_TEXT_DIM)
		self.infoTextA.SetText("Czas: 00:00:00")
		self.infoTextA.Show()

		# Przycisk zamiany sesji (<>)
		self.btnSwap = ui.Button()
		self.btnSwap.SetParent(self)
		self.btnSwap.SetPosition(326, 52)
		self.btnSwap.SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
		self.btnSwap.SetOverVisual("d:/ymir work/ui/public/small_button_02.sub")
		self.btnSwap.SetDownVisual("d:/ymir work/ui/public/small_button_03.sub")
		self.btnSwap.SetText("<>")
		if hasattr(self.btnSwap, "ButtonText") and self.btnSwap.ButtonText:
			self.btnSwap.ButtonText.SetPosition(self.btnSwap.GetWidth() / 2, self.btnSwap.GetHeight() / 2)
		self.btnSwap.SetEvent(ui.__mem_func__(self.__OnSwap))
		self.btnSwap.Show()

		# Sesja B (Prawa strona)
		self.boxB = ui.ThinBoard()
		self.boxB.SetParent(self)
		self.boxB.SetPosition(360, 34)
		self.boxB.SetSize(306, 66)
		self.boxB.Show()

		self.titleB = ui.TextLine()
		self.titleB.SetParent(self.boxB)
		self.titleB.SetPosition(10, 6)
		self.titleB.SetPackedFontColor(COLOR_TITLE)
		self.titleB.SetText("Sesja B (Porownywana):")
		self.titleB.Show()

		self.btnPrevB = ui.Button()
		self.btnPrevB.SetParent(self.boxB)
		self.btnPrevB.SetPosition(8, 24)
		self.btnPrevB.SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
		self.btnPrevB.SetOverVisual("d:/ymir work/ui/public/small_button_02.sub")
		self.btnPrevB.SetDownVisual("d:/ymir work/ui/public/small_button_03.sub")
		self.btnPrevB.SetText("<")
		if hasattr(self.btnPrevB, "ButtonText") and self.btnPrevB.ButtonText:
			self.btnPrevB.ButtonText.SetPosition(self.btnPrevB.GetWidth() / 2, self.btnPrevB.GetHeight() / 2)
		self.btnPrevB.SetEvent(ui.__mem_func__(self.__OnPrevB))
		self.btnPrevB.Show()

		self.nameTextB = ui.TextLine()
		self.nameTextB.SetParent(self.boxB)
		self.nameTextB.SetPosition(56, 26)
		self.nameTextB.SetPackedFontColor(COLOR_GOLD)
		self.nameTextB.SetText("---")
		self.nameTextB.Show()

		self.btnNextB = ui.Button()
		self.btnNextB.SetParent(self.boxB)
		self.btnNextB.SetPosition(256, 24)
		self.btnNextB.SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
		self.btnNextB.SetOverVisual("d:/ymir work/ui/public/small_button_02.sub")
		self.btnNextB.SetDownVisual("d:/ymir work/ui/public/small_button_03.sub")
		self.btnNextB.SetText(">")
		if hasattr(self.btnNextB, "ButtonText") and self.btnNextB.ButtonText:
			self.btnNextB.ButtonText.SetPosition(self.btnNextB.GetWidth() / 2, self.btnNextB.GetHeight() / 2)
		self.btnNextB.SetEvent(ui.__mem_func__(self.__OnNextB))
		self.btnNextB.Show()

		self.infoTextB = ui.TextLine()
		self.infoTextB.SetParent(self.boxB)
		self.infoTextB.SetPosition(10, 46)
		self.infoTextB.SetPackedFontColor(COLOR_TEXT_DIM)
		self.infoTextB.SetText("Czas: 00:00:00")
		self.infoTextB.Show()

		# ---------------- SRODKOWE KARTY METRYK (KPI) ----------------
		kpiY = 106
		cardW = 157
		self.cardRate = self.__CreateKPICard(14, kpiY, cardW, 68, "Tempo zarobku:")
		self.cardTotal = self.__CreateKPICard(179, kpiY, cardW, 68, "Laczny zysk (Yang):")
		self.cardMetin = self.__CreateKPICard(344, kpiY, cardW, 68, "Metiny / godz.:")
		self.cardExp = self.__CreateKPICard(509, kpiY, cardW, 68, "Bossy & EXP / h:")

		# ---------------- TABELA DROPÓW (ZESTAWIENIE ŁUPÓW) ----------------
		headerY = 180
		self.tableHeader = ui.Bar()
		self.tableHeader.SetParent(self)
		self.tableHeader.SetPosition(14, headerY)
		self.tableHeader.SetSize(652, 22)
		self.tableHeader.SetColor(0xFF141210)
		self.tableHeader.Show()

		self.lblColItem = self.__CreateHeaderLabel(20, 4, "Przedmiot", COLOR_TITLE)
		self.lblColA = self.__CreateHeaderLabel(250, 4, "Sesja A", COLOR_TITLE)
		self.lblColB = self.__CreateHeaderLabel(340, 4, "Sesja B", COLOR_TITLE)
		self.lblColDiffCnt = self.__CreateHeaderLabel(430, 4, "Roznica sztuk", COLOR_TITLE)
		self.lblColDiffVal = self.__CreateHeaderLabel(530, 4, "Roznica Yang", COLOR_TITLE)

		# Kontener listy dropów
		tableY = 204
		self.tableBg = ui.ThinBoard()
		self.tableBg.SetParent(self)
		self.tableBg.SetPosition(14, tableY)
		self.tableBg.SetSize(652, 282)
		self.tableBg.Show()

		self.scrollBar = ui.ScrollBar()
		self.scrollBar.SetParent(self.tableBg)
		self.scrollBar.SetPosition(634, 6)
		self.scrollBar.SetScrollBarSize(270)
		self.scrollBar.SetScrollEvent(ui.__mem_func__(self.__OnScroll))
		self.scrollBar.Show()

		self.rowContainer = ui.Window()
		self.rowContainer.SetParent(self.tableBg)
		self.rowContainer.SetPosition(6, 6)
		self.rowContainer.SetSize(624, 270)
		self.rowContainer.Show()

		for i in xrange(COMPARE_VISIBLE_ROWS):
			row = CompareDropRow(self)
			row.SetParent(self.rowContainer)
			row.SetPosition(0, i * COMPARE_ROW_HEIGHT)
			row.Hide()
			self.rows.append(row)

		# ---------------- DOLNY PASEK AKCJI (FOOTER) ----------------
		footerY = 494

		self.lblFooterMode = ui.TextLine()
		self.lblFooterMode.SetParent(self)
		self.lblFooterMode.SetPosition(18, footerY + 4)
		self.lblFooterMode.SetPackedFontColor(COLOR_TITLE)
		self.lblFooterMode.SetText("Wycena:")
		self.lblFooterMode.Show()

		self.btnModeMarket = ui.RadioButton()
		self.btnModeMarket.SetParent(self)
		self.btnModeMarket.SetPosition(70, footerY)
		self.btnModeMarket.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		self.btnModeMarket.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		self.btnModeMarket.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		self.btnModeMarket.SetText("Rynkowa")
		if hasattr(self.btnModeMarket, "ButtonText") and self.btnModeMarket.ButtonText:
			self.btnModeMarket.ButtonText.SetPosition(self.btnModeMarket.GetWidth() / 2, self.btnModeMarket.GetHeight() / 2)
		self.btnModeMarket.SetEvent(ui.__mem_func__(self.__OnSelectMarketMode))
		self.btnModeMarket.Show()

		self.btnModeNPC = ui.RadioButton()
		self.btnModeNPC.SetParent(self)
		self.btnModeNPC.SetPosition(140, footerY)
		self.btnModeNPC.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		self.btnModeNPC.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		self.btnModeNPC.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		self.btnModeNPC.SetText("NPC")
		if hasattr(self.btnModeNPC, "ButtonText") and self.btnModeNPC.ButtonText:
			self.btnModeNPC.ButtonText.SetPosition(self.btnModeNPC.GetWidth() / 2, self.btnModeNPC.GetHeight() / 2)
		self.btnModeNPC.SetEvent(ui.__mem_func__(self.__OnSelectNPCMode))
		self.btnModeNPC.Show()

		self.btnRenameB = ui.Button()
		self.btnRenameB.SetParent(self)
		self.btnRenameB.SetPosition(365, footerY)
		self.btnRenameB.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		self.btnRenameB.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		self.btnRenameB.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		self.btnRenameB.SetText("Zmien nazwe")
		if hasattr(self.btnRenameB, "ButtonText") and self.btnRenameB.ButtonText:
			self.btnRenameB.ButtonText.SetPosition(self.btnRenameB.GetWidth() / 2, self.btnRenameB.GetHeight() / 2)
		self.btnRenameB.SetEvent(ui.__mem_func__(self.__OnRenameSessionB))
		self.btnRenameB.Show()

		self.btnDeleteB = ui.Button()
		self.btnDeleteB.SetParent(self)
		self.btnDeleteB.SetPosition(445, footerY)
		self.btnDeleteB.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		self.btnDeleteB.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		self.btnDeleteB.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		self.btnDeleteB.SetText("Usun sesje")
		if hasattr(self.btnDeleteB, "ButtonText") and self.btnDeleteB.ButtonText:
			self.btnDeleteB.ButtonText.SetPosition(self.btnDeleteB.GetWidth() / 2, self.btnDeleteB.GetHeight() / 2)
		self.btnDeleteB.SetEvent(ui.__mem_func__(self.__OnDeleteSessionB))
		self.btnDeleteB.Show()

		self.btnClose = ui.Button()
		self.btnClose.SetParent(self)
		self.btnClose.SetPosition(570, footerY)
		self.btnClose.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		self.btnClose.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		self.btnClose.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		self.btnClose.SetText("Zamknij")
		if hasattr(self.btnClose, "ButtonText") and self.btnClose.ButtonText:
			self.btnClose.ButtonText.SetPosition(self.btnClose.GetWidth() / 2, self.btnClose.GetHeight() / 2)
		self.btnClose.SetEvent(ui.__mem_func__(self.Close))
		self.btnClose.Show()

	def __CreateKPICard(self, x, y, width, height, title):
		bg = ui.Bar()
		bg.SetParent(self)
		bg.SetPosition(x, y)
		bg.SetSize(width, height)
		bg.SetColor(0xFF1B1815)
		bg.Show()

		lblTitle = ui.TextLine()
		lblTitle.SetParent(bg)
		lblTitle.SetPosition(6, 4)
		lblTitle.SetPackedFontColor(COLOR_TITLE)
		lblTitle.SetText(title)
		lblTitle.Show()

		line1 = ui.TextLine()
		line1.SetParent(bg)
		line1.SetPosition(6, 18)
		line1.SetPackedFontColor(COLOR_TEXT_DIM)
		line1.SetText("-")
		line1.Show()

		line2 = ui.TextLine()
		line2.SetParent(bg)
		line2.SetPosition(6, 32)
		line2.SetPackedFontColor(COLOR_TEXT_NORMAL)
		line2.SetText("-")
		line2.Show()

		lineDelta = ui.TextLine()
		lineDelta.SetParent(bg)
		lineDelta.SetPosition(6, 48)
		lineDelta.SetPackedFontColor(COLOR_GREEN)
		lineDelta.SetText("-")
		lineDelta.Show()

		return (bg, lblTitle, line1, line2, lineDelta)

	def __CreateHeaderLabel(self, x, y, text, color):
		label = ui.TextLine()
		label.SetParent(self.tableHeader)
		label.SetPosition(x, y)
		label.SetPackedFontColor(color)
		label.SetText(text)
		label.Show()
		return label

	def RefreshSessions(self):
		"""Odswieza liste sesji do wyboru (Biezaca + Zapisane)."""
		currentSnapshot = self.session.GetSessionSnapshot("[Biezaca sesja]")
		saved = self.session.GetSavedSessions()

		# Indeks 0 = Biezaca sesja, nastepne to zapisane sesje (od najnowszej do najstarszej)
		self.sessionList = [currentSnapshot] + list(reversed(saved))
		totalCount = len(self.sessionList)

		if totalCount > 1:
			if self.indexA >= totalCount:
				self.indexA = 0
			if self.indexB >= totalCount or self.indexB < 0:
				self.indexB = 1
			# Upewniamy sie, ze sesja A i sesja B nie wskazuja na te sama pozycje
			if self.indexA == self.indexB:
				self.indexB = 1 if self.indexA == 0 else 0
		else:
			# Brak zapisanych sesji
			self.indexA = 0
			self.indexB = -1

		self.UpdateComparison()

	def UpdateComparison(self):
		if not self.sessionList:
			return

		totalCount = len(self.sessionList)
		sessionA = self.sessionList[self.indexA]

		# Naglowek Sesji A
		nameA = sessionA.get("name", "Sesja A")
		if len(nameA) > 24:
			nameA = nameA[:22] + ".."
		self.nameTextA.SetText(nameA)
		self.titleA.SetText("Sesja A (%d/%d): [Baza]" % (self.indexA + 1, totalCount))

		durA = FormatTime(sessionA.get("duration", 0))
		dateA = sessionA.get("date", "")
		self.infoTextA.SetText("Czas: %s | %s" % (durA, dateA) if dateA else "Czas: %s" % durA)

		# Jesli brak zapisanych sesji do porownania (indexB == -1)
		if self.indexB < 0 or self.indexB >= totalCount:
			self.titleB.SetText("Sesja B: [Brak zapisanych sesji]")
			self.nameTextB.SetPackedFontColor(COLOR_TEXT_DIM)
			self.nameTextB.SetText("(Brak zapisu)")
			self.infoTextB.SetText("Zapisz sesje przyciskiem 'Zapisz'")

			self.comparisonData = None
			self.cardRate[2].SetText("A: ~%s/h" % FormatNumber(self.session.GetYangPerHour()))
			self.cardRate[3].SetText("B: -")
			self.cardRate[4].SetPackedFontColor(COLOR_TEXT_DIM)
			self.cardRate[4].SetText("Brak sesji do porownania")

			self.cardTotal[2].SetText("A: %s" % FormatNumber(self.session.GetTotalValue()))
			self.cardTotal[3].SetText("B: -")
			self.cardTotal[4].SetPackedFontColor(COLOR_TEXT_DIM)
			self.cardTotal[4].SetText("Zapisz sesje, aby zestawic")

			self.cardMetin[2].SetText("A: ~%.1f / h" % self.session.GetMetinsPerHour())
			self.cardMetin[3].SetText("B: -")
			self.cardMetin[4].SetPackedFontColor(COLOR_TEXT_DIM)
			self.cardMetin[4].SetText("-")

			self.cardExp[2].SetText("Bossy: A: %d | B: -" % self.session.kills_boss)
			self.cardExp[3].SetPackedFontColor(COLOR_TEXT_DIM)
			self.cardExp[3].SetText("-")
			self.cardExp[4].SetPackedFontColor(COLOR_TEXT_DIM)
			self.cardExp[4].SetText("EXP: -")

			SetModeButtonVisual(self.btnModeMarket, self.price_mode == MODE_MARKET)
			SetModeButtonVisual(self.btnModeNPC, self.price_mode == MODE_NPC)

			self.scrollIndex = 0
			self.RefreshList()
			return

		# Prawidlowa sesja B
		self.nameTextB.SetPackedFontColor(COLOR_GOLD)
		sessionB = self.sessionList[self.indexB]
		nameB = sessionB.get("name", "Sesja B")
		if len(nameB) > 24:
			nameB = nameB[:22] + ".."
		self.nameTextB.SetText(nameB)
		self.titleB.SetText("Sesja B (%d/%d): [Porownanie]" % (self.indexB + 1, totalCount))

		durB = FormatTime(sessionB.get("duration", 0))
		dateB = sessionB.get("date", "")
		self.infoTextB.SetText("Czas: %s | %s" % (durB, dateB) if dateB else "Czas: %s" % durB)

		# Obliczenie porownania
		self.comparisonData = self.session.CompareSessions(sessionA, sessionB, self.price_mode)
		metricsA = self.comparisonData["metricsA"]
		metricsB = self.comparisonData["metricsB"]

		# Karta 0: Tempo Zarobku (~Yang/h)
		rateA = metricsA["yang_per_hour"]
		rateB = metricsB["yang_per_hour"]
		deltaRate = self.comparisonData["delta_rate"]
		pct = self.comparisonData["delta_rate_pct"]

		self.cardRate[2].SetText("A: ~%s/h" % FormatNumber(rateA))
		self.cardRate[3].SetText("B: ~%s/h" % FormatNumber(rateB))
		if deltaRate > 0:
			self.cardRate[4].SetPackedFontColor(COLOR_GREEN)
			self.cardRate[4].SetText("+%s/h (+%.1f%%)" % (FormatNumber(deltaRate), pct))
		elif deltaRate < 0:
			self.cardRate[4].SetPackedFontColor(COLOR_RED)
			self.cardRate[4].SetText("-%s/h (%.1f%%)" % (FormatNumber(abs(deltaRate)), pct))
		else:
			self.cardRate[4].SetPackedFontColor(COLOR_TEXT_DIM)
			self.cardRate[4].SetText("= 0/h (0.0%)")

		# Karta 1: Laczny Zysk (Yang)
		totA = metricsA["total_value"]
		totB = metricsB["total_value"]
		deltaTot = self.comparisonData["delta_total"]

		self.cardTotal[2].SetText("A: %s" % FormatNumber(totA))
		self.cardTotal[3].SetText("B: %s" % FormatNumber(totB))
		if deltaTot > 0:
			self.cardTotal[4].SetPackedFontColor(COLOR_GREEN)
			self.cardTotal[4].SetText("+%s Yang" % FormatNumber(deltaTot))
		elif deltaTot < 0:
			self.cardTotal[4].SetPackedFontColor(COLOR_RED)
			self.cardTotal[4].SetText("-%s Yang" % FormatNumber(abs(deltaTot)))
		else:
			self.cardTotal[4].SetPackedFontColor(COLOR_TEXT_DIM)
			self.cardTotal[4].SetText("= 0 Yang")

		# Karta 2: Metiny / godz.
		mRateA = metricsA["metin_per_hour"]
		mRateB = metricsB["metin_per_hour"]
		deltaMRate = self.comparisonData["delta_metins_rate"]

		self.cardMetin[2].SetText("A: ~%.1f / h" % mRateA)
		self.cardMetin[3].SetText("B: ~%.1f / h" % mRateB)
		if deltaMRate > 0.05:
			self.cardMetin[4].SetPackedFontColor(COLOR_GREEN)
			self.cardMetin[4].SetText("+%.1f / h" % deltaMRate)
		elif deltaMRate < -0.05:
			self.cardMetin[4].SetPackedFontColor(COLOR_RED)
			self.cardMetin[4].SetText("%.1f / h" % deltaMRate)
		else:
			self.cardMetin[4].SetPackedFontColor(COLOR_TEXT_DIM)
			self.cardMetin[4].SetText("= 0.0 / h")

		# Karta 3: Bossy & EXP / h
		deltaExp = self.comparisonData["delta_exp_rate"]
		bossA = metricsA["kills_boss"]
		bossB = metricsB["kills_boss"]
		deltaBoss = self.comparisonData["delta_bosses"]

		self.cardExp[2].SetText("Bossy: A: %d | B: %d" % (bossA, bossB))
		if deltaBoss > 0:
			self.cardExp[3].SetPackedFontColor(COLOR_GREEN)
			self.cardExp[3].SetText("Roznica bossow: +%d" % deltaBoss)
		elif deltaBoss < 0:
			self.cardExp[3].SetPackedFontColor(COLOR_RED)
			self.cardExp[3].SetText("Roznica bossow: %d" % deltaBoss)
		else:
			self.cardExp[3].SetPackedFontColor(COLOR_TEXT_DIM)
			self.cardExp[3].SetText("Roznica bossow: 0")

		if deltaExp > 0:
			self.cardExp[4].SetPackedFontColor(COLOR_GREEN)
			self.cardExp[4].SetText("EXP: +%s/h" % FormatNumber(deltaExp))
		elif deltaExp < 0:
			self.cardExp[4].SetPackedFontColor(COLOR_RED)
			self.cardExp[4].SetText("EXP: -%s/h" % FormatNumber(abs(deltaExp)))
		else:
			self.cardExp[4].SetPackedFontColor(COLOR_TEXT_DIM)
			self.cardExp[4].SetText("EXP: = 0/h")

		# Wizualizacja przyciskow trybu wyceny
		SetModeButtonVisual(self.btnModeMarket, self.price_mode == MODE_MARKET)
		SetModeButtonVisual(self.btnModeNPC, self.price_mode == MODE_NPC)

		self.scrollIndex = 0
		self.RefreshList()

	def RefreshList(self):
		if not self.comparisonData:
			for row in self.rows:
				row.Hide()
			return

		drops = self.comparisonData.get("drops", [])
		total = len(drops)

		if total <= COMPARE_VISIBLE_ROWS:
			self.scrollBar.Hide()
		else:
			self.scrollBar.Show()
			self.scrollBar.SetMiddleBarSize(float(COMPARE_VISIBLE_ROWS) / float(total))

		visible = drops[self.scrollIndex : self.scrollIndex + COMPARE_VISIBLE_ROWS]
		for i in xrange(COMPARE_VISIBLE_ROWS):
			row = self.rows[i]
			if i < len(visible):
				row.SetData(visible[i])
				row.Show()
			else:
				row.Hide()

	def __OnScroll(self):
		if not self.comparisonData:
			return
		drops = self.comparisonData.get("drops", [])
		total = len(drops)
		if total <= COMPARE_VISIBLE_ROWS:
			self.scrollIndex = 0
		else:
			pos = self.scrollBar.GetPos()
			self.scrollIndex = int(pos * (total - COMPARE_VISIBLE_ROWS))
		self.RefreshList()

	def OnRunMouseWheel(self, nLen):
		if not self.comparisonData:
			return False
		drops = self.comparisonData.get("drops", [])
		total = len(drops)
		if total <= COMPARE_VISIBLE_ROWS:
			return False
		if nLen > 0:
			self.scrollIndex = max(0, self.scrollIndex - 1)
		else:
			self.scrollIndex = min(total - COMPARE_VISIBLE_ROWS, self.scrollIndex + 1)
		self.scrollBar.SetPos(float(self.scrollIndex) / float(total - COMPARE_VISIBLE_ROWS))
		self.RefreshList()
		return True

	def __OnPrevA(self):
		if len(self.sessionList) <= 1:
			return
		total = len(self.sessionList)
		newIdx = (self.indexA - 1) % total
		if newIdx == self.indexB and total > 1:
			newIdx = (newIdx - 1) % total
		self.indexA = newIdx
		self.UpdateComparison()

	def __OnNextA(self):
		if len(self.sessionList) <= 1:
			return
		total = len(self.sessionList)
		newIdx = (self.indexA + 1) % total
		if newIdx == self.indexB and total > 1:
			newIdx = (newIdx + 1) % total
		self.indexA = newIdx
		self.UpdateComparison()

	def __OnPrevB(self):
		if len(self.sessionList) <= 1 or self.indexB < 0:
			return
		total = len(self.sessionList)
		newIdx = (self.indexB - 1) % total
		if newIdx == self.indexA and total > 1:
			newIdx = (newIdx - 1) % total
		self.indexB = newIdx
		self.UpdateComparison()

	def __OnNextB(self):
		if len(self.sessionList) <= 1 or self.indexB < 0:
			return
		total = len(self.sessionList)
		newIdx = (self.indexB + 1) % total
		if newIdx == self.indexA and total > 1:
			newIdx = (newIdx + 1) % total
		self.indexB = newIdx
		self.UpdateComparison()

	def __OnSwap(self):
		if len(self.sessionList) <= 1 or self.indexB < 0:
			return
		self.indexA, self.indexB = self.indexB, self.indexA
		self.UpdateComparison()

	def __OnSelectMarketMode(self):
		self.price_mode = MODE_MARKET
		self.UpdateComparison()

	def __OnSelectNPCMode(self):
		self.price_mode = MODE_NPC
		self.UpdateComparison()

	def __OnDeleteSessionB(self):
		if not self.sessionList or self.indexB < 0 or self.indexB >= len(self.sessionList):
			chat.AppendChat(chat.CHAT_TYPE_INFO, "[Sesja Farmienia] Brak wybranej sesji do usuniecia.")
			return

		if self.indexB == 0:
			chat.AppendChat(chat.CHAT_TYPE_INFO, "[Sesja Farmienia] Nie mozna usunac biezacej sesji.")
			return

		selected = self.sessionList[self.indexB]
		sessionId = selected.get("id")
		sessionName = selected.get("name", "Sesja")

		dlg = uiCommon.QuestionDialog()
		dlg.SetText("Czy na pewno chcesz usunac sesje:\n'%s'?" % sessionName)

		def OnAccept():
			self.session.DeleteSavedSession(sessionId)
			dlg.Close()
			self.questionDialog = None
			chat.AppendChat(chat.CHAT_TYPE_INFO, "[Sesja Farmienia] Usunieto sesje: %s" % sessionName)
			self.RefreshSessions()

		def OnCancel():
			dlg.Close()
			self.questionDialog = None

		dlg.SetAcceptEvent(OnAccept)
		dlg.SetCancelEvent(OnCancel)
		dlg.Open()
		self.questionDialog = dlg

	def __OnRenameSessionB(self):
		if not self.sessionList or self.indexB < 0 or self.indexB >= len(self.sessionList):
			chat.AppendChat(chat.CHAT_TYPE_INFO, "[Sesja Farmienia] Brak wybranej sesji do zmiany nazwy.")
			return

		selected = self.sessionList[self.indexB]
		isCurrent = (self.indexB == 0)
		sessionId = selected.get("id")
		currentName = selected.get("name", "")

		dlg = uiCommon.InputDialog()
		dlg.SetTitle("Zmien nazwe sesji")
		dlg.SetMaxLength(40)

		def OnAccept():
			newName = dlg.GetText().strip()
			if newName and newName != currentName:
				if isCurrent:
					self.session.SetSessionName(newName)
					chat.AppendChat(chat.CHAT_TYPE_INFO, "[Sesja Farmienia] Zmieniono nazwe biezacej sesji na: %s" % newName)
				else:
					self.session.RenameSavedSession(sessionId, newName)
					chat.AppendChat(chat.CHAT_TYPE_INFO, "[Sesja Farmienia] Zmieniono nazwe na: %s" % newName)
				self.RefreshSessions()
			dlg.Close()
			self.inputDialog = None

		def OnCancel():
			dlg.Close()
			self.inputDialog = None

		dlg.SetAcceptEvent(OnAccept)
		dlg.SetCancelEvent(OnCancel)
		dlg.Open()
		if hasattr(dlg, "SetText"):
			dlg.SetText(currentName)
		if hasattr(dlg, "inputValue") and dlg.inputValue:
			try:
				dlg.inputValue.SetText(currentName)
			except Exception:
				pass
		self.inputDialog = dlg
