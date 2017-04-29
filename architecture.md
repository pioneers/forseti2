# forseti2 architecture notes

Last updated: April 2017

These notes describe the implementation of forseti2, and a bit about *why* it is
implemented the way it is.

## Overview

Forseti2 is designed as a modular distributed system. Components running on the
field include:
* Match state tracking (e.g. running the match timer)
* 4x driver stations (currently Dawn). Strictly speaking, these are not part of forseti2.
* UI for starting/stopping matches, displaying match information on the overhead projector, etc.
* Hardware interfaces with status lights (and any game-dependent field elements)

All versions of forseti2 have communicated with robots by using the driver
station software (Dawn, and PiEMOS before that) to relay messages to the robots.
This allows re-using the same communications scheme on the field as during
individual testing. It also means that field control already consists of at
least 5 pieces of software on the same network (4 driver stations and some base
station software).

Forseti2 takes distributed systems one step further by splitting up the base station
software into multiple programs. This allows the UI portion to use web technologies
so that it looks nice (in particular, the match timer is projected on the overhead
screen for the audience to see). It also decouples the hardware-interfacing
portions from the rest of the system, so if there are any electrical problems
that subsystem can be restarted without touching anything else.

## LCM for communication

Communications between these systems are handled with a shared-bus paradigm.
Nodes can publish messages to a particular *channel*, and any other node can
subscribe to that channel. Channel names are just strings, and are globally
accessible throughout field control. This solves the service discovery problem:
nodes (other than the lcm_ws_bridge server, described later) can be started on
any computer and they will just work. So, for example, hardware driver nodes can
be moved around if a particular computer is having issues, or a node can be
moved to a staff computer if it needs to be hot-patched during an event.

Python nodes access the shared bus using LCM. Web browsers can't access LCM
directly due to security restrictions, so they talk to a server known as the
LCM Websocket Bridge. The IP/port of this server is the only address that needs
to be hardcoded to run field control. Dawn also uses the LCM Websocket Bridge
(it could technically talk over native LCM because it is a desktop app, but the
LCM project does not provide any nodejs bindings).

## Browser-based UI

Field control needs a UI for running matches: it allows specifying which teams
are playing, starting/stopping the match timer, etc. This was originally written
in Python using toolkits such as tkinter and wxwidgets, but people don't actually
know the APIs of these toolkits and the interfaces didn't look that great. The
next iteration moved public-facing UI (such as what is shown on the overhead
screen) to web technologies, using a web server that translated between LCM
messages and a custom ad-hoc JSON protocol. This proved to be very heavy on
boilerplate code, which led to the creation of the LCM Websocket Bridge. Now
UI nodes can use the same message type schema as the rest of field control. A
side benefit is that the UI pages can be pure HTML/JS that is served from a
static file host.

## Match schedule and score reporting

Field control needs access to the match schedule for an event, and there needs
to be some way of logging match scores (also traditionally done by the field
control staff). At one point such information was passed around using slips of
paper (and maybe flash drives), which proved to be a mess. An attempt was made
to write a dedicated web app/server for hosting schedules and scores, but this
was a one-off thing that wasn't very robust to staff turnover.

The eventual solution was to use a Google Spreadsheet to record the match
schedule and match results. The spreadsheet is very easy to edit for the event
planners (both before the event, and during the event since elimination matches
depend on the winners of previous matches). It can also be accessed in a
programmatic fashion for both the PiE Website (so teams can see a live schedule
with scores) and field control. The current implementation from the field control
side involves the match UI webpage javascript being able to pull match information
from the spreadsheet. Afterwards the field operators can verify it, make any
on-the-spot corrections necessary, and then hand it off to be used throughout the
field. Final match scores are entered by manually typing them into the spreadsheet.

## Thoughts on live scoring

One year PiE tried to do live scoring for the field, which was done by volunteers
pressing buttons on XBox controllers to manipulate the scores. This proved to not
be accurate at all. Any future iterations would ideally be done by the actual
referees using a mobile/tablet interface.

The nice thing is that any devices connected to the field control WiFi network
can talk to the LCM Websocket Bridge, which means that a scoring console can be
made using the same technology stack. However, we haven't yet done this during
an actual competition.

## Misc thoughts

* Field status lights are great at giving at-a-glance information about state
* Buying bulk CAT5 cable is a good way of running wires around the field.
* Crimp MTA or other connectors to the CAT5 cable, since the standard ethernet jacks weren't reliable
* Sticky pads and zipties are great for cable management on the field
* Webcam for livestream used a 50 foot usb extension cable and worked
* Having each robot host a wifi network proved to be unreliable, plus would
increase setup time because WiFi connections take time. Use a central unchanging field router instead
* Make sure that LCM sets time-to-live (TTL) correctly so that messages aren't spammed over wifi
