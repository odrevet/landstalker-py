# landstalker-py

A (stub) landstalker for PC, using assets from the megadrive game Landstalker exported using lordmir's landstalker_editor


# Needed assets

Export using https://github.com/lordmir/landstalker_editor/

**All files goes to the `data` directory**

* To display maps: export all tmx
* To enable heightmap (wip background collision) : Export map as csv set (heightmap csv only is needed)
* To display the Ryle (aka Nigel) sprite : Select `Sprite/Sprite/Gfx000` and export as png with `file/Export sprite as png`

# Python packages

See `requirements.txt`

# Usage

--map or -m map number
--debug or -d enable debug mode
- x initial player x location
- y initial player y location
- z initial player z location


Uage examples:

* Load map 595

```
python main.py -m 595
```

* Load map 240 and set player location, enable debug

```
python main.py -m 240 -x 380 -y 120 -z 16 --debug
```

# Keys

* Arrowkeys: move hero.
* Ctrl-Left or Crtl-Right: load previous or next map
* Maj + Arrowkeys : move camera


# Debug mode

Draw heightmap and player coords in the HUD
