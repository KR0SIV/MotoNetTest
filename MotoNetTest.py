from socket import *
from tkinter import *
import configparser
from os import path
import threading
import socket
import time
import re

config = configparser.ConfigParser()
confName = 'MotoNetTestServer'
if path.exists('conf.ini'):
    pass
else:
    config[confName] = {}
    config[confName]['masterIP'] = '127.0.0.1'
    config[confName]['peerIP'] = '127.0.0.2'
    config[confName]['masterUDP'] = '50000'
    config[confName]['restUDP'] = '50001'
    config[confName]['delaySEC'] = '2'
    config[confName]['packetCOUNT'] = '20'
    config[confName]['timeoutSEC'] = '10'

    with open('conf.ini', 'w') as configfile:
        config.write(configfile)

try:
    config.read('conf.ini')
    masterIP = config.get(confName, 'masterIP')
    peerIP = config.get(confName, 'peerIP')
    masterUDP = config.get(confName, 'masterUDP')
    restUDP = config.get(confName, 'restUDP')
    delaySEC = config.get(confName, 'delaySEC')
    packetCOUNT = config.get(confName, 'packetCOUNT')
    timeoutSEC = config.get(confName, 'timeoutSEC')
except:
    config[confName] = {}
    config[confName]['masterIP'] = '127.0.0.1'
    config[confName]['peerIP'] = '127.0.0.2'
    config[confName]['masterUDP'] = '50000'
    config[confName]['restUDP'] = '50001'
    config[confName]['delaySEC'] = '2'
    config[confName]['packetCOUNT'] = '20'
    config[confName]['timeoutSEC'] = '10'

    with open('conf.ini', 'w') as configfile:
        config.write(configfile)

root = Tk()

##GUI FUNCTIONS/BACKEND

def donothing():
    x = 0


def serverThread():
    startbtn.configure(fg='green')
    MasterUDPStatusLabel.configure(text='Listening on ' + masterIP + ':' + masterUDP)
    RestUDPStatusLabel.configure(text='Listening on ' + peerIP + ':' + restUDP)
    t = threading.Thread(target=echoServer)
    t.start()
    startbtn.configure(state=DISABLED)


def clientThread():
    startclientbtn.configure(fg='green')
    MasterUDPStatusLabel.configure(text='Listening on ' + masterIP + ':' + masterUDP)
    RestUDPStatusLabel.configure(text='Listening on ' + peerIP + ':' + restUDP)
    # t = threading.Thread(target=testingServer)
    t = threading.Thread(target=echoClient)
    t.start()
    startclientbtn.configure(state=DISABLED)


def stopThread():
    pass


def clientMode():
    clientbtn.configure(fg='green')
    # startclientbtn = Button(root, text='Start Client', command=clientThread)
    startclientbtn.configure(state=NORMAL)
    # startclientbtn.grid(column=1, row=6)
    serverbtn.configure(state=DISABLED)


def serverMode():
    serverbtn.configure(fg='green')
    # startbtn = Button(root, text='Start Server', command=serverThread)
    # startbtn.grid(column=0, row=6)
    startbtn.configure(state=NORMAL)
    clientbtn.configure(state=DISABLED)


def buttonReset():
    startbtn.configure(state=DISABLED)
    startclientbtn.configure(state=DISABLED)
    serverbtn.configure(state=NORMAL)
    clientbtn.configure(state=NORMAL)


