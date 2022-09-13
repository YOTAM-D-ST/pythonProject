"""
    yotam shavit client
"""

# mouduls
import wx
from OOPclient1 import *
from constants1 import *

# constants
FIRST_PAR = 0
SECOND_PAR = 1
BORDER = 5


class GUI(wx.Frame):
    # constructor
    def __init__(self):
        super(GUI, self).__init__(None, title='server technicen',
                                  size=(300, 250))

        # client object
        self.client = None

        # list of params
        self.params = []

        # combo box
        self.combo_box = None

        self.InitUI()

    def InitUI(self):
        # initiate all the the objects in the users interface

        # creates menu bar
        menu_bar = wx.MenuBar()
        # add a menu
        file_menu = wx.Menu()
        # wx.ID_EXIT = once the menu item is clicked the windows closes
        menu_item = file_menu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        # appeand the item to the menu
        menu_bar.Append(file_menu, 'Menu&')
        # sets the menu bar to be a Frame object
        self.SetMenuBar(menu_bar)
        # bind the quit button to the OnQuit function that quit the gui
        self.Bind(wx.EVT_MENU, self.OnQuit, menu_item)

        # creation of panel
        pnl = wx.Panel(self)
        # static box
        sb = wx.StaticBox(pnl, label='Parameters')
        # box sizer
        sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)

        # The param 1 text
        text_one = wx.StaticText(pnl, label='Param 1')
        # The param 2 text
        text_two = wx.StaticText(pnl, label='Param 2')
        # The first parameter box
        param_one = wx.TextCtrl(pnl)
        # The second parameter box
        param_two = wx.TextCtrl(pnl)
        # We append the first parameter box
        self.params.append(param_one)
        # We append the second parameter box
        self.params.append(param_two)
        # Add the first text to the vertical box
        sbs.Add(text_one)
        # Add the first text box (TextCtrl)
        # flag = The orientation
        # border = distance from orientation point
        sbs.Add(self.params[FIRST_PAR], flag=wx.LEFT, border=BORDER)
        # Add the second text
        sbs.Add(text_two)
        # Add the second text box
        sbs.Add(self.params[SECOND_PAR], flag=wx.LEFT, border=BORDER)
        # Set this static box sizer to be the one we just created
        pnl.SetSizer(sbs)

        # list of commands
        com = \
            ['DIR', 'TAKE_SCREENSHOT', 'SEND_FILE', 'DELETE', 'COPY',
             'EXECUTE', 'HISTORY', 'EXIT']
        # Static text above the menu
        wx.StaticText(pnl, pos=(130, 50), label="command")
        # a combo box
        self.combo_box = \
            wx.ComboBox(pnl, pos=(130, 70), choices=com, style=wx.CB_READONLY)

        # Create button
        cbtn = wx.Button(pnl, label='Send', pos=(140, 150))
        # Binds the method to the button when pressed
        cbtn.Bind(wx.EVT_BUTTON, self.on_send)

        self.client = Client(IP, PORT)

        self.Center()
        self.Show(True)

    def OnQuit(self, event):
        """
        when the user pressing the quit button
        the event is called and the gui is closed
        """
        self.Close()
        self.client.c.close()

    def on_send(self, event):
        """
        send user command chosen to server when the event
        of pressing the send button is happening
        """
        command = self.combo_box.GetStringSelection()
        parone = self.params[FIRST_PAR].GetLineText(FIRST_PAR)
        partwo = self.params[SECOND_PAR].GetLineText(FIRST_PAR)

        if parone.strip(' ') == "" and partwo.strip(' ') == "":
            response = self.client.send_command(command)
        elif parone.strip(' ') == "":
            response = \
                self.client.send_command(command + ' ' + parone.strip(' '))
        else:
            hold = command + ' ' + parone.strip(' ') + ' ' + partwo.strip(' ')
            response = \
                self.client.send_command(hold)
        wx.MessageBox(response, 'Response', wx.OK | wx.ICON_INFORMATION)


def main():
    """
    main
    """
    ex = wx.App()
    GUI()
    ex.MainLoop()


if __name__ == '__main__':
    main()
