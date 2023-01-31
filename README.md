# quickclaw.py
script to automate adding new pokemon species to pokecrystal  
requires [pokebase](https://pypi.org/project/pokebase/)

## Limitations
* cannot generate cries, outside scope of project
* menu icons must be manually assigned
* species graphics (including footprint) must be added manually
* sprites must be placed into gfx/pics.asm sprite banks manually

## Usage
python3 quickclaw.py {species name} {parameters listed below}
* -evs : writes ev yields to base_stats
* -decap : decapitalized species names
* -pc16 : follow [pokecrystal16](https://github.com/aaaaaa123456789/pokecrystal16) conventions
* -no_filler_data : ignores writing unknown1 and unknown2 data to base_stats
* -no_filler_pics : ignores writing beta pics to base_stats
* -unique_icons : unique menu icon constant for each new species
* -fix_footprints : fix footprint [design flaw](https://github.com/pret/pokecrystal/blob/master/docs/design_flaws.md#footprints-are-split-into-top-and-bottom-halves)
* -fix_dba_pic : fix dba_pic [design flaw](https://github.com/pret/pokecrystal/blob/master/docs/design_flaws.md#pic-banks-are-offset-by-pics_fix)