##SERVER FUNCTIONS
def echoServer():
    ##Server will recieve a PING from the client and then responds with ACK
    try:
        config.read('conf.ini')
        serverAddress = config.get(confName, 'masterIP')
        clientAddress = config.get(confName, 'peerIP')
        masterPort = config.get(confName, 'masterUDP')
        restPort = config.get(confName, 'restUDP')
        delaySEC = config.get(confName, 'delaySEC')
        packetCOUNT = config.get(confName, 'packetCOUNT')
        timeoutSEC = config.get(confName, 'timeoutSEC')
        packetCOUNT = int(packetCOUNT) * 2

        # master socket
        masterSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        masterSock.settimeout(int(timeoutSEC))
        masterServer = (serverAddress, int(masterPort))
        masterSock.bind(masterServer)
        print("Listening on " + serverAddress + ":" + str(masterPort))

        # rest socket
        restSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        restSock.settimeout(int(timeoutSEC))
        restServer = (serverAddress, int(restPort))
        restSock.bind(restServer)
        print("Listening on " + serverAddress + ":" + str(restPort))

        for i in range(int(packetCOUNT)):
            # Master UDP Port Payload
            Masterpayload, rx = masterSock.recvfrom(1048)
            #print('MASTER: ' + Masterpayload.decode('utf-8'))
            if Masterpayload.decode('utf-8') == 'PING':
                masterSock.sendto(bytes('ACK', 'utf-8'), (clientAddress, int(masterPort)))
                MasterUDPStatusLabel.configure(fg='green', text='Recieved ACK')
            if 'SYSMSG' in Masterpayload.decode('utf-8'):
                theping = re.findall(".\..", Masterpayload.decode('utf-8'))[0]
                thecount = re.findall("..\Z", Masterpayload.decode('utf-8'))[0]
                MasterSYSMSG.configure(text='Ping: ' + theping + 'ms Packets: ' + thecount)
                time.sleep(int(delaySEC))

            # Rest UDP Port Payload
            Restpayload, rx = restSock.recvfrom(1048)
            #print('REST: ' + Restpayload.decode('utf-8'))
            if Restpayload.decode('utf-8') == 'PING':
                restSock.sendto(bytes('ACK', 'utf-8'), (clientAddress, int(restPort)))
                RestUDPStatusLabel.configure(fg='green', text='Recieved ACK')
            if 'SYSMSG' in Restpayload.decode('utf-8'):
                theping = re.findall(".\..", Restpayload.decode('utf-8'))[0]
                thecount = re.findall("..\Z", Restpayload.decode('utf-8'))[0]
                RestSYSMSG.configure(text='Ping: ' + theping + 'ms Packets: ' + thecount)
                time.sleep(int(delaySEC))
        MasterUDPStatusLabel.configure(text='Complete')
        RestUDPStatusLabel.configure(text='Complete')
        clientbtn.configure(state=DISABLED)
        serverbtn.configure(state=DISABLED)
    except timeout:
        MasterUDPStatusLabel.configure(text='Timed Out', fg='red')
        RestUDPStatusLabel.configure(text='Timed Out', fg='red')
        clientbtn.configure(state=DISABLED)
        serverbtn.configure(state=DISABLED)

def echoClient():
    config.read('conf.ini')
    serverAddress = config.get(confName, 'masterIP')
    clientAddress = config.get(confName, 'peerIP')
    masterPort = config.get(confName, 'masterUDP')
    restPort = config.get(confName, 'restUDP')
    packetCOUNT = config.get(confName, 'packetCOUNT')
    timeoutSEC = config.get(confName, 'timeoutSEC')

    try:
        # master socket
        masterclientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        masterclientSock.settimeout(int(timeoutSEC))
        masterClient = (clientAddress, int(masterPort))
        masterclientSock.bind(masterClient)
        print("Listening on " + clientAddress + ":" + str(masterPort))

        # rest socket
        restclientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        restclientSock.settimeout(int(timeoutSEC))
        restServer = (clientAddress, int(restPort))
        restclientSock.bind(restServer)
        print("Listening on " + clientAddress + ":" + str(restPort))

        mastercounter = 0
        restcounter = 0

        for i in range(int(packetCOUNT)):
            # CLIENT MUST SEND BEFORE IT WILL RECIEVE A PACKET
            # MASTER
            start = time.time()
            masterclientSock.sendto(bytes('PING', 'utf-8'), (serverAddress, int(masterPort)))
            end = time.time()
            elapsed = re.findall(".\..", str(end - start))[0]
            Masterclientpayload, rx = masterclientSock.recvfrom(1048)
            #print(Masterclientpayload.decode('utf-8'))
            if 'ACK' in Masterclientpayload.decode('utf-8'):
                mastercounter = mastercounter + 1
                #print('master count: ' + str(mastercounter))
                MasterUDPStatusLabel.configure(fg='green', text='Recieved ACK')
                MasterSYSMSG.configure(text='Ping: ' + str(elapsed) + 'ms Packets: ' + str(mastercounter))
                sendsys = 'SYSMSG: ' + elapsed + 'COUNT: ' + str(mastercounter)
                masterclientSock.sendto(bytes(sendsys, 'utf-8'), (serverAddress, int(masterPort)))

            # REST
            start = time.time()
            restclientSock.sendto(bytes('PING', 'utf-8'), (serverAddress, int(restPort)))
            end = time.time()
            elapsed = re.findall(".\..", str(end - start))[0]
            Restclientpayload, rx = restclientSock.recvfrom(1048)
            if 'ACK' in Restclientpayload.decode('utf-8'):
                restcounter = restcounter + 1
                RestUDPStatusLabel.configure(fg='green', text='Recieved ACK')
                RestSYSMSG.configure(text='Ping: ' + str(elapsed) + 'ms Packets: ' + str(restcounter))
                sendsys = 'SYSMSG: ' + elapsed + 'COUNT: ' + str(restcounter)
                restclientSock.sendto(bytes(sendsys, 'utf-8'), (serverAddress, int(restPort)))
        MasterUDPStatusLabel.configure(text='Complete')
        RestUDPStatusLabel.configure(text='Complete')
        clientbtn.configure(state=DISABLED)
        serverbtn.configure(state=DISABLED)
    except timeout:
        MasterUDPStatusLabel.configure(text='Timed Out', fg='red')
        RestUDPStatusLabel.configure(text='Timed Out', fg='red')
        clientbtn.configure(state=DISABLED)
        serverbtn.configure(state=DISABLED)
    except:
        errorMsgLabel.configure(text='FAILED: IS SERVER RUNNING?', fg='red', wraplength=150)

