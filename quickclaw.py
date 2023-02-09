### quickclaw.py ###
# script to automate adding new pokemon species to pokecrystal

import pokebase as pb
import io
import sys

### utils ###
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
def convert_constant(s: str) -> str:
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

pokecrystal_moves = []
pokecrystal_items = []
pokecrystal_types = []
pokecrystal_growth_rates = []
pokecrystal_tms = []

class QuickclawSpecies:
    def __init__(self, pokemon, pokemon_data):
        self.pokemon = pokemon
        self.pokemon_data = pokemon_data

    pokemon: pb.APIResource
    pokemon_data: pb.APIResource

    constant: str
    name: str
    name_as_filename: str
    name_as_variable: str

    base_stat_total: str
    hp: str
    attack: str
    defense: str
    special_attack: str
    special_defense: str
    speed: str

    ev_hp: str
    ev_attack: str
    ev_defense: str
    ev_special_attack: str
    ev_special_defense: str
    ev_speed: str

    type1: str
    type2: str
    catch_rate: str
    base_stat: str
    item_common: str
    item_rare: str
    gender_ratio: str
    step_cycles_to_hatch: str
    growth_rate: str
    egg_group1: str
    egg_group2: str

    moves: list
    tm_compat: list
    egg_moves: list

    genus: str
    height: str
    weight: str
    dex_entry: list

def get_species() -> QuickclawSpecies:
    if (len(sys.argv) > 1):
        species_query = sys.argv[1]
    else:
        print('Error: No species given')
        quit()
    return QuickclawSpecies(pb.pokemon(species_query), pb.pokemon_species(species_query))

def get_flags() -> dict:
    args = []
    if (len(sys.argv) > 2):
        for x in range(2, len(sys.argv)):
            args.append(sys.argv[x])
    flags = {
        'evs': False,
        'decap': False,
        'pc16': False,
        'no_filler_data': False,
        'no_filler_pics': False,
        'unique_icons': False,
        'fix_footprints': False,
        'fix_dba_pic': False
    }
    for flag in flags:
        if '-'+flag in args:
            flags[flag] = True
    return flags

def pokecrystal_constant(species, flags):
    species.constant = convert_constant(species.pokemon_data.names[8].name)
    print('Created constant: ' + species.constant)

    with open('constants/pokemon_constants.asm', 'r+') as f:
        data = f.readlines()
        insert_file(f, data, 'NUM_POKEMON EQU const_value', '\tconst ' + species.constant + '\n')
        print('Wrote constant ' + species.constant + ' to constants/pokemon_constants.asm')

def pokecrystal_name(species, flags):
    species.name = species.pokemon_data.names[8].name
    if flags['decap'] == False:
        species.name = species.name.upper()
    species.name = pad_string(species.name, 10, '@', False)
    species.name = '"' + species.name + '"'
    print('Created name: ' + species.name)

    with open('data/pokemon/names.asm', 'r+') as f:
        data = f.readlines()
        insert_file(f, data, 'assert_table_length NUM_POKEMON', '\tdb ' + species.name + '\n')
        print('Wrote name ' + species.name + ' to data/pokemon/names.asm')

