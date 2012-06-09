#!/usr/bin/python
# -*- coding: utf-8 -*-

# This workout is based on the 300's and Spartucus official workouts. I hope to
# document each exercise soon
#
# Author: Wil Alvarez (aka satanas) <wil.alejandro@gmail.com>
# Jan 01, 2012

import os
import gtk
import sys
import gst
import gobject

WORKOUTS = [
    '(Pe) Side to side push ups',
    '(Ab) Bike abs',
    '(Ho) Single arm dumbbell swing',
    '(Ab) Regular abs',
    '(To) Mountain Climber',
    '(Pe) "T" push ups',
    '(Ho) Bent over arm side lateral',
    '(Ab) Total abs',
    '(Pi) Split Jump',
    '(Ho) Dumbbell front raises (to ceiling)',
]
'''
WORKOUTS = [
    '(Pe) Side to side push ups',
    '(Ab) Bike abs',
    '(Ho) Superman',
    '(Ab) Regular abs',
    '(To) Mountain Climber',
    '(Pe) "T" push ups',
    '(Pi) High Jump', #'(Pi) Frog jump',
    '(Ab) Total abs',
    '(Pi) Split Jump',
    '(Pe) Bank push-up',
]
'''
LIMIT_WORKOUT = 60 # seconds
LIMIT_REST = 15 # seconds

class Workout(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)

        self.index = 0
        self.timer = None
        self.status = 'stopped'
        self.sound = Sound()
        self.instant_timer = None

        self.set_title('Extreme Workout')
        self.set_default_size(310, 482)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_gravity(gtk.gdk.GRAVITY_STATIC)
        self.connect('delete-event', self.__close)
        self.connect('key-press-event', self.__on_key_press)

        self.time_label = gtk.Label()
        self.time_label.set_use_markup(True)
        self.time_label.set_markup('<span size="120000">00:00:00</span>')
        time_evbox = gtk.EventBox()
        time_evbox.add(self.time_label)
        time_evbox.modify_bg(gtk.STATE_NORMAL | gtk.STATE_ACTIVE, gtk.gdk.Color(255, 255, 255))
        time_box = gtk.HBox(False)
        time_box.pack_start(time_evbox, True, True, 20)

        self.exercise_label = gtk.Label()
        self.exercise_label.set_use_markup(True)
        name = '<span size="40000"><b>%s</b></span>' % WORKOUTS[self.index]
        self.exercise_label.set_markup(name)
        exercise_box = gtk.HBox(False)
        exercise_box.pack_start(self.exercise_label, True, True)

        self.button_start = gtk.Button('Start')
        self.button_start.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0, 33410, 3855))
        self.button_start.modify_bg(gtk.STATE_PRELIGHT, gtk.gdk.Color(0, 46260, 3855))
        self.button_start.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.Color(0, 25700, 3855))
        self.button_end = gtk.Button('End')
        self.button_end.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(46260, 3855, 0))
        self.button_end.modify_bg(gtk.STATE_PRELIGHT, gtk.gdk.Color(53970, 3855, 0))
        self.button_end.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.Color(33410, 3855, 0))
        button_box = gtk.HBox(True)
        button_box.pack_start(self.button_start, True, True, 10)
        button_box.pack_start(self.button_end, True, True, 10)

        vbox = gtk.VBox(False)
        vbox.pack_start(time_box, True, True, 10)
        vbox.pack_start(exercise_box, False, False, 2)
        vbox.pack_start(button_box, True, True, 60)

        self.add(vbox)

        self.button_start.connect('clicked', self.__start)
        self.button_end.connect('clicked', self.__end)

        self.show_all()
        self.fullscreen()

    def __start(self, widget):
        self.index = 0
        self.secs = 0
        self.frac = 0
        self.status = 'working'
        self.sound.start()
        name = '<span size="40000"><b>%s</b></span>' % WORKOUTS[self.index]
        self.exercise_label.set_markup(name)
        self.instant_timer = gobject.timeout_add(10, self.__update_timer)

    def __update_timer(self):
        self.frac += 1
        if self.frac > 99:
            self.secs += 1
            self.frac = 0

        if self.status == 'working':
            if self.secs >= LIMIT_WORKOUT:
                if self.index + 1 >= len(WORKOUTS):
                    self.__done()
                else:
                    self.__rest()
        elif self.status == 'resting':
            if self.secs >= LIMIT_REST:
                self.__change()

        clock = '<span size="120000">00:%02i:%02i</span>' % (self.secs, self.frac)
        self.time_label.set_markup(clock)
        return True

    def __rest(self):
        self.secs = 0
        self.frac = 0
        self.status = 'resting'
        name = '<span size="40000"><b>Rest %i. Next: %s</b></span>' % (LIMIT_REST, WORKOUTS[self.index + 1])
        self.exercise_label.set_markup(name)
        self.sound.cycle()

    def __change(self):
        self.index += 1
        self.secs = 0
        self.frac = 0
        if self.index > len(WORKOUTS):
            self.__done()
            return
        name = '<span size="40000"><b>%s</b></span>' % WORKOUTS[self.index]
        self.exercise_label.set_markup(name)
        self.status = 'working'
        self.sound.start()

    def __done(self):
        self.status = 'stopped'
        self.sound.end()
        self.time_label.set_markup('<span size="120000">00:00:00</span>')
        name = '<span size="40000"><b>Well done!</b></span>'
        self.exercise_label.set_markup(name)
        if self.instant_timer:
            gobject.source_remove(self.instant_timer)

    def __end(self, widget):
        self.status = 'stopped'
        self.sound.end()
        self.time_label.set_markup('<span size="120000">00:00:00</span>')
        name = '<span size="40000"><b>Fagget!</b></span>'
        self.exercise_label.set_markup(name)
        if self.instant_timer:
            gobject.source_remove(self.instant_timer)

    def __on_key_press(self, widget, event):
        keyname = gtk.gdk.keyval_name(event.keyval)
        if keyname == 'Escape':
            confirm = gtk.MessageDialog(self, 0, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, 'Are you sure?')
            response = confirm.run()
            confirm.destroy()
            if response == gtk.RESPONSE_YES:
                self.__close(widget)
                return True
        return False

    def __close(self, widget, event=None):
        self.destroy()
        gtk.main_quit()
        sys.exit(0)

class Sound:
    def __init__(self):
        self.player = gst.element_factory_make("playbin2", "player")
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.__on_gst_message)

    def __on_gst_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
        elif t == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            err, debug = message.parse_error()
            print err, debug

    def play(self, filename):
        filepath = os.path.realpath(os.path.join(os.path.dirname(__file__), filename))
        self.player.set_property("uri", "file://" + filepath)
        self.player.set_state(gst.STATE_PLAYING)

    def start(self):
        self.play('bell.mp3')

    def cycle(self):
        self.play('horn.mp3')

    def end(self):
        self.play('siren.mp3')


if __name__ == "__main__":
    w = Workout()
    gtk.main()
