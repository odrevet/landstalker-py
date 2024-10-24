# landstalker-py

A (stub) landstalker for PC, using assets from the megadrive game Landstalker exported using lordmir's landstalker_editor


# Needed assets

Export using https://github.com/lordmir/landstalker_editor/

**All files goes to the `data` directory**

Some functionalities are only available in branches in this fork at the moment : https://github.com/odrevet/landstalker_editor

* Export all rooms (branch export-rooms-with-flags) and move them to `data/rooms`
* To enable heightmap (wip background collision) : Export map as csv set (heightmap csv only is needed) and move them to `data/heightmaps`
* To display the Ryle (aka Nigel) sprite : Select `Sprite/Sprite/Gfx000` and export as png with `file/Export sprite animation as png` (branch `export-sprite-animation`) and move to png to `data/gfx`

# Python packages

See `requirements.txt`

# Usage

--room or -r room number
--debug or -d enable debug mode
- x initial player x location
- y initial player y location
- z initial player z location


Uage examples:

* Load room 595

```
python src/main.py -r 595
```

* Load room 240 and set player location, enable debug

```
python src/main.py -r 240 -x 380 -y 120 -z 16 --debug
```

# Keys

* Arrowkeys: move hero.
* Ctrl-Left or Crtl-Right: load previous or next map
* Maj + Arrowkeys : move camera


# Debug mode

Display player coords in the HUD

h key : toogle draw heightmap 
b key : toogle draw hero boundbox