def pokecrystal_base_data(species, flags):
    # create stats asm
    species.name_as_filename = species.constant.lower()
    stats_asm = 'data/pokemon/base_stats/' + species.name_as_filename + '.asm'
    with open(stats_asm, 'w+'):
        print('Created file: ' + stats_asm)

    with open(stats_asm, 'a') as f:
        if flags['pc16']:
            f.write('\tdb 0 ; species ID placeholder' + '\n\n')
            print('Wrote species ID placeholder to ' + stats_asm)
        else:
            f.write('\tdb ' + species.constant + '\n\n')
            print('Wrote species ID to ' + stats_asm)

    # base stat total
    bst_temp = 0
    for i in range(0, len(species.pokemon.stats)):
        bst_temp += species.pokemon.stats[i].base_stat
    species.base_stat_total = str(bst_temp)
    # base stats
    species.hp              = str(species.pokemon.stats[0].base_stat)
    species.attack          = str(species.pokemon.stats[1].base_stat)
    species.defense         = str(species.pokemon.stats[2].base_stat)
    species.special_attack  = str(species.pokemon.stats[3].base_stat)
    species.special_defense = str(species.pokemon.stats[4].base_stat)
    species.speed           = str(species.pokemon.stats[5].base_stat)

    print('Found stats: \tBST:' + species.base_stat_total + 
    '\nHP: ' + species.hp + '\tATK:' + species.attack + '\tDEF:' + species.defense + 
    '\nSPD:' + species.speed + '\tSAT:' + species.special_attack + '\tSDF:' + species.special_defense)
    species.hp = pad_string(species.hp, 3)
    species.attack = pad_string(species.attack, 3)
    species.defense = pad_string(species.defense, 3)
    species.speed = pad_string(species.speed, 3)
    species.special_attack = pad_string(species.special_attack, 3)
    species.special_defense = pad_string(species.special_defense, 3)

    # write base stats to asm
    with open(stats_asm, 'a') as f:
        f.write('\tdb ' + species.hp + ', ' + species.attack + ', ' + species.defense + ', ' + species.speed + ', ' 
        + species.special_attack + ', ' + species.special_defense + ' ; ' + species.base_stat_total + ' BST\n')
        print('Wrote stats to ' + stats_asm)

    # ev yield
    if flags['evs']:
        species.ev_hp              = str(species.pokemon.stats[0].effort)
        species.ev_attack          = str(species.pokemon.stats[1].effort)
        species.ev_defense         = str(species.pokemon.stats[2].effort)
        species.ev_special_attack  = str(species.pokemon.stats[3].effort)
        species.ev_special_defense = str(species.pokemon.stats[4].effort)
        species.ev_speed           = str(species.pokemon.stats[5].effort)

        print('Found ev yields:' +
        '\nHP: ' + species.ev_hp + '\tATK:' + species.ev_attack + '\tDEF:' + species.ev_defense + 
        '\nSPD:' + species.ev_speed + '\tSAT:' + species.ev_special_attack + '\tSDF:' + species.ev_special_defense)

        # write evs to asm
        with open(stats_asm, 'a') as f:
            f.write('\tevs  ' + species.ev_hp + ',   ' + species.ev_attack + ',   ' + species.ev_defense + ',   ' 
            + species.ev_speed + ',   ' + species.ev_special_attack + ',   ' + species.ev_special_defense + '\n')
            print('Wrote ev yields to ' + stats_asm)

    with open(stats_asm, 'a') as f:
        f.write('\t;   hp  atk  def  spd  sat  sdf\n\n')

    # types
    with open('constants/type_constants.asm', 'r') as f:
        data = f.readlines()
        find_entries_in_range(data, pokecrystal_types, 'const_def', 'DEF TYPES_END EQU const_value', 7, '\n')
        print('Found all valid types defined in pokecrystal')

    species.type1 = str(species.pokemon.types[0].type).upper()
    if len(species.pokemon.types) == 1: # if species only has 1 type
        species.type2 = species.type1 # duplicate primary type
    else:
        species.type2 = str(species.pokemon.types[1].type).upper()
    if species.type1 == 'PSYCHIC':
        species.type1 = 'PSYCHIC_TYPE'
    if species.type2 == 'PSYCHIC':
        species.type2 = 'PSYCHIC_TYPE'
    if species.type1 not in pokecrystal_types:
        print('Warning: ' + species.type1 + ' is not defined in pokecrystal. Setting to NORMAL')
        species.type1 = 'NORMAL'
    if species.type2 not in pokecrystal_types:
        print('Warning: ' + species.type2 + ' is not defined in pokecrystal. Setting to NORMAL')
        species.type2 = 'NORMAL'
    print('Found types: ' + species.type1 + ', ' + species.type2)

    with open(stats_asm, 'a') as f:
        f.write('\tdb ' + species.type1 + ', ' + species.type2 + ' ; type\n')
        print('Wrote types to ' + stats_asm)

    # catch rate
    species.catch_rate = str(species.pokemon_data.capture_rate)
    print('Found catch rate: ' + species.catch_rate)

    with open(stats_asm, 'a') as f:
        f.write('\tdb ' + species.catch_rate + ' ; catch rate\n')
        print('Wrote catch rate to ' + stats_asm)

    # base exp
    species.base_exp = str(species.pokemon.base_experience)
    print('Found base exp: ' + species.base_exp)

    with open(stats_asm, 'a') as f:
        f.write('\tdb ' + species.base_exp + ' ; base exp\n')
        print('Wrote base exp to ' + stats_asm)

    # held items
    with open('constants/item_constants.asm', 'r') as f:
        data = f.readlines()
        find_entries_in_range(data, pokecrystal_items, 'const_def', 'DEF NUM_ITEMS EQU const_value - 1', 7)
        print('Found valid items defined in pokecrystal')

    species.item_common = 'NO_ITEM'
    species.item_rare = 'NO_ITEM'
    for x in species.pokemon.held_items:
        if x.version_details[-1].rarity == 100:
            species.item_common = convert_constant(str(x.item))
            species.item_rare = species.item_common
        if x.version_details[-1].rarity == 50:
            species.item_common = convert_constant(str(x.item))
        if x.version_details[-1].rarity == 5:
            species.item_rare = convert_constant(str(x.item))
    print('Found items: ' + species.item_common + ', ' + species.item_rare)

    if species.item_common not in pokecrystal_items:
        print('Warning: ' + species.item_common + ' is not defined in pokecrystal. Setting to NO_ITEM')
        species.item_common = 'NO_ITEM'
    if species.item_rare not in pokecrystal_items:
        print('Warning: ' + species.item_rare + ' is not defined in pokecrystal. Setting to NO_ITEM')
        species.item_rare = 'NO_ITEM'

    with open(stats_asm, 'a') as f:
        f.write('\tdb ' + species.item_common + ', ' + species.item_rare + ' ; items\n')
        print('Wrote items to ' + stats_asm)

    # gender ratio
    gender_ratios = { '0': 'GENDER_F0', '1': 'GENDER_F12_5', '2': 'GENDER_F25', '4': 'GENDER_F50', '6': 'GENDER_F75', 
    '8': 'GENDER_F100', '-1': 'GENDER_UNKNOWN' }
    species.gender_ratio = gender_ratios[str(species.pokemon_data.gender_rate)]
    print('Found gender ratio: ' + species.gender_ratio)

    with open(stats_asm, 'a') as f:
        f.write('\tdb ' + species.gender_ratio + ' ; gender ratio\n')
        print('Wrote gender ratio to ' + stats_asm)

    # unknown 1 data
    if flags['no_filler_data'] == False:
        with open(stats_asm, 'a') as f:
            f.write('\tdb 100 ; unknown 1\n')
            print('Wrote unknown 1 to ' + stats_asm)

    # step cycles to hatch
    species.step_cycles_to_hatch = str(species.pokemon_data.hatch_counter)
    print('Found step cycles to hatch: ' + species.step_cycles_to_hatch)

    with open(stats_asm, 'a') as f:
        f.write('\tdb ' + species.step_cycles_to_hatch + ' ; step cycles to hatch\n')
        print('Wrote step cycles to hatch to ' + stats_asm)

    # unknown 2 data
    if flags['no_filler_data'] == False:
        with open(stats_asm, 'a') as f:
            f.write('\tdb 5 ; unknown 2\n')
            print('Wrote unknown 2 to ' + stats_asm)

    # incbin
    with open(stats_asm, 'a') as f:
        f.write('\tINCBIN "gfx/pokemon/' + species.name_as_filename + '/front.dimensions"\n')
        print('Wrote sprite dimensions to ' + stats_asm)

    # beta pics
    if flags['no_filler_pics'] == False:
        with open(stats_asm, 'a') as f:
            f.write('\tdw NULL, NULL ; unused (beta front/back pics)\n')
            print('Wrote unused beta pics to ' + stats_asm)

    # growth rate
    with open('constants/pokemon_data_constants.asm', 'r') as f:
        data = f.readlines()
        find_entries_in_range(data, pokecrystal_growth_rates, 'wBaseGrowthRate', 'DEF NUM_GROWTH_RATES EQU const_value', 7, '\n')
        print('Found all valid growth rates defined in pokecrystal')

    growth_rates = { 'medium': 'GROWTH_MEDIUM_FAST', 'medium-slow': 'GROWTH_MEDIUM_SLOW', 'fast': 'GROWTH_FAST', 
    'slow': "GROWTH_SLOW", 'slow-then-very-fast': 'GROWTH_ERRATIC', 'fast-then-very-slow': 'GROWTH_FLUCTUATING' }
    species.growth_rate = growth_rates[str(species.pokemon_data.growth_rate)]
    print('Found growth rate: ' + species.growth_rate)
    if species.growth_rate not in pokecrystal_growth_rates:
        print('Warning: ' + species.growth_rate + ' is not defined in pokecrystal. Setting to NORMAL')
        species.growth_rate = 'GROWTH_MEDIUM_FAST'

    with open(stats_asm, 'a') as f:
        f.write('\tdb ' + species.growth_rate + ' ; growth rate\n')
        print('Wrote growth rate to ' + stats_asm)

    # egg groups
    egg_groups = { 'monster': 'EGG_MONSTER', 'water1': 'EGG_WATER_1', 'bug': 'EGG_BUG', 'flying': 'EGG_FLYING', 
    'ground': 'EGG_GROUND', 'fairy': 'EGG_FAIRY', 'plant': 'EGG_PLANT', 'humanshape': 'EGG_HUMANSHAPE',
    'water3': 'EGG_WATER_3', 'mineral': 'EGG_MINERAL', 'indeterminate': 'EGG_INDETERMINATE', 'water2': 'EGG_WATER_2', 
    'ditto': 'EGG_DITTO', 'dragon': 'EGG_DRAGON', 'no-eggs': 'EGG_NONE' }
    species.egg_group1 = egg_groups[str(species.pokemon_data.egg_groups[0])]
    if len(species.pokemon_data.egg_groups) == 1: # if species only has 1 egg group
        species.egg_group2 = species.egg_group1 # duplicate egg group
    else:
        species.egg_group2 = egg_groups[str(species.pokemon_data.egg_groups[1])]
    print('Found egg groups: ' + species.egg_group1 + ', ' + species.egg_group2)

    with open(stats_asm, 'a') as f:
        f.write('\tdn ' + species.egg_group1 + ', ' + species.egg_group2 + ' ; egg groups\n\n')
        print('Wrote egg groups to ' + stats_asm)

    # tm/hm/mt learnset
    # create list of moves
    species.moves = []
    for x in species.pokemon.moves:
        lvl = 0
        for i in range(len(x.version_group_details)):
            lvl = x.version_group_details[-(1+i)].level_learned_at
            if(lvl != 0):
                break
        move = convert_constant(str(x.move))
        if move == 'PSYCHIC':
            move = 'PSYCHIC_M'
        species.moves.append((lvl, move))
    species.moves.sort()
    print('Found valid moves for species')

    # create list of valid tms from pokecrystal
    with open('constants/item_constants.asm', 'r') as f:
        data = f.readlines()
        # tms
        find_entries_in_range(data, pokecrystal_tms, 'DEF TM01 EQU const_value', 'DEF NUM_TMS EQU __tmhm_value__ - 1', 8)
        # hms
        find_entries_in_range(data, pokecrystal_tms, 'DEF HM01 EQU const_value', 'DEF NUM_HMS EQU __tmhm_value__ - NUM_TMS - 1', 8)
        # tutor moves
        find_entries_in_range(data, pokecrystal_tms, 'DEF MT01 EQU const_value', 'DEF NUM_TUTORS = __tmhm_value__ - NUM_TMS - NUM_HMS - 1', 8)
        print('Found valid tms/hms/tutors defined in pokecrystal')

    # tm compatibility for this species
    species.tm_compat = []
    for move in pokecrystal_tms:
        if any([move in tup for tup in species.moves]):
            species.tm_compat.append(move)
    print('Created tm compatibility for species')

    with open(stats_asm, 'a') as f:
        f.write('\t; tm/hm learnset\n\ttmhm ')
        if(len(species.tm_compat) != 0):
            last_item = species.tm_compat[-1]
            for move in species.tm_compat:
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

