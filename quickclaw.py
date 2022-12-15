### quickclaw.py ###
# script to automate adding new pokemon species to pokecrystal

# TODO: add cli flags: evs, decap, pc16, nofillerdata
# flag for ignoring quickclaw checks for if a given item or move exists in pokecrystal project
# implemented after main functionality is working

import pokebase as pb
import sys

### handle cli arguments ###
if (len(sys.argv) > 1):
    species_query = sys.argv[1]
else:
    print('Error: No species given')
    quit()

species = pb.pokemon(species_query)
species_data = pb.pokemon_species(species_query)

def search_file(data, s):
    line_num = 0
    for row in data:
        line_num += 1
        if row.find(s) != -1:
            break
    return line_num

### constant ###
def create_constant(s):
    temp_const = s.upper()
    constant = ''
    for c in temp_const:
        if c.isalpha() == False:
            c = '_'
        constant += c
    return constant

constant = create_constant(species_data.names[8].name)
print('Created constant: ' + constant)

# write constant to asm
with open('constants/pokemon_constants.asm', 'r+') as f:
    data = f.readlines()
    line_num = search_file(data, 'NUM_POKEMON EQU const_value')
    data.insert(line_num-1, '\tconst ' + constant + '\n')
    f.seek(0)
    f.writelines(data)
    print('Wrote constant ' + constant + ' to constants/pokemon_constants.asm')

### species name ###
name = species_data.names[8].name
for i in range(len(name), 10): # max length of species name
    name += '@' # padding
name = '"' + name + '"'
print('Created name: ' + name)

# write name to asm
with open('data/pokemon/names.asm', 'r+') as f:
    data = f.readlines()
    line_num = search_file(data, 'assert_table_length NUM_POKEMON')
    data.insert(line_num-1, '\tdb ' + name + '\n')
    f.seek(0)
    f.writelines(data)
    print('Wrote name ' + name + ' to data/pokemon/names.asm')

### base stats asm ###
# create base_stats/species.asm
name_as_filename = constant.lower()
stats_asm = 'data/pokemon/base_stats/' + name_as_filename + '.asm'
f = open(stats_asm, 'x')
print('Created file: ' + stats_asm)
f.close()

with open(stats_asm, 'a') as f:
    f.write('\tdb 0 ; species ID placeholder' + '\n\n')
    print('Wrote species ID placeholder to ' + stats_asm)

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
'\nHP: ' + hp + '\tATK:' + attack + '\tDEF:' + defense + 
'\nSPD:' + speed + '\tSAT:' + special_attack + '\tSDF:' + special_defense)
# TODO: clean this up
if(len(hp) == 2):
    hp = ' ' + hp
if(len(attack) == 2):
    attack = ' ' + attack
if(len(defense) == 2):
    defense = ' ' + defense
if(len(speed) == 2):
    speed = ' ' + speed
if(len(special_attack) == 2):
    special_attack = ' ' + special_attack
if(len(special_defense) == 2):
    special_defense = ' ' + special_defense

# write base stats to asm
with open(stats_asm, 'a') as f:
    f.write('\tdb ' + hp + ', ' + attack + ', ' + defense + ', ' + speed + ', ' 
    + special_attack + ', ' + special_defense + ' ; ' + base_stat_total + ' BST\n')
    print('Wrote stats to ' + stats_asm)

# ev yield
ev_hp              = str(species.stats[0].effort)
ev_attack          = str(species.stats[1].effort)
ev_defense         = str(species.stats[2].effort)
ev_special_attack  = str(species.stats[3].effort)
ev_special_defense = str(species.stats[4].effort)
ev_speed           = str(species.stats[5].effort)

print('Found ev yields:' +
'\nHP: ' + ev_hp + '\tATK:' + ev_attack + '\tDEF:' + ev_defense + 
'\nSPD:' + ev_speed + '\tSAT:' + ev_special_attack + '\tSDF:' + ev_special_defense)

# write evs to asm
with open(stats_asm, 'a') as f:
    f.write('\tevs  ' + ev_hp + ',   ' + ev_attack + ',   ' + ev_defense + ',   ' 
    + ev_speed + ',   ' + ev_special_attack + ',   ' + ev_special_defense)
    f.write('\n\t;   hp  atk  def  spd  sat  sdf\n\n')
    print('Wrote ev yields to ' + stats_asm)

# types
type1 = str(species.types[0].type).upper()
if len(species.types) == 1: # if species only has 1 type
    type2 = type1 # duplicate primary type
else:
    type2 = str(species.types[1].type).upper()
if type1 == 'PSYCHIC':
    type1 = 'PSYCHIC_TYPE'
if type2 == 'PSYCHIC':
    type2 = 'PSYCHIC_TYPE'
print('Found types: ' + type1 + ', ' + type2)

with open(stats_asm, 'a') as f:
    f.write('\tdb ' + type1 + ', ' + type2 + ' ; type\n')
    print('Wrote types to ' + stats_asm)

# catch rate
catch_rate = str(species_data.capture_rate)
print('Found catch rate: ' + catch_rate)

with open(stats_asm, 'a') as f:
    f.write('\tdb ' + catch_rate + ' ; catch rate\n')
    print('Wrote catch rate to ' + stats_asm)

# base exp
base_exp = str(species.base_experience)
print('Found base exp: ' + base_exp)

with open(stats_asm, 'a') as f:
    f.write('\tdb ' + base_exp + ' ; base exp\n')
    print('Wrote base exp to ' + stats_asm)

