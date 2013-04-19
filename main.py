#!/usr/bin/python
# -*- coding: utf-8 -*-

# This workout is based on the 300's and Spartucus official workouts and I hope to
# document each exercise soon. Rules are:
# 1.- 10 exercises
# 2.- 60 seconds sets
# 3.- 15 seconds break
# 4.- Complete whole circuit, rest 2 minutes and repeat
# 5.- Enjoy the pain mothafucka!
#
# Author: Wil Alvarez (aka satanas) <wil.alejandro@gmail.com>

# TODO:
# * Improve UI
# * Show the number of the current exercise

import os
import gtk
import sys
import gst
import random
import gobject

random.seed()

LIMIT_WORKOUT = 60 # seconds
LIMIT_REST = 15 # seconds

class Level:
    WARM_UP = 1
    FAT_BURNER = 2
    SPARTAN = 3

    @staticmethod
    def to_s(number):
        if number == Level.WARM_UP:
            return 'Warm Up'
        if number == Level.FAT_BURNER:
            return 'Fat Burner'
        if number == Level.SPARTAN:
            return 'Spartan'

class Impact:
    NORMAL = 1
    HIGH = 2

class Exercise:
    def __init__(self, name, level, impact):
        self.name = name
        self.level = level
        self.impact = impact

class Training:
    def __init__(self):
        self.exercises = []

    def shuffle(self):
        random.shuffle(self.exercises)

    def select(self, num, level, impact):
        selected = []
        while len(selected) < 2:
            item = random.choice(self.exercises)
            if item not in selected and item.level <= level and item.impact <= impact:
                selected.append(item)
        return selected


class Core(Training):
    def __init__(self):
        Training.__init__(self)

        self.exercises.append(Exercise('Plank', Level.WARM_UP, Impact.NORMAL))
        self.exercises.append(Exercise('Side Plank', Level.WARM_UP, Impact.NORMAL))
        self.exercises.append(Exercise('Stable Arm Plank', Level.FAT_BURNER, Impact.NORMAL))
        self.exercises.append(Exercise('1 Leg Plank', Level.FAT_BURNER, Impact.NORMAL))
        self.exercises.append(Exercise('Scorpions', Level.SPARTAN, Impact.NORMAL))
        self.exercises.append(Exercise('Mountain Climber', Level.SPARTAN, Impact.HIGH))
        self.exercises.append(Exercise('Knee to Elbow Plank', Level.SPARTAN, Impact.NORMAL))
        self.exercises.append(Exercise('High Jump Push-Ups', Level.SPARTAN, Impact.HIGH))
        self.exercises.append(Exercise('\"T\" Push-Ups', Level.SPARTAN, Impact.NORMAL))
        self.exercises.append(Exercise('Mountain Climber Push-Ups', Level.SPARTAN, Impact.NORMAL))
        self.exercises.append(Exercise('Push-Ups Crossover Climbs', Level.SPARTAN, Impact.NORMAL)) # Mountain climber but with crossed hand
        self.exercises.append(Exercise('Push-Ups and Row', Level.FAT_BURNER, Impact.NORMAL))
        self.exercises.append(Exercise('Push-Ups and Pass Weight', Level.FAT_BURNER, Impact.NORMAL))
        self.exercises.append(Exercise('Push-Ups Squad Combo', Level.SPARTAN, Impact.HIGH))
        self.exercises.append(Exercise('Progression', Level.SPARTAN, Impact.HIGH))
        #self.exercises.append(Exercise('Spiderman Push-Ups', Level.SPARTAN, Impact.NORMAL))

        self.shuffle()

class Legs(Training):
    def __init__(self):
        Training.__init__(self)

        self.exercises.append(Exercise('Goblet Squad', Level.FAT_BURNER, Impact.NORMAL))
        self.exercises.append(Exercise('Dumbbell Lunge and Rotation', Level.WARM_UP, Impact.NORMAL))
        self.exercises.append(Exercise('Ballistic Knee Raises', Level.WARM_UP, Impact.HIGH))
        self.exercises.append(Exercise('Split Jump', Level.SPARTAN, Impact.HIGH))
        self.exercises.append(Exercise('High Jump', Level.SPARTAN, Impact.HIGH))
        self.exercises.append(Exercise('Frog Jump', Level.SPARTAN, Impact.HIGH))

        self.shuffle()

class Arms(Training):
    def __init__(self):
        Training.__init__(self)

        self.exercises.append(Exercise('Dumbbell Front Raises (to ceiling)', Level.FAT_BURNER, Impact.NORMAL))
        self.exercises.append(Exercise('Single Arm Dumbbell Swing', Level.WARM_UP, Impact.NORMAL))
        self.exercises.append(Exercise('Dumbbell Row', Level.WARM_UP, Impact.NORMAL))
        self.exercises.append(Exercise('Superman Row', Level.FAT_BURNER, Impact.NORMAL))
        self.exercises.append(Exercise('Side to Side Push-Ups', Level.SPARTAN, Impact.NORMAL))
        self.exercises.append(Exercise('Bent Over Arm', Level.WARM_UP, Impact.NORMAL))
        self.exercises.append(Exercise('Diamond Push-Ups', Level.SPARTAN, Impact.NORMAL))

        self.shuffle()