def pokecrystal_learnset(species, flags):
    # evos attack pointers
    name_as_variable_temp = species.constant.title()
    species.name_as_variable = ''
    for c in name_as_variable_temp:
        if c.isalpha():
            species.name_as_variable += c
    with open('data/pokemon/evos_attacks_pointers.asm', 'r+') as f:
        data = f.readlines()
        insert_file(f, data, 'assert_table_length NUM_POKEMON', '\tdw ' + species.name_as_variable + 'EvosAttacks\n')
        print('Wrote evos attack pointer to data/pokemon/evos_attacks_pointers.asm')

    # create list of all valid moves from pokecrystal
    with open('constants/move_constants.asm', 'r') as f:
        data = f.readlines()
        find_entries_in_range(data, pokecrystal_moves, 'const_def', 'DEF NUM_ATTACKS EQU const_value - 1', 7)
        print('Found all valid moves defined in pokecrystal')

    # handle evolutions
    evo_chain = evolution_tree_bfs(species.pokemon_data.evolution_chain.chain, species.pokemon.id)
    evolutions_s = ''
    # append to evolutions_s with line according to evolution method
    for i in range(len(evo_chain.evolves_to)):
        evo_trigger = evo_chain.evolves_to[i].evolution_details[0].trigger.name
        evo_species = convert_constant(evo_chain.evolves_to[i].species.names[8].name)
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
            item = convert_constant(str(evo_chain.evolves_to[i].evolution_details[0].item))
            if item not in pokecrystal_items:
                print('Warning: ' + item + ' is not defined in pokecrystal. Disabling evolution ' + evo_species)
                evolutions_s += '\t; db EVOLVE_ITEM, ' + item + ', ' + evo_species + '\n'
            else:
                evolutions_s += '\tdb EVOLVE_ITEM, ' + item + ', ' + evo_species + '\n'
        # trade
        elif(evo_trigger == 'trade'):
            held_item = convert_constant(str(evo_chain.evolves_to[i].evolution_details[0].held_item))
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
        f.write('\n' + species.name_as_variable + 'EvosAttacks:\n')
        f.write(evolutions_s)
        f.write('\tdb 0 ; no more evolutions\n')
        first_move = ''
        for lvl, move in species.moves:
            if lvl == 1:
                first_move = move
                break
        for lvl, move in species.moves[species.moves.index((1, first_move)):]:
            if move in pokecrystal_moves:
                f.write('\tdb ' + str(lvl) + ', ' + move + '\n')
            else:
                f.write('\t; db ' + str(lvl) + ', ' + move + '\n')
        f.write('\tdb 0 ; no more level-up moves\n')
        print('Wrote level-up learnset and evolution to data/pokemon/evos_attacks.asm')

