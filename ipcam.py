#!/usr/bin/env python
'''
    Originally written by mindcollapse
    https://gist.github.com/mindcollapse/3089556#file-pysurcamui-py
'''

import gtk
import threading
import datetime
import urllib2
import json

CONFIG_FILE = "config.json"

# config sample
# {
#  "url": "http://192.168.1.100",
#  "user": "user",
#  "pwd": "password"
# }


class IPCAM(gtk.Window):

    def __init__(self):
        super(IPCAM, self).__init__()

        try:
            config = json.load(open(CONFIG_FILE))
        except:
            raise SystemExit("%s config file was not found or parsed correctly"
                             % CONFIG_FILE)
        try:
            url = config['url']
            usr = config['user']
            pwd = config['pwd']
        except:
            raise SystemExit("Config does not contain all required fields.")

        self.cam = "%s/snapshot.cgi?user=%s&pwd=%s" % (url, usr, pwd)

        # variables
        self.isrunning = True
        self.currentimage = None
        self.previousimage = None
        self.rms = 0

        # window decoration
        self.set_default_size(320, 240)
        self.set_resizable(False)
        self.set_keep_above(True)
        self.set_position(gtk.WIN_POS_CENTER)

        # status icon
        self.statusicon = gtk.StatusIcon()
        self.statusicon.set_from_stock(gtk.STOCK_MEDIA_RECORD)
        self.statusicon.connect("activate", self.togglevisibility)
        self.statusicon.connect("popup-menu", self.popupmenu)

        # image view canvas
        canvaseventbox = gtk.EventBox()
        self.canvas = gtk.Image()
        self.canvas.show()
        canvaseventbox.add(self.canvas)
        self.add(canvaseventbox)

        self.show_all()

    def imageprocess(self):

        while self.isrunning:
            try:
                self.currentframedata = urllib2.urlopen(self.cam).read()
            except:
                continue

            gtk.gdk.threads_enter()
            try:
                if self.get_visible():
                    self.set_title(str(datetime.datetime.now()))
                    framedataloader = gtk.gdk.PixbufLoader()
                    framedataloader.write(self.currentframedata)
                    framedataloader.close()
                    self.canvas.set_from_pixbuf(framedataloader.get_pixbuf())
            finally:
                gtk.gdk.threads_leave()

    def popupmenu(self, icon, button, time):
        menu = gtk.Menu()

        shlabel = "Hide" if self.get_visible() else "Show"
        showhide = gtk.MenuItem(shlabel)

        quit = gtk.MenuItem("Quit")

        showhide.connect("activate", self.togglevisibility)
        quit.connect("activate", self.main_quit)

        menu.append(showhide)
        menu.append(quit)

        menu.show_all()
        menu.popup(None, None, gtk.status_icon_position_menu, button, time,
                   self.statusicon)

    def togglevisibility(self, event):
        if self.get_visible():
            self.hide()
        else:
            self.show()

    def minimizeonclose(self, window, event):
        self.hide_on_delete()
        return True

    def main_quit(self, event):
        self.isrunning = False
        self.imageprocessthread = False
        gtk.main_quit()

    def main(self):
        # background image process and update thread
        gtk.gdk.threads_init()
        self.imageprocessthread = threading.Thread(target=self.imageprocess)
        self.imageprocessthread.start()

        self.connect("destroy", self.main_quit)
        self.connect("delete-event", self.minimizeonclose)

        gtk.gdk.threads_enter()
        gtk.main()
        gtk.gdk.threads_leave()

UI = IPCAM()
UI.main()
