# MT2Plus: Zdalne NPC (Remote NPC Window)
# Python 2.7 as the client has it; texts are CP1250 escapes so the file stays pure ASCII.
import ui
import net
import wndMgr
import uiToolTip
import chat
import player

NPC_LIST = [
	("Handlarka R\xf3\xbfno\x9cci", 9003, "Otwiera sklep Handlarki R\xf3\xbfno\x9cci (mikstury, przedmioty codzienne)."),
	("Handlarz Broni\xb9", 9001, "Otwiera sklep Handlarza Broni\xb9 (podstawowy or\xea\xbf dla klas)."),
	("Handlarz Zbroj\xb9", 9002, "Otwiera sklep Handlarza Zbroj\xb9 (zbroje, tarcze, he\xb3my)."),
	("Heuk-Young", 20090, "Otwiera bezpo\x9arednio okno wytwarzania Heuk-Younga."),
	("Dozorca / Magazyn", 9005, "Otwiera menu Dozorcy (Magazyn, IS, Sztabki, Wytwarzanie)."),
	("Alchemik", 20001, "Otwiera menu Alchemika (Sklep, Alchemia, Kryszta\xb3 Energii)."),
	("Uriel", 20011, "Otwiera dialog i zadania u m\xeadrca Uriela."),
]

class RemoteNPCWindow(ui.BoardWithTitleBar):
	def __init__(self):
		ui.BoardWithTitleBar.__init__(self)
		self.tooltip = uiToolTip.ToolTip()
		self.buttons = []
		self._BuildUI()

	def __del__(self):
		ui.BoardWithTitleBar.__del__(self)

	def Destroy(self):
		self.buttons = []
		self.tooltip = None
		self.Hide()

	def _BuildUI(self):
		self.SetSize(230, 320)
		self.AddFlag("movable")
		self.AddFlag("float")
		self.SetTitleName("Zdalne NPC")
		self.SetCloseEvent(self.Close)

		btnY = 38
		for name, vnum, desc in NPC_LIST:
			btn = ui.Button()
			btn.SetParent(self)
			btn.SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
			btn.SetOverVisual("d:/ymir work/ui/public/large_button_02.sub")
			btn.SetDownVisual("d:/ymir work/ui/public/large_button_03.sub")
			btn.SetPosition((230 - 88) / 2, btnY)
			btn.SetText(name)
			btn.SetEvent(lambda v=vnum: self.__OnClickNPC(v))
			btn.SetShowToolTipEvent(self.__OnOverIn, desc)
			btn.SetHideToolTipEvent(self.__OnOverOut)
			btn.Show()
			self.buttons.append(btn)
			btnY += 38

		self.SetCenterPosition()

	def __OnOverIn(self, text):
		if self.tooltip:
			self.tooltip.ClearToolTip()
			self.tooltip.AutoAppendTextLine(text)
			self.tooltip.AlignHorizonalCenter()
			self.tooltip.ShowToolTip()

	def __OnOverOut(self):
		if self.tooltip:
			self.tooltip.HideToolTip()

	def __OnClickNPC(self, vnum):
		self.__OnOverOut()
		if player.GetStatus(player.HP) <= 0:
			chat.AppendChat(chat.CHAT_TYPE_INFO, "Nie mo\xbfesz korzysta\xe6 ze zdalnego NPC b\xead\xb9c martwym.")
			return
		net.SendChatPacket("/remote_npc " + str(vnum))
		self.Close()

	def Open(self):
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def Close(self):
		self.__OnOverOut()
		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True


_remoteNPCWindow = None

def ToggleWindow():
	global _remoteNPCWindow
	if not _remoteNPCWindow:
		_remoteNPCWindow = RemoteNPCWindow()
	if _remoteNPCWindow.IsShow():
		_remoteNPCWindow.Close()
	else:
		_remoteNPCWindow.Open()