def pokecrystal_egg_moves(species, flags):
    # egg move pointers
    with open('data/pokemon/egg_move_pointers.asm', 'r+') as f:
        data = f.readlines()
        if(species.pokemon_data.evolution_chain.chain.species.id == species.pokemon.id): # if species is beginning of evolution chain
            insert_file(f, data, 'assert_table_length NUM_POKEMON', '\tdw ' + species.name_as_variable + 'EggMoves\n')
        else:
            insert_file(f, data, 'assert_table_length NUM_POKEMON', '\tdw NoEggMoves\n')
        print('Wrote egg move pointer to data/pokemon/egg_move_pointers.asm')

    if(species.pokemon_data.evolution_chain.chain.species.id == species.pokemon.id):
        # create list of egg moves
        species.egg_moves = []
        for x in species.pokemon.moves:
            for i in range(len(x.version_group_details)):
                if x.version_group_details[-(1+i)].move_learn_method.name == 'egg':
                    species.egg_moves.append(convert_constant(x.move.name))
                    break
        print('Found list of egg moves')
        
        # write egg moves to asm
        with open('data/pokemon/egg_moves.asm', 'r+') as f:
            data = f.readlines()
            egg_moves_s = species.name_as_variable + 'EggMoves:\n'
            for move in species.egg_moves:
                if move in pokecrystal_moves:
                    egg_moves_s += '\tdb ' + move + '\n'
                else:
                    egg_moves_s += '\t; db ' + move + '\n'
            egg_moves_s += '\tdb -1 ; end\n\n'
            insert_file(f, data, 'NoEggMoves:', egg_moves_s)
            print('Wrote egg moves to data/pokemon/egg_moves.asm')
    else:
        print('Species has no egg moves')

