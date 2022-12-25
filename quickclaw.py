### quickclaw.py ###
# script to automate adding new pokemon species to pokecrystal

import pokebase as pb
import io
import sys

### functions ###
# returns line number of string in file
# data - contents of file
# s - search key
def search_file(data: list[str], s: str) -> int:
    line_num = 0
    for row in data:
        line_num += 1
        if row.find(s) != -1:
            break
    return line_num

# inserts string into file
# file - file to be written to
# data - contents of file
# s_search - search key
# s_insert - string to be inserted
def insert_file(file: io.TextIOWrapper, data: list[str], s_search: str, s_insert: str) -> None:
    line_num = search_file(data, s_search)
    data.insert(line_num-1, s_insert)
    file.seek(0)
    file.writelines(data)

# appends entries gathered from a file to a list
# data - contents of flie
# list - entries are appended to
# s_begin - search key marking beginning of range of file
# s_end - search key marking end of range of file
# offset - int marking where to begin parsing entry
# until - str marking where to stop parsing entry
def find_entries_in_range(data: list[str], l: list, s_begin: str, s_end: str, offset: int, until = ' ') -> None:
    begin = search_file(data, s_begin)
    end = search_file(data, s_end)
    for line in data[begin:end-1]:
        entry = line[offset:line.find(until, offset)]
        l.append(entry)

# returns a string converted to constant case
# s - string to be converted
def create_constant(s: str) -> str:
    temp_const = s.upper()
    constant = ''
    for c in temp_const:
        if c.isalpha() == False:
            c = '_'
        constant += c
    return constant

# returns a string after padded with filler data
# s - the string to be padded
# max - length of the return string
# filler - data added to string
# before - where filler will be placed: before if true, after if false
def pad_string(s: str, max: int, filler = ' ', before = True) -> str:
    if(len(s) < max):
        for _ in range(max - len(s)):
            if before:
                s = filler + s
            else:
                s = s + filler
    return s

# returns evolution chain of species matching key
# root - evolution chain object
# key - id of species to search for
def evolution_tree_bfs(root, key: int):
    q = []
    if root.species.id == key:
        return root
    q.append(root)
    while(len(q) != 0):
        v = q.pop(0)
        if v.species.id == key:
            return v
        for e in v.evolves_to:
            q.append(e)

### handle cli arguments ###
if (len(sys.argv) > 1):
    species_query = sys.argv[1]
else:
    print('Error: No species given')
    quit()

species = pb.pokemon(species_query)
species_data = pb.pokemon_species(species_query)

args = []
if (len(sys.argv) > 2):
    for x in range(2, len(sys.argv)):
        args.append(sys.argv[x])

flag_evs = False
flag_decap = False
flag_pc16 = False
flag_no_filler_data = False
flag_no_filler_pics = False
flag_unique_icons = False

if '-evs' in args:
    flag_evs = True
if '-decap' in args:
    flag_decap = True
if '-pc16' in args:
    flag_pc16 = True
if '-nofillerdata' in args:
    flag_no_filler_data = True
if '-nofillerpics' in args:
    flag_no_filler_pics = True
if '-uniqueicons' in args:
    flag_unique_icons = True

### constant ###
constant = create_constant(species_data.names[8].name)
print('Created constant: ' + constant)

# write constant to asm
with open('constants/pokemon_constants.asm', 'r+') as f:
    data = f.readlines()
    insert_file(f, data, 'NUM_POKEMON EQU const_value', '\tconst ' + constant + '\n')
    print('Wrote constant ' + constant + ' to constants/pokemon_constants.asm')

### species name ###
name = species_data.names[8].name
if(flag_decap == False):
    name = name.upper()
name = pad_string(name, 10, '@', False)
name = '"' + name + '"'
print('Created name: ' + name)

# write name to asm
with open('data/pokemon/names.asm', 'r+') as f:
    data = f.readlines()
    insert_file(f, data, 'assert_table_length NUM_POKEMON', '\tdb ' + name + '\n')
    print('Wrote name ' + name + ' to data/pokemon/names.asm')

### base stats asm ###
# create base_stats/species.asm
name_as_filename = constant.lower()
stats_asm = 'data/pokemon/base_stats/' + name_as_filename + '.asm'
with open(stats_asm, 'w+'):
    print('Created file: ' + stats_asm)

with open(stats_asm, 'a') as f:
    if(flag_pc16):
        f.write('\tdb 0 ; species ID placeholder' + '\n\n')
        print('Wrote species ID placeholder to ' + stats_asm)
    else:
        f.write('\tdb ' + constant + '\n\n')
        print('Wrote species ID to ' + stats_asm)

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
hp = pad_string(hp, 3)
attack = pad_string(attack, 3)
defense = pad_string(defense, 3)
speed = pad_string(speed, 3)
special_attack = pad_string(special_attack, 3)
special_defense = pad_string(special_defense, 3)