# held items
# TODO: check item constants pulled from pokebase against 
# those in pokecrystal repo. display warning if there is no
# matching item constant
item_common = 'NO_ITEM'
item_rare = 'NO_ITEM'
for x in species.held_items:
    if x.version_details[0].rarity == 100:
        item_common = create_constant(str(x.item))
        item_rare = item_common
    if x.version_details[0].rarity == 50:
        item_common = create_constant(str(x.item))
    if x.version_details[0].rarity == 5:
        item_rare = create_constant(str(x.item))
print('Found items: ' + item_common + ', ' + item_rare)

with open(stats_asm, 'a') as f:
    f.write('\tdb ' + item_common + ', ' + item_rare + ' ; items\n')
    print('Wrote items to ' + stats_asm)

# gender ratio
gender_ratios = { '0': 'GENDER_F0', '1': 'GENDER_F12_5', '2': 'GENDER_F25', '4': 'GENDER_F50', '6': 'GENDER_F75', 
'8': 'GENDER_F100', '-1': 'GENDER_UNKNOWN' }
gender_ratio = gender_ratios[str(species_data.gender_rate)]
print('Found gender ratio: ' + gender_ratio)

with open(stats_asm, 'a') as f:
    f.write('\tdb ' + gender_ratio + ' ; gender ratio\n')
    print('Wrote gender ratio to ' + stats_asm)

# unknown 1 data (if user left filler data enabled)

# step cycles to hatch
step_cycles_to_hatch = str(species_data.hatch_counter)
print('Found step cycles to hatch: ' + step_cycles_to_hatch)

with open(stats_asm, 'a') as f:
    f.write('\tdb ' + step_cycles_to_hatch + ' ; step cycles to hatch\n')
    print('Wrote step cycles to hatch to ' + stats_asm)

# unknown 2 data (if user left filler data enabled)

# incbin
with open(stats_asm, 'a') as f:
    f.write('\tINCBIN "gfx/pokemon/' + name_as_filename + '/front.dimensions"\n')
    print('Wrote sprite dimensions to ' + stats_asm)

# unused
with open(stats_asm, 'a') as f:
    f.write('\tdw NULL, NULL ; unused (beta front/back pics)\n')
    print('Wrote unused data to ' + stats_asm)

# growth rate
growth_rates = { 'medium': 'GROWTH_MEDIUM_FAST', 'medium-slow': 'GROWTH_MEDIUM_SLOW', 'fast': 'GROWTH_FAST', 
'slow': "GROWTH_SLOW", 'slow-then-very-fast': 'GROWTH_ERRATIC', 'fast-then-very-slow': 'GROWTH_FLUCTUATING' }
growth_rate = growth_rates[str(species_data.growth_rate)]
print('Found growth rate: ' + growth_rate)

with open(stats_asm, 'a') as f:
    f.write('\tdb ' + growth_rate + ' ; growth rate\n')
    print('Wrote growth rate to ' + stats_asm)

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

with open(stats_asm, 'a') as f:
    f.write('\tdn ' + egg_group1 + ', ' + egg_group2 + ' ; egg groups\n\n')
    print('Wrote egg groups to ' + stats_asm)

### learnset ###
# create list of moves
moves = []
for x in species.moves:
    lvl = x.version_group_details[0].level_learned_at
    move = create_constant(str(x.move))
    if move == 'PSYCHIC':
        move = 'PSYCHIC_M'
    moves.append((lvl, move))
moves.sort()
print('Found valid moves for species')

# create list of valid tms from pokecrystal
tms = []
with open('constants/item_constants.asm', 'r') as f:
    data = f.readlines()

    # tms
    begin = search_file(data, 'DEF TM01 EQU const_value')
    end = search_file(data, 'DEF NUM_TMS EQU __tmhm_value__ - 1')
    for line in data[begin:end-1]:
        tm_move = line[8:line.find(' ', 8)]
        tms.append(tm_move)

    # hms
    begin = search_file(data, 'DEF HM01 EQU const_value')
    end = search_file(data, 'DEF NUM_HMS EQU __tmhm_value__ - NUM_TMS - 1')
    for line in data[begin:end-1]:
        tm_move = line[8:line.find(' ', 8)]
        tms.append(tm_move)
    
    # tutor moves
    begin = search_file(data, 'DEF MT01 EQU const_value')
    end = search_file(data, 'DEF NUM_TUTORS = __tmhm_value__ - NUM_TMS - NUM_HMS - 1')
    for line in data[begin:end-1]:
        tm_move = line[8:line.find(' ', 8)]
        tms.append(tm_move)
print('Found valid tms/hms/tutors defined in pokecrystal')

# tm compatibility for this species
tm_compat = []
for move in tms:
    if any([move in tup for tup in moves]):
        tm_compat.append(move)
print('Created tm compatibility for species')

with open(stats_asm, 'a') as f:
    f.write('\t; tm/hm learnset\n\ttmhm ')
    last_item = tm_compat[-1]
    for move in tm_compat:
        if move == last_item:
            f.write(move)
        else:
            f.write(move + ', ')
    f.write('\n\t; end\n')
    print('Wrote tm compatibility to ' + stats_asm)

# level-up learnset
pokecrystal_moves = []
with open('constants/move_constants.asm', 'r') as f:
    data = f.readlines()
    begin = search_file(data, 'const_def')
    end = search_file(data, 'DEF NUM_ATTACKS EQU const_value - 1')
    for line in data[begin:end-1]:
        pokecrystal_moves = line[8:line.find(' ', 7)]
        tms.append(pokecrystal_moves)
print('Found all valid moves defined in pokecrystal')