def pokecrystal_cry(species, flags):
    with open('data/pokemon/cries.asm', 'r+') as f:
        data = f.readlines()
        insert_file(f, data, 'assert_table_length NUM_POKEMON', '\tmon_cry CRY_NIDORAN_M,     0,    0 ; ' + species.constant + '\n')
        print('Wrote cry placeholder to data/pokemon/cries.asm')

def pokecrystal_icon(species, flags):
    if flags['unique_icons']:
        # create icon constant
        with open('constants/icon_constants.asm', 'r+') as f:
            data = f.readlines()
            insert_file(f, data, 'DEF NUM_ICONS EQU const_value - 1', '\tconst ICON_' + species.constant + '\n')
            print('Wrote new icon constant to constants/icon_constants.asm')

    with open('data/pokemon/menu_icons.asm', 'r+') as f:
        data = f.readlines()
        if flags['unique_icons']:
            insert_file(f, data, 'assert_table_length NUM_POKEMON', '\tdb ICON_' + species.constant + '\n')
            print('Wrote icon to data/pokemon/menu_icons.asm')
        else:
            insert_file(f, data, 'assert_table_length NUM_POKEMON', '\tdb ICON_BULBASAUR   ; ' + species.constant + '\n')
            print('Wrote icon placeholder to data/pokemon/menu_icons.asm')