# write base stats to asm
with open(stats_asm, 'a') as f:
    f.write('\tdb ' + hp + ', ' + attack + ', ' + defense + ', ' + speed + ', ' 
    + special_attack + ', ' + special_defense + ' ; ' + base_stat_total + ' BST\n')
    print('Wrote stats to ' + stats_asm)

# ev yield
if(flag_evs):
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
        + ev_speed + ',   ' + ev_special_attack + ',   ' + ev_special_defense + '\n')
        print('Wrote ev yields to ' + stats_asm)

with open(stats_asm, 'a') as f:
    f.write('\t;   hp  atk  def  spd  sat  sdf\n\n')

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
pokecrystal_items = []
with open('constants/item_constants.asm', 'r') as f:
    data = f.readlines()
    find_entries_in_range(data, pokecrystal_items, 'const_def', 'DEF NUM_ITEMS EQU const_value - 1', 7)
    print('Found valid items defined in pokecrystal')

item_common = 'NO_ITEM'
item_rare = 'NO_ITEM'
for x in species.held_items:
    if x.version_details[-1].rarity == 100:
        item_common = create_constant(str(x.item))
        item_rare = item_common
    if x.version_details[-1].rarity == 50:
        item_common = create_constant(str(x.item))
    if x.version_details[-1].rarity == 5:
        item_rare = create_constant(str(x.item))
print('Found items: ' + item_common + ', ' + item_rare)

if item_common not in pokecrystal_items:
    print('Warning: ' + item_common + ' is not defined in pokecrystal. Setting to NO_ITEM')
    item_common = 'NO_ITEM'
if item_rare not in pokecrystal_items:
    print('Warning: ' + item_rare + ' is not defined in pokecrystal. Setting to NO_ITEM')
    item_rare = 'NO_ITEM'

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

# unknown 1 data
if(flag_no_filler_data == False):
    with open(stats_asm, 'a') as f:
        f.write('\tdb 100 ; unknown 1\n')
        print('Wrote unknown 1 to ' + stats_asm)

# step cycles to hatch
step_cycles_to_hatch = str(species_data.hatch_counter)
print('Found step cycles to hatch: ' + step_cycles_to_hatch)

with open(stats_asm, 'a') as f:
    f.write('\tdb ' + step_cycles_to_hatch + ' ; step cycles to hatch\n')
    print('Wrote step cycles to hatch to ' + stats_asm)

# unknown 2 data
if(flag_no_filler_data == False):
    with open(stats_asm, 'a') as f:
        f.write('\tdb 5 ; unknown 2\n')
        print('Wrote unknown 2 to ' + stats_asm)

# incbin
with open(stats_asm, 'a') as f:
    f.write('\tINCBIN "gfx/pokemon/' + name_as_filename + '/front.dimensions"\n')
    print('Wrote sprite dimensions to ' + stats_asm)

# beta pics
if(flag_no_filler_pics == False):
    with open(stats_asm, 'a') as f:
        f.write('\tdw NULL, NULL ; unused (beta front/back pics)\n')
        print('Wrote unused beta pics to ' + stats_asm)

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

# tm/hm/mt learnset
# create list of moves
moves = []
for x in species.moves:
    lvl = 0
    for i in range(len(x.version_group_details)):
        lvl = x.version_group_details[-(1+i)].level_learned_at
        if(lvl != 0):
            break
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
    find_entries_in_range(data, tms, 'DEF TM01 EQU const_value', 'DEF NUM_TMS EQU __tmhm_value__ - 1', 8)
    # hms
    find_entries_in_range(data, tms, 'DEF HM01 EQU const_value', 'DEF NUM_HMS EQU __tmhm_value__ - NUM_TMS - 1', 8)
    # tutor moves
    find_entries_in_range(data, tms, 'DEF MT01 EQU const_value', 'DEF NUM_TUTORS = __tmhm_value__ - NUM_TMS - NUM_HMS - 1', 8)
    print('Found valid tms/hms/tutors defined in pokecrystal')

# tm compatibility for this species
tm_compat = []
for move in tms:
    if any([move in tup for tup in moves]):
        tm_compat.append(move)
print('Created tm compatibility for species')

with open(stats_asm, 'a') as f:
    f.write('\t; tm/hm learnset\n\ttmhm ')
    if(len(tm_compat) != 0):
        last_item = tm_compat[-1]
        for move in tm_compat:
            if move == last_item:
                f.write(move)
            else:
                f.write(move + ', ')
    f.write('\n\t; end\n')
    print('Wrote tm compatibility to ' + stats_asm)