class Abs(Training):
    def __init__(self):
        Training.__init__(self)

        self.exercises.append(Exercise('Tall Sit Up', Level.WARM_UP, Impact.NORMAL))
        self.exercises.append(Exercise('Reverse Crunch', Level.FAT_BURNER, Impact.NORMAL))
        self.exercises.append(Exercise('Total Abs (ball)', Level.FAT_BURNER, Impact.NORMAL))
        self.exercises.append(Exercise('Sky Reacher', Level.FAT_BURNER, Impact.NORMAL))
        self.exercises.append(Exercise('Oblique Crunch', Level.SPARTAN, Impact.NORMAL))
        self.exercises.append(Exercise('Bike Abs', Level.FAT_BURNER, Impact.NORMAL))
        self.exercises.append(Exercise('Superman Crunch', Level.SPARTAN, Impact.NORMAL))
        self.exercises.append(Exercise('Rowers', Level.SPARTAN, Impact.NORMAL))
        self.exercises.append(Exercise('Hip Raises', Level.SPARTAN, Impact.NORMAL))

        self.shuffle()

class Workout(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)

        self.index = 0
        self.level = None
        self.impact = None
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

        self.level_selector()

        self.fullscreen()

    def level_selector(self):
        level_label = gtk.Label()
        level_label.set_use_markup(True)
        level_label.set_markup('<span size="40000"><b>Select level:</b></span>')

        warmup_button = gtk.Button('Warm Up')
        warmup_button.connect('clicked', self.impact_selector, Level.WARM_UP)
        fatburner_button = gtk.Button('Fat Burner')
        fatburner_button.connect('clicked', self.impact_selector, Level.FAT_BURNER)
        spartan_button = gtk.Button('Spartan')
        spartan_button.connect('clicked', self.impact_selector, Level.SPARTAN)
        close_button = gtk.Button('Close')

        close_button.connect('clicked', self.__close)

        self._child = gtk.VBox(False)
        self._child.pack_start(level_label, False, False, 10)
        self._child.pack_start(warmup_button, False, False, 2)
        self._child.pack_start(fatburner_button, False, False, 2)
        self._child.pack_start(spartan_button, False, False, 2)
        self._child.pack_start(close_button, False, False, 20)

        self.add(self._child)
        self.show_all()

    def impact_selector(self, widget, level):
        self.level = level

        impact_label = gtk.Label()
        impact_label.set_use_markup(True)
        msg = '<span size="40000"><b>You have selected level %s. Now select impact:</b></span>' % Level.to_s(level)
        impact_label.set_markup(msg)

        normal_button = gtk.Button('Normal')
        normal_button.connect('clicked', self.prepare, Impact.NORMAL)
        high_button = gtk.Button('High')
        high_button.connect('clicked', self.prepare, Impact.HIGH)

        close_button = gtk.Button('Close')
        close_button.connect('clicked', self.__close)

        self.remove(self._child)

        self._child = gtk.VBox(False)
        self._child.pack_start(impact_label, False, False, 10)
        self._child.pack_start(normal_button, False, False, 2)
        self._child.pack_start(high_button, False, False, 2)
        self._child.pack_start(close_button, False, False, 20)

        self.add(self._child)
        self.show_all()

    def prepare(self, widget, impact):
        self.impact = impact

        core = Core()
        legs = Legs()
        arms = Arms()
        abs_ = Abs()

        self.workout = core.select(3, self.level, self.impact)
        self.workout += abs_.select(3, self.level, self.impact)
        self.workout += legs.select(2, self.level, self.impact)
        self.workout += arms.select(2, self.level, self.impact)

        random.shuffle(self.workout)

        close_button = gtk.Button('Close')
        close_button.connect('clicked', self.__close)

        continue_button = gtk.Button('Continue')
        continue_button.connect('clicked', self.ready)

        self.remove(self._child)
        self._child = gtk.VBox(False)

        for exercise in self.workout:
            label = gtk.Label(exercise.name)
            self._child.pack_start(label, False, False, 2)

        self._child.pack_start(continue_button, False, False, 10)
        self._child.pack_start(close_button, False, False, 10)

        self.add(self._child)
        self.show_all()

    def ready(self, widget):
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
        name = '<span size="40000"><b>%s</b></span>' % self.workout[self.index].name
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

        self.button_start.connect('clicked', self.__start)
        self.button_end.connect('clicked', self.__end)

        self.remove(self._child)
        self._child = gtk.VBox(False)
        self._child.pack_start(time_box, True, True, 10)
        self._child.pack_start(exercise_box, False, False, 2)
        self._child.pack_start(button_box, True, True, 60)

        self.add(self._child)
        self.show_all()

    def __start(self, widget):
        self.index = 0
        self.secs = 0
        self.frac = 0
        self.status = 'working'
        self.sound.start()
        name = '<span size="40000"><b>%s</b></span>' % self.workout[self.index].name
        self.exercise_label.set_markup(name)
        self.instant_timer = gobject.timeout_add(10, self.__update_timer)

    def __update_timer(self):
        self.frac += 1
        if self.frac > 99:
            self.secs += 1
            self.frac = 0

        if self.status == 'working':
            if self.secs >= LIMIT_WORKOUT:
                if self.index + 1 >= len(self.workout):
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
        name = '<span size="40000"><b>Rest %i. Next: %s</b></span>' % (LIMIT_REST, self.workout[self.index + 1].name)
        self.exercise_label.set_markup(name)
        self.sound.cycle()

    def __change(self):
        self.index += 1
        self.secs = 0
        self.frac = 0
        if self.index > len(self.workout):
            self.__done()
            return
        name = '<span size="40000"><b>%s</b></span>' % self.workout[self.index].name
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
