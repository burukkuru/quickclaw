### quickclaw.py ###
# script to automate adding new pokemon species to pokecrystal
# TODO: Write to pokecrystal files

import pokebase as pb
import sys

### handle cli arguments ###
# TODO: handle species names containing spaces
if (len(sys.argv) > 1):
    species_query = sys.argv[1]
else:
    print('Error: No species given')
    quit()

species = pb.pokemon(species_query)
species_data = pb.pokemon_species(species_query)

# user settings
# enable if using decapitalized species names
decap_names = False 

### constant ###
def create_constant(s):
    temp_const = s.upper()
    constant = ''
    for c in temp_const:
        if c.isalpha() == False:
            c = '_'
        constant += c
    return constant
constant = create_constant(species.name)
print('Created constant: ' + constant)

### species name ###
if decap_names:
    name = species.name.title()
else:
    name = species.name.upper()
for i in range(len(name), 10): # max length of species name
    name += '@' # padding
name = '"' + name + '"'
print('Created name: ' + name)

### base stats asm ###
# create base_stats/species.asm


# base stat total
bst_temp = 0
for i in range(0, len(species.stats)):
    bst_temp += species.stats[i].base_stat
base_stat_total = str(bst_temp)
# base stats
hp              = str(species.stats[0].base_stat)
attack          = str(species.stats[1].base_stat)
defense         = str(species.stats[2].base_stat)
special_attack  = str(species.stats[3].base_stat)
special_defense = str(species.stats[4].base_stat)
speed           = str(species.stats[5].base_stat)

print('Found stats: \tBST:' + base_stat_total + 
'\nHP:' + hp + '\tATK:' + attack + '\tDEF:' + defense + 
'\nSPD:' + speed + '\tSAT:' + special_attack + '\tSDF:' + special_defense)

# ev yield
# TODO: cli argument for if user added in evs


# types
# TODO: additional check if type exists (fairy)
type1 = str(species.types[0].type).upper()
if len(species.types) == 1: # if species only has 1 type
    type2 = type1 # duplicate primary type
else:
    type2 = str(species.types[1].type).upper()
print('Found types: ' + type1 + ', ' + type2)

# catch rate
catch_rate = str(species_data.capture_rate)
print('Found catch rate: ' + catch_rate)

# base exp
base_exp = str(species.base_experience)
print('Found base exp: ' + base_exp)

# held items # TODO: add held item functionality
# TODO: check item constants pulled from pokebase against 
# those in pokecrystal repo. display warning if there is no
# matching item constant
print('Warning: Wild held items are currently not handled by quickclaw.py')
item_common = 'NO_ITEM'
item_rare = 'NO_ITEM'
print('Found items: ' + item_common + ', ' + item_rare)

# gender ratio
gender_ratios = { '0': 'GENDER_F0', '1': 'GENDER_F12_5', '2': 'GENDER_F25', '4': 'GENDER_F50', '6': 'GENDER_F75', 
'8': 'GENDER_F100', '-1': 'GENDER_UNKNOWN' }
gender_ratio = gender_ratios[str(species_data.gender_rate)]
print('Found gender ratio: ' + gender_ratio)

# step cycles to hatch
step_cycles_to_hatch = str(species_data.hatch_counter)
print('Found step cycles to hatch: ' + step_cycles_to_hatch)

# growth rate
# TODO: apply similar warning to held item check if erratic and fluctuating growth
# rates do not exist in the pokecrystal repo
growth_rates = { 'medium': 'GROWTH_MEDIUM_FAST', 'medium-slow': 'GROWTH_MEDIUM_SLOW', 'fast': 'GROWTH_FAST', 
'slow': "GROWTH_SLOW", 'slow-then-very-fast': 'GROWTH_ERRATIC', 'fast-then-very-slow': 'GROWTH_FLUCTUATING' }
growth_rate = growth_rates[str(species_data.growth_rate)]
print('Found growth rate: ' + growth_rate)

# egg groups
egg_groups = { 'monster': 'EGG_MONSTER', 'water1': 'EGG_WATER_1', 'bug': 'EGG_BUG', 'flying': 'EGG_FLYING', 
'ground': 'EGG_GROUND', 'fairy': 'EGG_FAIRY', 'plant': 'EGG_PLANT', 'humanshape': 'EGG_HUMANSHAPE',
'water3': 'EGG_WATER_3', 'mineral': 'EGG_MINERAL', 'indeterminate': 'EGG_INDETERMINATE', 'water2': 'EGG_WATER_2', 
'ditto': 'EGG_DITTO', 'dragon': 'EGG_DRAGON', 'no-eggs': 'EGG_NONE' }
egg_group1 = egg_groups[str(species_data.egg_groups[0])]
if len(species_data.egg_groups) == 1: # if species only has 1 egg group
    egg_group2 = egg_group1 # duplicate egg group
else:
    egg_group2 = egg_groups[str(species_data.egg_groups[1])]
print('Found egg groups: ' + egg_group1 + ', ' + egg_group2)

# tm/hm learnset
# TODO: check this against list of valid tms
tm_learnset = ''

### evolutions and level-up learnset ###
lvl_learnset = ''

for i in species.moves:
    lvl_learnset += create_constant(str(i.move)) + ', '

print(lvl_learnset)