def pokecrystal_dex_entry(species, flags):
    # create dex entry asm
    dex_entry_asm = 'data/pokemon/dex_entries/' + species.name_as_filename + '.asm'
    with open(dex_entry_asm, 'w+'):
        print('Created file: ' + dex_entry_asm)

    # create genus name
    species.genus = species.pokemon_data.genera[7].genus
    species.genus = species.genus[0:species.genus.find(' Pokémon')] # truncate ending
    species.genus = species.genus.upper()
    species.genus = species.genus[:11] # max limit
    species.genus = species.genus + '@' # padding
    species.genus = '"' + species.genus + '"'
    print('Created genus name: ' + species.genus)

    # create height
    height_cm = species.pokemon.height * 10 # convert decimeters to centimeters
    height_inches = round(height_cm * 0.393701) # convert centimeters to inches
    height_feet = str(int(height_inches / 12))
    height_remainder = str(height_inches % 12)
    if len(height_remainder) == 1:
        height_remainder = '0' + height_remainder
    species.height = height_feet + height_remainder
    print('Converted height: ' + species.height)

    # create weight
    weight_kg = species.pokemon.weight / 10 # convert hectograms to kilograms
    weight_lb = weight_kg * 2.20462262 # convert kilograms to pounds
    species.weight = str(round(weight_lb * 10))
    print('Converted weight: ' + species.weight)

    # parse words from shortest flavor_text_entry
    min_len = sys.maxsize
    min_index = 0
    for i in range(len(species.pokemon_data.flavor_text_entries)):
        entry = species.pokemon_data.flavor_text_entries[i]
        if entry.language.name == 'en':
            if len(entry.flavor_text) < min_len:
                min_len = len(entry.flavor_text)
                min_index = i
    entry_words = species.pokemon_data.flavor_text_entries[min_index].flavor_text.split()
    # reconstruct dex_entry
    species.dex_entry = [''] * 6
    line = 0
    for word in entry_words:
        if len(species.dex_entry[line] + word) > 18:
            line += 1
            if line >= len(species.dex_entry):
                print('Warning: full dex entry could not fit')
                break
        if len(species.dex_entry[line]) != 0:
            species.dex_entry[line] += ' '
        species.dex_entry[line] += word
    # convert "Pokémon" to "#MON"
    for i in range(len(species.dex_entry)):
        species.dex_entry[i] = species.dex_entry[i].replace('Pokémon', '#MON')
    print('Parsed lines from dex entry: ' + str(species.dex_entry))

    with open(dex_entry_asm, 'a') as f:
        f.write('\tdb ' + species.genus + ' ; species name\n')
        f.write('\tdw ' + species.height + ', ' + species.weight + ' ; height, weight\n\n')
        # dex entry lines
        f.write('\tdb   "' + species.dex_entry[0] + '"\n')
        f.write('\tnext "' + species.dex_entry[1] + '"\n')
        f.write('\tnext "' + species.dex_entry[2] + '"\n\n')
        f.write('\tpage "' + species.dex_entry[3] + '"\n')
        f.write('\tnext "' + species.dex_entry[4] + '"\n')
        f.write('\tnext "' + species.dex_entry[5] + '@"\n')
        print('Wrote dex entry to ' + dex_entry_asm)

    # dex entry pointer
    with open('data/pokemon/dex_entry_pointers.asm', 'r+') as f:
        data = f.readlines()
        insert_file(f, data, 'assert_table_length NUM_POKEMON', '\tdw ' + species.name_as_variable + 'PokedexEntry\n')
        print('Wrote dex entry pointer to data/pokemon/dex_entry_pointers.asm')

    # dex entry path
    with open('data/pokemon/dex_entries.asm', 'a') as f:
        f.write(species.name_as_variable + 'PokedexEntry::    INCLUDE "' + dex_entry_asm + '"\n')
        print('Wrote dex entry path to data/pokemon/dex_entries.asm')

    # dex order new
    with open('data/pokemon/dex_order_new.asm', 'r+') as f:
        data = f.readlines()
        insert_file(f, data, 'assert_table_length NUM_POKEMON', '\tdb ' + species.constant + '\n')
        print('Wrote dex order new to data/pokemon/dex_order_new.asm')

    # dex order alpha
    with open('data/pokemon/dex_order_alpha.asm', 'r+') as f:
        data = f.readlines()
        alpha_list = []
        find_entries_in_range(data, alpha_list, 'table_width 1, AlphabeticalPokedexOrder', 'assert_table_length NUM_POKEMON', 4, '\n')
        for name in alpha_list:
            if species.constant < name:
                break
        insert_file(f, data, name, '\tdb ' + species.constant + '\n')
        print('Wrote dex order alpha to data/pokemon/dex_order_alpha.asm')

