import wx
import pygame
import serial.tools.list_ports
import time

class MainFrame(wx.Frame):
    def __init__(self,parent,ptitle):
        wx.Frame.__init__(self,parent,title=ptitle)
        self.selectedPort = None
        pygame.init()
        size = [500,700]
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption("Joystick Monitor")
        pygame.init()
        pygame.joystick.init()
        self.ser = None
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
        ports = serial.tools.list_ports.comports()
        self.portsbox = wx.ComboBox(panel,pos=(40,8))
        for pt in ports:
            self.portsbox.AppendItems(pt.device)

        self.connbtn = wx.BitmapButton(panel,bitmap=wx.Bitmap('conn-icon.png',wx.BITMAP_TYPE_ANY),size=(102,24),pos=(160,6.8))
        self.Bind(wx.EVT_BUTTON, self.OnConn,self.connbtn)
        self.disconnbtn = wx.BitmapButton(panel,bitmap=wx.Bitmap('discon-icon.png',wx.BITMAP_TYPE_ANY),size=(102,24),pos=(160,6.8))
        self.disconnbtn.Hide()
        self.Bind(wx.EVT_BUTTON, self.OnDisconn,self.disconnbtn)
        self.connTxt = wx.StaticText(panel,label="Connected: None",pos=(270,10))

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

        clock = pygame.time.Clock()
        textPrint = TextPrint()
        self.coorx = 0
        self.coory = 0
        self.coorz = 0

        while done==False:
            if jpanel.textBox.GetNumberOfLines()>40:
                jpanel.textBox.SetValue("");
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    done=True

                if event.type==pygame.JOYBUTTONDOWN:
                    print("Joystick button presed.")
                    jpanel.textBox.SetValue(jpanel.textBox.GetValue()+"pressed\n")
                if event.type==pygame.JOYBUTTONUP:
                    print("Joystick button released.")
                if event.type==pygame.JOYAXISMOTION:
                    if event.axis==0:
                        self.coory = event.value
                    elif event.axis==1:
                        self.coorx = event.value
                    if abs(event.value)>0.5:
                        jpanel.textBox.SetValue(jpanel.textBox.GetValue()+"{} and {}\n".format(event.axis,event.value))
                            
            self.SendMSG()

            self.screen.fill((255,255,255))
            textPrint.reset()
            joystick_count=pygame.joystick.get_count()
            textPrint.print(self.screen, "Number of joysticks: {}".format(joystick_count))
            textPrint.indent()

            for i in range(joystick_count):
                joystick=pygame.joystick.Joystick(i)
                joystick.init()
 
                textPrint.print(self.screen,"Joystick {}".format(i))
                textPrint.indent()

                name=joystick.get_name()
                textPrint.print(self.screen, "Joystick name: {}".format(name))

                axes=joystick.get_numaxes()
                textPrint.print(self.screen, "Number of axes: {}".format(axes))
                textPrint.indent()

                for i in range(axes):
                    axis=joystick.get_axis(i)
                    textPrint.print(self.screen,"Axis {}value: {:>6.3f}".format(i,axis))
                textPrint.unindent()

                buttons=joystick.get_numbuttons()
                textPrint.print(self.screen, "Number of buttons: {}".format(buttons))
                textPrint.indent()

                for i in range(buttons):
                    button=joystick.get_button(i)
                    textPrint.print(self.screen, "Button {:>2} value: {}".format(i,button))
                textPrint.unindent()

                hats=joystick.get_numhats()
                textPrint.print(self.screen, "Number of hats: {}".format(hats))
                textPrint.indent()

                for i in range(hats):
                    hat=joystick.get_hat(i)
                    textPrint.print(self.screen, "Hat {} value: {}".format(i, str(hat)))
                textPrint.unindent()

                textPrint.unindent()

            pygame.display.flip()

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
        print("Connected: "+self.portsbox.GetStringSelection())
        if(self.portsbox.GetStringSelection()!=""):
            self.connTxt.SetLabel("Connected: "+self.portsbox.GetStringSelection())
            self.selectedPort = self.portsbox.GetStringSelection()
            self.ser = serial.Serial(self.selectedPort,9600,timeout=1)
            self.connbtn.Hide()
            self.disconnbtn.Show()
        else:
            wx.MessageBox('กรุณาเลือก Port','Error',wx.OK|wx.ICON_INFORMATION)
        
    def OnDisconn(self,e):
        print("Disconnected: "+self.selectedPort)
        self.connTxt.SetLabel("Connected: None")
        self.ser.close()
        self.selectedPort = None
        self.ser = None
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

    def SendMSG(self):
        if(self.coorx>0.5):
            if self.ser!=None:
                self.ser.write("G1 X1 Y0\n".encode())
                time.sleep(0.5)
            print("G1 X1 Y0")
        if(self.coorx<-0.5):
            if self.ser!=None:
                self.ser.write("G1 X-1 Y0\n".encode())
                time.sleep(0.5)
            print("G1 X-1 Y0")
        if(self.coory<-0.5):
            if self.ser!=None:
                self.ser.write("G1 X0 Y1\n".encode())
                time.sleep(0.5)
            print("G1 X0 Y1")
        if(self.coory>0.5):
            if self.ser!=None:
                self.ser.write("G1 X0 Y-1\n".encode())
                time.sleep(0.5)
            print("G1 X0 Y-1")

class JoystickPanel(wx.Panel):
    def __init__(self,parent,*args,**kwargs):
        wx.Panel.__init__(self,parent,*args,**kwargs)
        self.SetBackgroundColour((255,255,255))
        self.textBox = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(340,565))

class TextPrint:
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None,20)

    def print(self, screen, textString):
        textBitmap = self.font.render(textString, True,(0,0,0))
        screen.blit(textBitmap, [self.x, self.y])
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

