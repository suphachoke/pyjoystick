import wx
import pygame
import serial.tools.list_ports

class MainFrame(wx.Frame):
    def __init__(self,parent,ptitle):
        wx.Frame.__init__(self,parent,title=ptitle)
        self.selectedPort = None
        pygame.init()
        pygame.joystick.init()
        self.InitUI()

    def InitUI(self):
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        mquit = wx.MenuItem(fileMenu,101,'&Quit\tCtrl+Q','Quit the Application')
        mquit.SetBitmap(wx.Image('door_exit.png',wx.BITMAP_TYPE_PNG).ConvertToBitmap())
        fileMenu.Append(mquit)
        fileMenu.AppendSeparator()
        menubar.Append(fileMenu,'&File')
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnQuit,mquit)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        panel = wx.Panel(self)
        label = wx.StaticText(panel,label="Port: ",pos=(10,10))
        ports = list(serial.tools.list_ports.comports())
        self.portsbox = wx.ComboBox(panel,choices=ports,pos=(40,8))

        self.connbtn = wx.BitmapButton(panel,bitmap=wx.Bitmap('conn-icon.png',wx.BITMAP_TYPE_ANY),size=(102,24),pos=(160,6.8))
        self.Bind(wx.EVT_BUTTON, self.OnConn,self.connbtn)
        self.disconnbtn = wx.BitmapButton(panel,bitmap=wx.Bitmap('discon-icon.png',wx.BITMAP_TYPE_ANY),size=(102,24),pos=(160,6.8))
        self.disconnbtn.Hide()
        self.Bind(wx.EVT_BUTTON, self.OnDisconn,self.disconnbtn)

        self.newfbtn = wx.BitmapButton(panel,bitmap=wx.Bitmap('new-file.png',wx.BITMAP_TYPE_ANY),size=(30,30),pos=(40,35))
        self.openfbtn = wx.BitmapButton(panel,bitmap=wx.Bitmap('open-file.png',wx.BITMAP_TYPE_ANY),size=(30,30),pos=(80,35))
        self.recbtn = wx.BitmapButton(panel,bitmap=wx.Bitmap('record.png',wx.BITMAP_TYPE_ANY),size=(30,30),pos=(120,35))
        self.stopbtn = wx.BitmapButton(panel,bitmap=wx.Bitmap('stop.ico',wx.BITMAP_TYPE_ANY),size=(30,30),pos=(160,35))
        self.Bind(wx.EVT_BUTTON, self.OnNewf, self.newfbtn)
        self.Bind(wx.EVT_BUTTON, self.OnOpenf, self.openfbtn)
        self.Bind(wx.EVT_BUTTON, self.DoRecordStart, self.recbtn)
        self.Bind(wx.EVT_BUTTON, self.DoRecordStop, self.stopbtn)
                
        jpanel = JoystickPanel(panel,pos=(500,10),size=(340,565))

        self.SetSize((860,640))
        self.Centre()
        self.Show()

        done = False

        textPrint = TextPrint()
        joystick_count=pygame.joystick.get_count()
        clock = pygame.time.Clock()
        textPrint.print(jpanel, "Number of joysticks: {}".format(joystick_count))
        textPrint.indent()
        while done==False:
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    done=True

                if event.type==pygame.JOYBUTTONDOWN:
                    print("Joystick button presed.")
                if event.type==pygame.JOYBUTTONUP:
                    print("Joystick button released.")

            textPrint.reset()

            for i in range(joystick_count):
                joystick=pygame.joystick.Joystick(i)
                joystick.init()

                textPrint.print(jpanel,"Joystick {}".format(i))
                textPrint.indent()

                name=joystick.get_name()
                textPrint.print(jpanel, "Joystick name: {}".format(name))

                axes=joystick.get_numaxes()
                textPrint.print(jpanel, "Number of axes: {}".format(axes))
                textPrint.indent()

                for i in range(axes):
                    axis=joystick.get_axis(i)
                    textPrint.print(jpanel,"Axis {}value: {:>6.3f}".format(i,axis))
                textPrint.unindent()

                buttons=joystick.get_numbuttons()
                textPrint.print(jpanel, "Number of buttons: {}".format(buttons))
                textPrint.indent()

                for i in range(buttons):
                    button=joystick.get_button(i)
                    textPrint.print(jpanel, "Button {:>2} value: {}".format(i,button))
                textPrint.unindent()

                hats=joystick.get_numhats()
                textPrint.print(jpanel, "Number of hats: {}".format(hats))
                textPrint.indent()

                for i in range(hats):
                    hat=joystick.get_hat(i)
                    textPrint.print(jpanel, "Hat {} value: {}".format(i, str(hat)))
                textPrint.unindent()

                textPrint.unindent()

            clock.tick(20)

    def OnQuit(self,e):
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        self.Close()

    def OnCloseWindow(self,e):
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        self.Destroy()

    def OnConn(self,e):
        print("disconnect:"+self.portsbox.GetStringSelection())
        if(self.portsbox.GetStringSelection()!=""):
            self.selectedPort = self.portsbox.GetStringSelection()
            self.connbtn.Hide()
            self.disconnbtn.Show()
        else:
            wx.MessageBox('กรุณาเลือก Port','Error',wx.OK|wx.ICON_INFORMATION)
        
    def OnDisconn(self,e):
        print("connect")
        self.selectedPort = None
        self.connbtn.Show()
        self.disconnbtn.Hide()

    def OnOpenf(self,e):
        with wx.FileDialog(self, "Open recorded file", wildcard="Text files (*.txt)|*.txt",style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal()==wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'r+') as file:
                    self.DoLoadFile(file)
            except IOError:
                wx.LogError("Cannot open file '%s'." % pathname)

    def OnNewf(self,e):
        with wx.FileDialog(self, "Create new file", wildcard="Text files (*.txt)|*.txt",style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal()==wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'w') as file:
                    self.DoLoadFile(file)
            except IOError:
                wx.LogError("Cannot save current data in file '%s'." % pathname)

    def DoLoadFile(self,f):
        self.logFile = f
        print(self.logFile)

    def DoRecordStart(self,e):
        self.recFlag = True
        print(self.logFile)

    def DoRecordStop(self,e):
        self.recFlag = False
        try:
            print(self.logFile)
            self.logFile.close()
        except:
            print('No file')

class JoystickPanel(wx.Panel):
    def __init__(self,parent,*args,**kwargs):
        wx.Panel.__init__(self,parent,*args,**kwargs)
        self.SetBackgroundColour((255,255,255))

class TextPrint:
    def __init__(self):
        self.reset()

    def print(self, panel, textString):
        wx.StaticText(panel,label=textString, pos=[self.x, self.y])
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10

if __name__=='__main__':
    ex = wx.App(False)
    MainFrame(None,'Esan3D - Controller')  
    ex.MainLoop()