def pokecrystal_footprint(species, flags):
    with open('gfx/footprints.asm', 'r+') as f:
        data = f.readlines()
        if flags['fix_footprints']:
            insert_file(f, data, 'assert_table_length $100', 'INCBIN "gfx/footprints/' + species.name_as_filename + '.1bpp"\n')
        else:
            insert_file(f, data, 'assert_table_length $100', 'INCBIN "gfx/footprints/' + species.name_as_filename + '.1bpp", footprint_top\n'
            + 'INCBIN "gfx/footprints/' + species.name_as_filename + '.1bpp", footprint_bottom\n')
        print('Wrote footprint path to gfx/footprints.asm')

def pokecrystal_animation(species, flags):
    with open('data/pokemon/pic_pointers.asm', 'r+') as f:
        data = f.readlines()
        if flags['fix_dba_pic']:
            insert_file(f, data, 'assert_table_length NUM_POKEMON', '\tdba ' + species.name_as_variable + 'Frontpic\n')
            insert_file(f, data, 'assert_table_length NUM_POKEMON', '\tdba ' + species.name_as_variable + 'Backpic\n')
        else:
            insert_file(f, data, 'assert_table_length NUM_POKEMON', '\tdba_pic ' + species.name_as_variable + 'Frontpic\n')
            insert_file(f, data, 'assert_table_length NUM_POKEMON', '\tdba_pic ' + species.name_as_variable + 'Backpic\n')
        print('Wrote pic pointers to data/pokemon/pic_pointers.asm')

    with open('gfx/pics.asm', 'a') as f:
        f.write('; ' + species.name_as_variable + 'Frontpic: INCBIN "gfx/pokemon/' + species.name_as_filename + '/front.animated.2bpp.lz"\n')
        f.write('; ' + species.name_as_variable + 'Backpic: INCBIN "gfx/pokemon/' + species.name_as_filename + '/back.2bpp.lz"\n')
        print('Wrote pic path to gfx/pics.asm')

    with open('data/pokemon/palettes.asm', 'r+') as f:
        data = f.readlines()
        insert_file(f, data, 'assert_table_length NUM_POKEMON', 'INCBIN "gfx/pokemon/' + species.name_as_filename + '/front.gbcpal", middle_colors\n' 
        + 'INCLUDE "gfx/pokemon/' + species.name_as_filename + '/shiny.pal"\n')
        print('Wrote palette pointers to data/pokemon/palettes.asm')

    with open('gfx/pokemon/anim_pointers.asm', 'r+') as f:
        data = f.readlines()
        insert_file(f, data, 'assert_table_length NUM_POKEMON', '\tdw ' + species.name_as_variable + 'Animation\n')
        print('Wrote anim pointers to gfx/pokemon/anim_pointers.asm')

    with open('gfx/pokemon/anims.asm', 'r+') as f:
        data = f.readlines()
        insert_file(f, data, 'EggAnimation', species.name_as_variable + 'Animation: INCLUDE "gfx/pokemon/' + species.name_as_filename + '/anim.asm"\n')
        print('Wrote anim path to gfx/pokemon/anims.asm')

    with open('gfx/pokemon/idle_pointers.asm', 'r+') as f:
        data = f.readlines()
        insert_file(f, data, 'assert_table_length NUM_POKEMON', '\tdw ' + species.name_as_variable + 'AnimationIdle\n')
        print('Wrote idle pointer to gfx/pokemon/idle_pointers.asm')

    with open('gfx/pokemon/idles.asm', 'r+') as f:
        data = f.readlines()
        insert_file(f, data, 'EggAnimationIdle', species.name_as_variable + 'AnimationIdle: INCLUDE "gfx/pokemon/' + species.name_as_filename + '/anim_idle.asm"\n')
        print('Wrote idle path to gfx/pokemon/idles.asm')

    with open('gfx/pokemon/bitmask_pointers.asm', 'r+') as f:
        data = f.readlines()
        insert_file(f, data, 'assert_table_length NUM_POKEMON', '\tdw ' + species.name_as_variable + 'Bitmasks\n')
        print('Wrote bitmask pointer to gfx/pokemon/bitmask_pointers.asm')

    with open('gfx/pokemon/bitmasks.asm', 'r+') as f:
        data = f.readlines()
        insert_file(f, data, 'EggBitmasks', species.name_as_variable + 'Bitmasks: INCLUDE "gfx/pokemon/' + species.name_as_filename + '/bitmask.asm"\n')
        print('Wrote bitmask path to gfx/pokemon/bitmasks.asm')

    with open('gfx/pokemon/frame_pointers.asm', 'r+') as f:
        data = f.readlines()
        insert_file(f, data, 'assert_table_length NUM_POKEMON', '\tdw ' + species.name_as_variable + 'Frames\n')
        print('Wrote frame pointer to gfx/pokemon/frame_pointers.asm')

    with open('gfx/pokemon/johto_frames.asm', 'r+') as f:
        data = f.readlines()
        insert_file(f, data, 'EggFrames', species.name_as_variable + 'Frames: INCLUDE "gfx/pokemon/' + species.name_as_filename + '/frames.asm"\n')
        print('Wrote frame path to gfx/pokemon/johto_frames.asm')

def pokecrystal_tables(species, flags):
    with open('data/pokemon/gen1_order.asm', 'r+') as f:
        data = f.readlines()
        insert_file(f, data, 'assert_table_length NUM_POKEMON', '\tdb ' + species.constant + '\n')
        print('Wrote gen1 order to data/pokemon/gen1_order.asm')

def main():
    species = get_species()
    flags = get_flags()

    pokecrystal_constant(species, flags)
    pokecrystal_name(species, flags)
    pokecrystal_base_data(species, flags)
    pokecrystal_learnset(species, flags)
    pokecrystal_egg_moves(species, flags)
    pokecrystal_cry(species, flags)
    pokecrystal_icon(species, flags)
    pokecrystal_dex_entry(species, flags)
    pokecrystal_footprint(species, flags)
    pokecrystal_animation(species, flags)
    pokecrystal_tables(species, flags)

    print('Done')

if __name__ == "__main__":
    main()