##ROOT MENU
root.title('Trbo Network Test')
root.geometry('350x140')

# IP Labels Root Window

# Master
MasterUDPLabel = Label(root, text='Master UDP: ')
MasterUDPLabel.grid(column=0, row=0)
MasterUDPStatusLabel = Label(root, text='Awaiting Test...')
MasterUDPStatusLabel.grid(column=1, row=0)

MasterSYSMSG = Label(root, text='')
MasterSYSMSG.grid(column=2, row=0)

# Rest
RestUDPLabel = Label(root, text='Rest UDP: ')
RestUDPLabel.grid(column=0, row=1)
RestUDPStatusLabel = Label(root, text='Awaiting Test...')
RestUDPStatusLabel.grid(column=1, row=1)

RestSYSMSG = Label(root, text='')
RestSYSMSG.grid(column=2, row=1)

serverbtn = Button(root, text='SERVER MODE', command=serverMode)
serverbtn.grid(column=0, row=5)

clientbtn = Button(root, text='CLIENT MODE', command=clientMode)
clientbtn.grid(column=1, row=5)

startbtn = Button(root, text='Start Server', command=serverThread)
startbtn.configure(state=DISABLED)
startbtn.grid(column=0, row=6)

startclientbtn = Button(root, text='Start Client', command=clientThread)
startclientbtn.configure(state=DISABLED)
startclientbtn.grid(column=1, row=6)

errorMsgLabel = Label(root, text='')
errorMsgLabel.grid(column=0, row=7)