# add base stats asm
with open('data/pokemon/base_stats.asm', 'r+') as f:
    data = f.readlines()
    insert_file(f, data, 'assert_table_length NUM_POKEMON', 'INCLUDE "' + stats_asm + '"\n')
    print('Wrote base_stats asm path to data/pokemon/base_stats.asm')

### level-up learnset ###
# evos attack pointers
name_as_variable_temp = constant.title()
name_as_variable = ''
for c in name_as_variable_temp:
    if c.isalpha():
        name_as_variable += c
with open('data/pokemon/evos_attacks_pointers.asm', 'r+') as f:
    data = f.readlines()
    insert_file(f, data, 'assert_table_length NUM_POKEMON', '\tdw ' + name_as_variable + 'EvosAttacks\n')
    print('Wrote evos attack pointer to data/pokemon/evos_attacks_pointers.asm')

# create list of all valid moves from pokecrystal
pokecrystal_moves = []
with open('constants/move_constants.asm', 'r') as f:
    data = f.readlines()
    find_entries_in_range(data, pokecrystal_moves, 'const_def', 'DEF NUM_ATTACKS EQU const_value - 1', 7)
    print('Found all valid moves defined in pokecrystal')

# handle evolutions
evo_chain = evolution_tree_bfs(species_data.evolution_chain.chain, species.id)
evolutions_s = ''
# append to evolutions_s with line according to evolution method
for i in range(len(evo_chain.evolves_to)):
    evo_trigger = evo_chain.evolves_to[i].evolution_details[0].trigger.name
    evo_species = create_constant(evo_chain.evolves_to[i].species.names[8].name)
    if(evo_trigger == 'level-up'):
        # happiness
        if(evo_chain.evolves_to[i].evolution_details[0].min_happiness != None):
            time_of_day_dict = {'' : 'TR_ANYTIME', 'day' : 'TR_MORNDAY', 'night' : 'TR_NIGHT'}
            time_of_day = str(evo_chain.evolves_to[i].evolution_details[0].time_of_day)
            evolutions_s += '\tdb EVOLVE_HAPPINESS, ' + time_of_day_dict[time_of_day] + ', ' + evo_species + '\n'
        # simple level-up
        else:
            lvl = evo_chain.evolves_to[i].evolution_details[0].min_level
            if lvl == None:
                print('Warning: min_level not set. Disabling evolution ' + evo_species)
                evolutions_s += '\t; evolution method not found for : ' + evo_species + '\n'
            else:
                evolutions_s += '\tdb EVOLVE_LEVEL, ' + str(lvl) + ', ' + evo_species + '\n'
    # item
    elif(evo_trigger == 'use-item'):
        item = create_constant(str(evo_chain.evolves_to[i].evolution_details[0].item))
        if item not in pokecrystal_items:
            print('Warning: ' + item + ' is not defined in pokecrystal. Disabling evolution ' + evo_species)
            evolutions_s += '\t; db EVOLVE_ITEM, ' + item + ', ' + evo_species + '\n'
        else:
            evolutions_s += '\tdb EVOLVE_ITEM, ' + item + ', ' + evo_species + '\n'
    # trade
    elif(evo_trigger == 'trade'):
        held_item = create_constant(str(evo_chain.evolves_to[i].evolution_details[0].held_item))
        if held_item == 'NONE':
            evolutions_s += '\tdb EVOLVE_TRADE, -1, ' + evo_species + '\n'
        else:
            if held_item not in pokecrystal_items:
                print('Warning: ' + held_item + ' is not defined in pokecrystal. Disabling evolution ' + species)
                evolutions_s += '\t; db EVOLVE_TRADE, ' + held_item + ', ' + evo_species + '\n'
            else:
                evolutions_s += '\tdb EVOLVE_TRADE, ' + held_item + ', ' + evo_species + '\n'
    # undefined
    else:
        print('Warning: No evolution method found. Disabling evolution ' + evo_species)
        evolutions_s += '\t; evolution method not found for : ' + evo_species + '\n'
    print('Found evolution: ' + evo_species)

with open('data/pokemon/evos_attacks.asm', 'a') as f:
    f.write('\n' + name_as_variable + 'EvosAttacks:\n')
    f.write(evolutions_s)
    f.write('\tdb 0 ; no more evolutions\n')
    first_move = ''
    for lvl, move in moves:
        if lvl == 1:
            first_move = move
            break
    for lvl, move in moves[moves.index((1, first_move)):]:
        if move in pokecrystal_moves:
            f.write('\tdb ' + str(lvl) + ', ' + move + '\n')
        else:
            f.write('\t; db ' + str(lvl) + ', ' + move + '\n')
    f.write('\tdb 0 ; no more level-up moves\n')
    print('Wrote level-up learnset and evolution to data/pokemon/evos_attacks.asm')