##CONFIGURATION MENU
def configurationMenu():
    config.read('conf.ini')
    masterIP = config[confName]['masterIP']
    peerIP = config[confName]['peerIP']
    masterUDP = config[confName]['masterUDP']
    restUDP = config[confName]['restUDP']
    delaySEC = config[confName]['delaySEC']
    packetCOUNT = config[confName]['packetCOUNT']
    timeoutSEC = config[confName]['timeoutSEC']

    confMenu = Toplevel(root)
    confMenu.title("System Test Configuration")
    confMenu.geometry("200x200")

    MasterIPLabel = Label(confMenu, text="Master (server) IP: ")
    MasterIPLabel.grid(column=1, row=0)

    MasterIPText = Entry(confMenu, width=15)
    MasterIPText.insert(0, masterIP)
    MasterIPText.grid(column=2, row=0)

    PeerIPLabel = Label(confMenu, text="Peer (client) IP: ")
    PeerIPLabel.grid(column=1, row=1)

    PeerIPText = Entry(confMenu, width=15)
    PeerIPText.insert(0, peerIP)
    PeerIPText.grid(column=2, row=1)

    MasterUDPLabel = Label(confMenu, text="Master UDP: ")
    MasterUDPLabel.grid(column=1, row=2)

    MasterUDPText = Entry(confMenu, width=15)
    MasterUDPText.insert(0, masterUDP)
    MasterUDPText.grid(column=2, row=2)

    RestUDPLabel = Label(confMenu, text="Rest UDP: ")
    RestUDPLabel.grid(column=1, row=3)

    RestUDPText = Entry(confMenu, width=15)
    RestUDPText.insert(0, restUDP)
    RestUDPText.grid(column=2, row=3)

    DelaySECText = Entry(confMenu, width=15)
    DelaySECText.insert(0, delaySEC)
    DelaySECText.grid(column=2, row=4)
    DelaySECLabel = Label(confMenu, text="Delay (sec): ")
    DelaySECLabel.grid(column=1, row=4)

    PacketCOUNTText = Entry(confMenu, width=15)
    PacketCOUNTText.insert(0, packetCOUNT)
    PacketCOUNTText.grid(column=2, row=5)
    PacketCOUNTLabel = Label(confMenu, text="Packet Count: ")
    PacketCOUNTLabel.grid(column=1, row=5)

    TimeoutSECText = Entry(confMenu, width=15)
    TimeoutSECText.insert(0, timeoutSEC)
    TimeoutSECText.grid(column=2, row=6)
    TimeoutSECLabel = Label(confMenu, text="Timeout(sec): ")
    TimeoutSECLabel.grid(column=1, row=6)

    btn = Button(confMenu, text="Save Values",
                 fg="black",
                 command=lambda: updateMenu(MasterIPText, PeerIPText, MasterUDPText, RestUDPText, DelaySECText, PacketCOUNTText, TimeoutSECText))
    btn.grid(column=2, row=7)


##About Menu
def aboutMenu():
    about = Toplevel(root)
    about.title("About")
    about.geometry("300x155")

    photo = PhotoImage(file="sarah.png")
    photo_label = Label(about, image=photo)
    photo_label.pack(side='left', anchor='nw')
    photo_label.image = photo

    aboutText = Label(about, wraplength=200,
                      text='This application was written by Sarah R. Giddings; The program sends UDP and TCP packets along pre-configured addresses to test if a network will pass Mototrbo traffic. Ping time is calculated using the start and end times for the traversal via the client. These client messages are mirrored on the server via a SYSMSG sent over the master UDP port.')
    aboutText.pack(side='left', anchor='sw')


##Help Text

def helptext():
    help = Toplevel(root)
    help.title('Quick Help')
    help.geometry('250x250')

    helpLabel = Label(help, text="The server uses the configured MASTER IP/Port for bi-directional communication"
                                 "while the client uses the PEER IP/Port to make it's connection.", wraplength=200)
    helpLabel.grid(column=0, row=0)


##UPDATE MENU
def updateMenu(masterIPentry, peerIPentry, masterUDPentry, restUDPentry, DelaySECEntry, PacketCOUNTEntry, TimeoutSECEntry):
    import configparser
    confName = "MotoNetTestServer"
    config = configparser.RawConfigParser()
    config[confName] = {}
    config.set(confName, 'masterIP', masterIPentry.get())
    config.set(confName, 'peerIP', peerIPentry.get())
    config.set(confName, 'masterUDP', masterUDPentry.get())
    config.set(confName, 'restUDP', restUDPentry.get())
    config.set(confName, 'delaySEC', DelaySECEntry.get())
    config.set(confName, 'packetCOUNT', PacketCOUNTEntry.get())
    config.set(confName, 'timeoutSEC', TimeoutSECEntry.get())
    with open('conf.ini', 'w') as configfile:
        config.write(configfile)


##ROOT MENU BAR
menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Configuration", command=configurationMenu)
filemenu.add_command(label="Reset Buttons", command=buttonReset)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=filemenu)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="Help Index", command=helptext)
helpmenu.add_command(label="About...", command=aboutMenu)
menubar.add_cascade(label="Help", menu=helpmenu)

root.config(menu=menubar)

root.mainloop()