### egg moves ###
# egg move pointers
with open('data/pokemon/egg_move_pointers.asm', 'r+') as f:
    data = f.readlines()
    if(species_data.evolution_chain.chain.species.id == species.id): # if species is beginning of evolution chain
        insert_file(f, data, 'assert_table_length NUM_POKEMON', '\tdw ' + name_as_variable + 'EggMoves\n')
    else:
        insert_file(f, data, 'assert_table_length NUM_POKEMON', '\tdw NoEggMoves\n')
    print('Wrote egg move pointer to data/pokemon/egg_move_pointers.asm')

if(species_data.evolution_chain.chain.species.id == species.id):
    # create list of egg moves
    egg_moves = []
    for x in species.moves:
        for i in range(len(x.version_group_details)):
            if x.version_group_details[-(1+i)].move_learn_method.name == 'egg':
                egg_moves.append(create_constant(x.move.name))
                break
    print('Found list of egg moves')
    
    # write egg moves to asm
    with open('data/pokemon/egg_moves.asm', 'r+') as f:
        data = f.readlines()
        egg_moves_s = name_as_variable + 'EggMoves\n'
        for move in egg_moves:
            if move in pokecrystal_moves:
                egg_moves_s += '\tdb ' + move + '\n'
            else:
                egg_moves_s += '\t; db ' + move + '\n'
        egg_moves_s += '\tdb -1 ; end\n\n'
        insert_file(f, data, 'NoEggMoves:', egg_moves_s)
        print('Wrote egg moves to data/pokemon/egg_moves.asm')
else:
    print('Species has no egg moves')

### cry ###
with open('data/pokemon/cries.asm', 'r+') as f:
    data = f.readlines()
    insert_file(f, data, 'assert_table_length NUM_POKEMON', '\tmon_cry CRY_NIDORAN_M,     0,    0 ; ' + constant + '\n')
    print('Wrote cry placeholder to data/pokemon/cries.asm')

### icon ###
if(flag_unique_icons):
    # create icon constant
    with open('constants/icon_constants.asm', 'r+') as f:
        data = f.readlines()
        insert_file(f, data, 'DEF NUM_ICONS EQU const_value - 1', '\tconst ICON_' + constant + '\n')
        print('Wrote new icon constant to constants/icon_constants.asm')

with open('data/pokemon/menu_icons.asm', 'r+') as f:
    data = f.readlines()
    if(flag_unique_icons):
        insert_file(f, data, 'assert_table_length NUM_POKEMON', '\tdb ICON_' + constant + '\n')
        print('Wrote icon to data/pokemon/menu_icons.asm')
    else:
        insert_file(f, data, 'assert_table_length NUM_POKEMON', '\tdb ICON_BULBASAUR   ; ' + constant + '\n')
        print('Wrote icon placeholder to data/pokemon/menu_icons.asm')

### pokedex entry ###
# create dex entry asm
dex_entry_asm = 'data/pokemon/dex_entries/' + name_as_filename + '.asm'
with open(dex_entry_asm, 'w+'):
    print('Created file: ' + dex_entry_asm)

# create genus name
genus = species_data.genera[7].genus
genus = genus[0:genus.find(' Pokémon')] # truncate ending
genus = genus.upper()
genus = genus[:11] # max limit
genus = genus + '@' # padding
genus = '"' + genus + '"'
print('Created genus name: ' + genus)

# create height
height_cm = species.height * 10 # convert decimeters to centimeters
height_inches = round(height_cm * 0.393701) # convert centimeters to inches
height_feet = str(int(height_inches / 12))
height_remainder = str(height_inches % 12)
if len(height_remainder) == 1:
    height_remainder = '0' + height_remainder
height = height_feet + height_remainder
print('Converted height: ' + height)

# create weight
weight_kg = species.weight / 10 # convert hectograms to kilograms
weight_lb = weight_kg * 2.20462262 # convert kilograms to pounds
weight = str(round(weight_lb * 10))
print('Converted weight: ' + weight)

# TODO: dex entry contents

with open(dex_entry_asm, 'a') as f:
    f.write('\tdb ' + genus + ' ; species name\n')
    f.write('\tdw ' + height + ', ' + weight + ' ; height, weight\n\n')
    # TODO: write dex entry contents
    print('Wrote dex entry to ' + dex_entry_asm)
