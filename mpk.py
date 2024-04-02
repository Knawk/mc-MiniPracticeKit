"""
TODO

- optimize program code loading
- optimize thrown item ID -> program logic?
"""


import re
import string
import sys


def escape(s, quotes = ''):
    for q in reversed(quotes):
        if q == 's':
            s = s.replace('\\', '\\\\').replace('\'', '\\\'')
        elif q == 'd':
            s = s.replace('\\', '\\\\').replace('"', '\\"')
        else:
            raise Exception(f"invalid quote char: {q}")
    return s


def compile_spu_program(prog):
    prog = re.sub(r'\\\n\s*', '', prog.strip())
    seqs = [[]]
    for line in prog.split('\n'):
        line = line.strip()
        if line.startswith('---'):
            seqs.append([])
        elif line and line[:1] != '#':
            seqs[-1].append(line)

    seq_lists = []
    for seq in seqs:
        l = ','.join('"%s"' % (escape(i, 'd'),) for i in seq)
        seq_lists.append('[%s]' % (l,))
    return '[%s]' % (','.join(s for s in seq_lists),)


# Notes on main program:
#   - storage pk.I is the main instruction buffer
#   - storage pk.H is the halt flag
#   - storage pk.C stores lists of items from containers to be given to player
#   - storage pk.R stores items from white boxes to be given in random order
#   - storage pk.B stores data for auto/potion scripts
#       - pk.B.P stores tags of writable books for potion scripts
#       - pk.B.A stores contents of writable books for auto scripts
#   - objective pk is used for misc scoreboard operations
MAIN_PROGRAM = compile_spu_program(string.Template("""
# setup

tellraw @p [{"text":"MiniPracticeKit v0.5 activated!","color":"aqua","bold":true}]
scoreboard objectives add pk dummy
gamerule announceAdvancements false

# save auxiliary programs
data modify storage pg ~ set from entity @e[tag=C,limit=1] HandItems[0].tag

# clean up from bootstrap process
execute at @e[tag=V] run fill ~ ~1 ~ ~15 ~1 ~2 bedrock
execute at @e[tag=C] run fill ~ ~-1 ~ ~ ~1 ~ air
kill @e[tag=C]

# detect if async chunk loading is enabled. ?A is nothing pre-20w45a, else 0
execute store success score ?A pk if block 0 -64 0 tuff

# detect eye of ender offset. ?O will be nothing pre-22w11a, otherwise 0
execute store success score ?O pk if block 0 -64 0 mud

# detect version's locate command, copy appropriate locate sequences into L0
scoreboard players reset ?L2 pk
execute store success score ?L2 pk run locate Fortress
execute if score ?L2 pk matches 0 run data modify storage pg ~.L0 set from storage pg ~.L2
scoreboard players reset ?L1 pk
execute store success score ?L1 pk run locate fortress
execute if score ?L1 pk matches 0 run data modify storage pg ~.L0 set from storage pg ~.L1

# track thrown triggers
data remove storage pk T
execute at @p as @e[type=item,distance=..32] run tag @s add T

# save triggers from barrels
data remove storage pk C
execute as @e[tag=T,type=item,nbt={Item:{id:"minecraft:barrel"}}] \\
    run data modify storage pk C append from entity @s Item.tag.BlockEntityTag.Items

execute if data storage pk C[] run data modify storage pk I prepend from storage pk I[0]
execute if data storage pk {C:[]} run data modify storage pk I[0] set value []

# break barrels, tag triggers
setblock 8 ~ 8 chest{CustomName:"$chest_name"}
data modify block 8 ~ 8 Items set from storage pk C[0]
setblock 8 ~ 8 air destroy
execute positioned 8 ~ 8 run kill @e[type=item,distance=..1,nbt={Item:{id:"minecraft:chest",tag:{display:{Name:"$chest_name"}}}}]
execute positioned 8 ~ 8 run tag @e[type=item,distance=..1] add T
data remove storage pk C[0]

---

# save trigger IDs
execute as @e[tag=T] run data modify storage pk T append from entity @s Item.id

# save trigger modes
execute as @e[tag=T,nbt={Item:{id:"minecraft:obsidian"}}] \\
    store result score BM pk \\
    run data get entity @s Item.Count

# tag item containers
tag @e[tag=T,nbt={Item:{id:"minecraft:chest"}}] add I
tag @e[tag=T,nbt={Item:{id:"minecraft:white_shulker_box"}}] add I
tag @e[tag=T,nbt={Item:{id:"minecraft:brown_shulker_box"}},sort=random,limit=1] add I
tag @e[tag=T,nbt={Item:{id:"minecraft:red_shulker_box"}},sort=random,limit=1] add I
tag @e[tag=T,nbt={Item:{id:"minecraft:orange_shulker_box"}},sort=random,limit=1] add I
tag @e[tag=T,nbt={Item:{id:"minecraft:yellow_shulker_box"}},sort=random,limit=1] add I

# add randomize marker to white shulker boxes
execute as @e[tag=I,nbt={Item:{id:"minecraft:white_shulker_box"}}] \\
    run data modify entity @s Item.tag.BlockEntityTag.Items append value {Slot:-1b}

# save items from item containers
data remove storage pk C
execute as @e[tag=I] \\
    run data modify storage pk C append from entity @s Item.tag.BlockEntityTag.Items

data remove storage pk B
# save potion scripts
execute as @e[\\
    tag=T,type=item,\\
    nbt={Item:{id:"minecraft:writable_book"}},\\
    nbt=!{Item:{tag:{display:{Name:'{"text":"AUTO"}'}}}}\\
    ] \\
    run data modify storage pk B.P append from entity @s Item.tag
# save auto scripts
execute as @e\\
    [tag=T,type=item,\\
    nbt={Item:{id:"minecraft:writable_book",tag:{display:{Name:'{"text":"AUTO"}'}}\\
    }}] \\
    run data modify storage pk B.A append from entity @s Item.tag.pages

execute if entity @e[tag=T] run data modify storage pk I[0] set value []
say No triggers found!
tellraw @p {\\
    "text":"Visit the website for info!",\\
    "color":"aqua",\\
    "underlined":"true",\\
    "clickEvent":{"action":"open_url","value":"http://mpk.knawk.net"}\\
}

---

execute if entity @e[tag=T] run clear @p
kill @e[tag=T]

---

# create potions from writable books

execute if data storage pk B.P[] run data modify storage pk I prepend from storage pk I[0]
execute unless data storage pk B.P[0] run data modify storage pk I[0] set value []

# create item
data modify storage pk B.i append value \\
    {id:"lingering_potion",Count:1b,tag:{\\
        CustomPotionColor:65535,HideFlags:32,display:{\\
            Name:'{"text":"Unnamed Script"}',\\
            Lore:['{"text":"MiniPracticeKit script"}']\\
        }\\
    }}
execute store result storage pk B.i[-1].Slot byte 1 run scoreboard players get $$bp pk
data modify storage pk B.i[-1].tag.S set from storage pk B.P[0].pages
data modify storage pk B.i[-1].tag.display.Name set from storage pk B.P[0].display.Name

scoreboard players add $$bp pk 1
data remove storage pk B.P[0]

---

# prepare to give potions to player
data modify storage pk C append from storage pk B.i

---

# align player to ensure correct pickup order
execute at @p align xz run tp @p ~.5 ~ ~.5

data modify storage pk I prepend from storage pk I[0]

# reify items from C[0]
execute at @p run setblock ~ ~ ~ chest{CustomName:"$chest_name"}
execute at @p run data modify block ~ ~ ~ Items set from storage pk C[0]
execute at @p run setblock ~ ~ ~ air destroy
execute at @p run kill @e[type=item,distance=..4,nbt={Item:{id:"minecraft:chest",tag:{display:{Name:"$chest_name"}}}}]

# if C[0] has an item with the randomize marker, cache them in R...
data remove storage pk R
execute at @p if data storage pk C[0][{Slot:-1b}] \\
    as @e[type=item,distance=..4,tag=!CI,sort=random] \\
    run data modify storage pk R append from entity @s Item
execute at @p if data storage pk R[] \\
    run kill @e[type=item,distance=..4,tag=!CI]

data remove storage pk C[0]
execute at @p run tag @e[type=item,distance=..4] add CI

execute unless data storage pk C[] unless data storage pk R[] \\
    run data remove storage pk I[1]

# ...then insert the items from R individually to C in a random order
execute if data storage pk R[] \\
    run data modify storage pk I[0] set from storage pg ~.Z[2]

---

# need 1gt for player to pick up items
data merge storage pk {H:1}

---

# locate BT

execute unless data storage pk {T:["minecraft:heart_of_the_sea"]} run data modify storage pk I[0] set value []
execute if score ?A pk matches 0 run say Warning: locating buried treasure may take a while!
data modify storage pk I[0] insert 1 from storage pg ~.L0.O[0][0]
tellraw @p {"nbt":"O","storage":"pk","interpret":true}

---

# locate shipwreck

execute unless data storage pk {T:["minecraft:oak_boat"]} run data modify storage pk I[0] set value []
data modify storage pk I[0] insert 1 from storage pg ~.L0.O[1][0]
tellraw @p {"nbt":"O","storage":"pk","interpret":true}

---

# locate monument

execute unless data storage pk {T:["minecraft:prismarine"]} run data modify storage pk I[0] set value []
data modify storage pk I[0] insert 1 from storage pg ~.L0.O[2][0]
tellraw @p {"nbt":"O","storage":"pk","interpret":true}

---

# locate bastions/fortresses

execute if data storage pk {T:["minecraft:blaze_rod"]} run data modify storage pk I insert 1 from storage pg ~.L0.N[1]
execute if data storage pk {T:["minecraft:gilded_blackstone"]} run data modify storage pk I insert 1 from storage pg ~.L0.N[0]

---

# go to nether structure(s)

execute \\
    unless data storage pk {T:["minecraft:blaze_rod"]} \\
    unless data storage pk {T:["minecraft:gilded_blackstone"]} \\
    run data modify storage pk I[0] set value []

# if `spreadplayers under` isn't available, prepare to tp to Nether via portal
scoreboard players reset ?SP pk
execute store success score ?SP pk run spreadplayers ~ ~ 0 1 under 0 true @p[tag=,tag=_]

# otherwise load waiting mode program
data modify storage pg _ set from storage pg ~.W
execute if score ?SP pk matches 0 run data modify storage pk I[0] set from storage pg ~.Z[0]

say Nether structure terrain teleportation is not supported in 1.15; sending you to Nether instead...
data modify storage pk T append value "minecraft:netherrack"

---

# go to blind coords

execute unless data storage pk {T:["minecraft:obsidian"]} run data modify storage pk I[0] set value []
# skip enter-stronghold and enter-dimension
data remove storage pk I[1]
data remove storage pk I[1]

# load blind mode program
data modify storage pg _ set from storage pg ~.N0
data modify storage pk I[0] set from storage pg ~.Z[0]

---

# enter stronghold

execute unless data storage pk {T:["minecraft:end_portal_frame"]} run data modify storage pk I[0] set value []
# skip enter-dimension
data remove storage pk I[1]

# load stronghold program
data modify storage pg _ set from storage pg ~.S
data modify storage pk I[0] set from storage pg ~.Z[0]

---

# enter dimension (must appear after enter-stronghold)

setblock 8 ~ 8 air
execute if data storage pk {T:["minecraft:netherrack"]} run setblock 8 ~ 8 nether_portal
execute if data storage pk {T:["minecraft:end_stone"]} run setblock 8 ~ 8 end_portal
execute unless block 8 ~ 8 air run data modify storage pk I[0] set from storage pg ~.Z[1]

---

# set gamemode and difficulty

execute if data storage pk {T:["minecraft:grass_block"]} run gamemode creative @a
execute if data storage pk {T:["minecraft:iron_sword"]} run gamemode survival @a
execute if data storage pk {T:["minecraft:map"]} run gamemode adventure @a
execute if data storage pk {T:["minecraft:ender_eye"]} run gamemode spectator @a

execute if data storage pk {T:["minecraft:leather_helmet"]} run difficulty peaceful
execute if data storage pk {T:["minecraft:golden_helmet"]} run difficulty easy
execute if data storage pk {T:["minecraft:iron_helmet"]} run difficulty normal
execute if data storage pk {T:["minecraft:diamond_helmet"]} run difficulty hard

---

# run auto scripts

data modify storage pg _ set from storage pk B.A
data modify storage pk I[0] set from storage pg ~.Z[0]

---

# cleanup

kill @e[tag=V]
forceload remove all
forceload add 0 0
scoreboard objectives remove pk dummy
gamerule announceAdvancements true

---

# potion script loop

data modify storage pk I prepend from storage pk I[0]
data merge storage pk {H:1}

# only run potion program if there are potions to process
execute at @p run tag @e[type=potion,distance=..8] add P
# this data moved from Potion to Item sometime between 1.15.2 and 1.16.1
execute as @e[tag=P] \\
    unless data entity @s Item.tag.S \\
    unless data entity @s Potion.tag.S \\
    run tag @s remove P
execute as @e[tag=P] run data modify storage pk I insert 1 from entity @s Item.tag.S
execute as @e[tag=P] run data modify storage pk I insert 1 from entity @s Potion.tag.S
kill @e[tag=P]
""").substitute(
    chest_name=escape('{"text":"."}', 'd'),
))


LOCATE_FORMATS = [
    lambda s: f'locate structure {s}',
    lambda s: f'locate {s}',
    lambda s: f'locate {s.title()}',
]


STRONGHOLD_SUBROUTINES = tuple(
    compile_spu_program(string.Template("""
execute as @e[tag=M] at @s positioned ^ ^ ^2048 store result score @s sh run $locate
---
execute as @e[tag=M] at @s positioned ^ ^ ^2048 positioned ~200 ~ ~ store result score $$dE sh run $locate
execute as @e[tag=M] at @s positioned ^ ^ ^2048 positioned ~ ~ ~200 store result score $$dS sh run $locate
---
# /locate uses (8, 8) pre-1.19, and (0, 0) in 1.19+, but we have (4, 4), so we need an appropriate offset
execute unless score ?O pk matches 0 as @e[tag=M] at @s positioned ~4 ~ ~4 store result score @s sh run $locate
execute if score ?O pk matches 0 as @e[tag=M] at @s positioned ~-4 ~ ~-4 store result score @s sh run $locate
---
# delay until marker is loaded
execute if score ?A pk matches 0 unless entity @e[tag=M] run data merge storage pk {H:1}
execute unless entity @e[tag=M] run data modify storage pk I insert 1 from storage pg ~.L0.S[3]
    """).substitute(locate=fmt('stronghold')))
    for fmt in LOCATE_FORMATS
)


LOCATE_OVERWORLD_SUBROUTINES = tuple(
    compile_spu_program(string.Template("""
execute at @p run $bt
---
execute at @p run $ship
---
execute at @p run $monument
    """).substitute(
        bt=fmt('buried_treasure'),
        ship=fmt('shipwreck'),
        monument=fmt('monument'),
    ))
    for fmt in LOCATE_FORMATS
)


# TODO optimize?
LOCATE_NETHER_SUBROUTINES = tuple(
    compile_spu_program(string.Template("""
execute in the_nether positioned 1 ~ 1 run $bastion
tellraw @p {"nbt":"O","storage":"pk","interpret":true}
execute in the_nether positioned 1 ~ -1 run $bastion
tellraw @p {"nbt":"O","storage":"pk","interpret":true}
execute in the_nether positioned -1 ~ 1 run $bastion
tellraw @p {"nbt":"O","storage":"pk","interpret":true}
execute in the_nether positioned -1 ~ -1 run $bastion
tellraw @p {"nbt":"O","storage":"pk","interpret":true}
---
execute in the_nether positioned 1 ~ 1 run $fortress
tellraw @p {"nbt":"O","storage":"pk","interpret":true}
execute in the_nether positioned 1 ~ -1 run $fortress
tellraw @p {"nbt":"O","storage":"pk","interpret":true}
execute in the_nether positioned -1 ~ 1 run $fortress
tellraw @p {"nbt":"O","storage":"pk","interpret":true}
execute in the_nether positioned -1 ~ -1 run $fortress
tellraw @p {"nbt":"O","storage":"pk","interpret":true}
    """).substitute(
        bastion=fmt('bastion_remnant'),
        fortress=fmt('fortress'),
    ))
    for fmt in LOCATE_FORMATS
)


STRONGHOLD_PROGRAM = compile_spu_program(string.Template("""
say Locating stronghold. This may take several seconds...

# setup
forceload add -1 -1 0 0
scoreboard objectives add sh dummy
scoreboard players set ~16 sh 16
scoreboard players set ~400 sh 400
data merge storage sh {p:[0d,61d,0d]}

# spawn markers
# TODO optimize?
summon armor_stand .0 0 .0 {Marker:1b,Tags:["M"]}
summon armor_stand .0 0 .0 {Marker:1b,Tags:["M"],Rotation:[30f]}
summon armor_stand .0 0 .0 {Marker:1b,Tags:["M"],Rotation:[60f]}
summon armor_stand .0 0 .0 {Marker:1b,Tags:["M"],Rotation:[90f]}
summon armor_stand .0 0 .0 {Marker:1b,Tags:["M"],Rotation:[120f]}

# kill all but best marker
data modify storage pk I[0] insert 1 from storage pg ~.L0.S[0][0]
scoreboard players set $$D sh 9999
execute as @e[tag=M] run scoreboard players operation $$D sh < @s sh
execute as @e[tag=M] unless score $$D sh = @s sh run kill @s

# measure distances for trilateration
data modify storage pk I insert 1 from storage pg ~.L0.S[1]

---

scoreboard players operation $$D sh *= $$D sh
scoreboard players operation $$dE sh *= $$dE sh
scoreboard players operation $$dS sh *= $$dS sh

# compute west offset from marker to SH
scoreboard players operation $$dE sh -= $$D sh
scoreboard players remove $$dE sh 40000
scoreboard players operation $$dE sh /= ~400 sh

# compute north offset from marker to SH
scoreboard players operation $$dS sh -= $$D sh
scoreboard players remove $$dS sh 40000
scoreboard players operation $$dS sh /= ~400 sh

# get marker coords
execute as @e[tag=M] at @s positioned ^ ^ ^2.048 run tp @s ~ ~ ~
execute store result score $$X sh run data get entity @e[tag=M,limit=1] Pos[0] 1000
execute store result score $$Z sh run data get entity @e[tag=M,limit=1] Pos[2] 1000

# SH coords = marker coords - offsets
scoreboard players operation $$X sh -= $$dE sh
scoreboard players operation $$Z sh -= $$dS sh

# get (4, 4)
execute if score ?O pk matches 0 run scoreboard players add $$X sh 8
execute if score ?O pk matches 0 run scoreboard players add $$Z sh 8
scoreboard players operation $$X sh /= ~16 sh
scoreboard players operation $$Z sh /= ~16 sh
scoreboard players operation $$X sh *= ~16 sh
scoreboard players operation $$Z sh *= ~16 sh
scoreboard players add $$X sh 4
scoreboard players add $$Z sh 4

say Stronghold found. Loading chunks...

# teleport player
gamerule fallDamage false
setblock 8 ~ 8 end_gateway{ExitPortal:{X:0,Y:999999,Z:0},ExactTeleport:1b}
execute store result block 8 ~ 8 ExitPortal.X int 1 run scoreboard players get $$X sh
execute store result block 8 ~ 8 ExitPortal.Z int 1 run scoreboard players get $$Z sh
data modify storage pk I[0] set from storage pg ~.Z[1]

---

# teleport marker, wait for chunks to load
execute store result storage sh p[0] double 1 run scoreboard players get $$X sh
execute store result storage sh p[2] double 1 run scoreboard players get $$Z sh
data modify entity @e[tag=M,limit=1] Pos set from storage sh p
data modify storage pk I insert 1 from storage pg ~.L0.S[3]

---

# set up markers for search
data merge entity @e[tag=M,limit=1] {Rotation:[0f],Tags:["M","MM"]}
summon armor_stand ~ ~ ~ {Tags:["M"],Marker:1b,Rotation:[90f]}
summon armor_stand ~ ~ ~ {Tags:["M"],Marker:1b,Rotation:[180f]}
summon armor_stand ~ ~ ~ {Tags:["M"],Marker:1b,Rotation:[-90f]}
execute at @e[tag=MM] run tp @e[tag=M] ~ ~ ~

# wait 1gt to avoid maxCommandChainLength
data merge storage pk {H:1}

---

# locate bottom of starter

data modify storage pk J set from storage pk I[0]

execute as @e[tag=M] at @s run tp @s ~ ~-1 ~
execute as @e[tag=M] at @s \\
    if block ^1 ^ ^1 smooth_stone_slab[type=bottom] \\
    if block ^1 ^1 ^-1 smooth_stone_slab \\
    if block ^-1 ^2 ^-1 smooth_stone_slab \\
    if block ^-1 ^3 ^1 smooth_stone_slab \\
    if block ^1 ^4 ^1 smooth_stone_slab \\
    if block ^1 ^5 ^-1 smooth_stone_slab[type=bottom] \\
    run tag @s add B
execute as @e[tag=M] at @s \\
    if block ^-1 ^ ^1 smooth_stone_slab[type=bottom] \\
    if block ^-1 ^1 ^-1 smooth_stone_slab \\
    if block ^1 ^2 ^-1 smooth_stone_slab \\
    if block ^1 ^3 ^1 smooth_stone_slab \\
    if block ^-1 ^4 ^1 smooth_stone_slab \\
    if block ^-1 ^5 ^-1 smooth_stone_slab[type=bottom] \\
    run tag @s add B

# break if bedrock reached
execute at @e[tag=M] if block ~ ~ ~ bedrock run scoreboard players add $$c sh 1
# break if bottom of starter was found
execute as @e[tag=B] run scoreboard players add $$c sh 1
# break if markers were unloaded
execute unless entity @e[tag=M] run scoreboard players add $$c sh 1

execute unless score $$c sh matches 1.. run data modify storage pk I[0] set from storage pk J

execute unless entity @e[tag=B] run say Stronghold starter not found
execute at @e[tag=B] run fill ~-1 ~-1 ~-1 ~1 ~-1 ~1 stone_bricks
execute at @e[tag=B] run say Done! Teleporting to stronghold starter.
execute at @e[tag=B,limit=1] run tp @p ~.5 ~ ~.5 ~ ~
gamerule fallDamage true

# cleanup
kill @e[tag=M]
scoreboard objectives remove sh
""").substitute())


NETHER_TERRAIN_PROGRAM_SETUP = compile_spu_program(string.Template("""
say Finding blind location...

execute in the_nether run forceload add 0 0
# set up air region for `if blocks`
execute in the_nether run fill 0 1 0 7 1 7 bedrock
execute in the_nether run fill 0 0 0 7 0 7 air

# summon ray
execute in the_nether run summon armor_stand 0 96 0 {Tags:[R],Passengers:[{id:armor_stand}]}

--- N0[1]

# if chunk loading is async, wait for ray chunk to load

execute if score ?A pk matches 0 run data merge storage pk {H:1}
execute unless entity @e[tag=R] run data modify storage pk I insert 1 from storage pg ~.N0[1]

--- N0[2]

# use UUID to give ray a random yaw, then face the other 180deg away
execute as @e[tag=R] store result entity @s Rotation[0] float 1 run data get entity @s UUID[0] .001
execute as @e[tag=R] at @s run tp @e[type=armor_stand,tag=!R,distance=..1] ~ ~ ~ ~180 ~
execute at @e[tag=R] as @e[type=armor_stand,distance=..1] run data merge entity @s {Tags:[R],Marker:1}

# start search
scoreboard players set $$_ pk 1
data modify storage pg _ set from storage pg ~.N1
data modify storage pk I[0] set from storage pg ~.Z[0]
""").substitute())


NETHER_TERRAIN_PROGRAM_SEARCH = compile_spu_program(string.Template("""
title @p actionbar ["Searching terrain ",{"score":{"objective":"pk","name":"$$_"}},"/10"]

# for each ray, create 4 markers at 24-block intervals at good blind coords
execute at @e[tag=R] positioned ^ ^ ^184 run forceload add ~-4 ~-4 ~3 ~3
execute at @e[tag=R] positioned ^ ^ ^208 run forceload add ~-4 ~-4 ~3 ~3
execute at @e[tag=R] positioned ^ ^ ^232 run forceload add ~-4 ~-4 ~3 ~3
execute at @e[tag=R] positioned ^ ^ ^256 run forceload add ~-4 ~-4 ~3 ~3
execute at @e[tag=R] positioned ^ ^ ^184 run summon armor_stand ~ ~ ~ {Marker:1,Tags:[M]}
execute at @e[tag=R] positioned ^ ^ ^208 run summon armor_stand ~ ~ ~ {Marker:1,Tags:[M]}
execute at @e[tag=R] positioned ^ ^ ^232 run summon armor_stand ~ ~ ~ {Marker:1,Tags:[M]}
execute at @e[tag=R] positioned ^ ^ ^256 run summon armor_stand ~ ~ ~ {Marker:1,Tags:[M]}

--- N1[1]

# if chunk loading is async, wait for all markers to load

execute if score ?A pk matches 0 run data merge storage pk {H:1}
execute store result $$m pk if entity @e[tag=M]
execute if score $$m pk matches ..7 run data modify storage pk I insert 1 from storage pg ~.N1[1]

# prep for next loop
scoreboard players reset $$n pk

--- N1[2]

# try shifting markers down a few times, tag those centered in an 8x1x8 air cuboid

execute as @e[tag=M,tag=!A] at @s if blocks ~-4 ~ ~-4 ~3 ~ ~3 0 0 0 all run tag @s add A
execute as @e[tag=M,tag=!A] at @s run tp @s ~ ~-8 ~
scoreboard players add $$n pk 1
execute if score $$n pk matches ..4 run data modify storage pk I insert 1 from storage pg ~.N1[2]

--- N1[3]

# keep only markers at the top center of a 8x7x8 air cuboid
execute as @e[tag=A] at @s \\
    unless blocks ~-4 ~-6 ~-4 ~3 ~-6 ~3 0 0 0 all \\
    unless blocks ~-4 ~-5 ~-4 ~3 ~-5 ~3 0 0 0 all \\
    run kill @s
execute as @e[tag=A] at @s \\
    unless blocks ~-4 ~-4 ~-4 ~3 ~-3 ~3 ~-4 ~-6 ~-4 all \\
    unless blocks ~-4 ~-2 ~-4 ~3 ~-1 ~3 ~-4 ~-6 ~-4 all \\
    run kill @s
execute unless entity @e[tag=A] run data remove storage pk I[0][]

# summon dummies around each marker in air
execute at @e[tag=A] align xz run summon armor_stand ~.5 ~-5 ~.5 {Tags:[D]}
execute at @e[tag=D] run summon armor_stand ~ ~ ~-4 {Tags:[D]}
execute at @e[tag=D] run summon armor_stand ~-4 ~ ~1 {Tags:[D]}
execute at @e[tag=D] run summon armor_stand ~2 ~ ~2 {Tags:[D]}

# let the dummies fall, mark the best one that reaches the ground
execute as @e[tag=D] run data merge entity @s {Motion:[0d,-10d],Health:1,Invisible:1}
data merge storage pk {H:1}
data merge storage pk {H:1}
data merge storage pk {H:1}
data merge storage pk {H:1}
data merge storage pk {H:1}
data merge storage pk {H:1}
data merge storage pk {H:1}
execute at @e[tag=A] positioned ~-4 40 ~-4 \\
    run tag @e[dx=8,dz=8,dy=99,sort=nearest,limit=1,tag=D,nbt={OnGround:1b}] add N

--- N1[4]

# clean up markers
kill @e[tag=M]

# rotate rays, increment loop index for next iteration
execute as @e[tag=R] at @s run tp @s ~ ~ ~ ~66 ~
scoreboard players add $$_ pk 1

# if no good dummy is left, and we haven't tried all angles, try again
data modify storage pg _ set from storage pg ~.N1
execute unless entity @e[tag=N] \\
    unless score $$_ pk matches 11 \\
    run data modify storage pk I[0] set from storage pg ~.Z[0]

# clean up rays, and all dummies except at most a good one
kill @e[tag=R]
tag @e[tag=N,limit=1] add NN
kill @e[tag=D,tag=!NN]

# finish up if there's a good dummy
data modify storage pg _ set from storage pg ~.N2
execute as @e[tag=N] run data modify storage pk I[0] set from storage pg ~.Z[0]

say No good terrain found!
execute in the_nether run forceload remove all
""").substitute())


NETHER_TERRAIN_PROGRAM_FINISH = compile_spu_program(string.Template("""
execute if score BM pk matches 3.. run data remove storage pk I[0][]

# build nether-side portal frame
execute at @e[tag=N] run fill ~-1 ~1 ~-1 ~2 ~3 ~1 air
execute at @e[tag=N] run fill ~-1 ~ ~ ~2 ~4 ~ obsidian
execute at @e[tag=N] run fill ~ ~1 ~ ~1 ~3 ~ air

--- N2[1]

say Done! Teleporting...

# add y-offset to avoid teleporting into partial blocks like soul sand
execute at @e[tag=N] run tp @p ~ ~1.063 ~

kill @e[tag=N]

# wait for teleport before adding portal
execute in overworld if entity @p[x=0] run data modify storage pk I prepend from storage pk I[0]
data merge storage pk {H:1}

--- N2[2]

execute in the_nether run forceload remove all

# light portal
execute if score BM pk matches 2.. run data remove storage pk I[0][]
execute at @p run setblock ~ ~1 ~ fire

# wait for teleport before allowing gamemode change
execute in the_nether if entity @p[x=0] run data modify storage pk I prepend from storage pk I[0]
data merge storage pk {H:1}
""").substitute())


WAITING_MODE_PROGRAM = compile_spu_program(string.Template("""
tag @p add W
gamemode creative @p
execute in the_nether run tp @p 0 999999 0

say Entered teleport waiting mode.
say Select desired coordinates above, then press Enter/Return to be teleported to nearby terrain.
say Change your gamemode to cancel.

title @p times 0 2147483647 0
title @p title {"text":"Waiting..."}
title @p subtitle {"text":"Please see instructions in chat."}

---

# if player is in stasis but changed gamemode, exit waiting mode
execute as @p[tag=W,gamemode=!creative] run tag @s remove W
execute if entity @p[tag=!W] run say Gamemode changed, exiting waiting mode.
scoreboard players set $$_ pk 0
execute if entity @p[tag=!W] run data modify storage pk I[0] set value []

# if player has teleported away, exit waiting mode
execute at @p positioned 0 999999 0 run tag @p[distance=8..] remove W
execute if entity @p[tag=!W] run say Teleport detected, sending to nearby terrain.
scoreboard players set $$_ pk 16
execute if entity @p[tag=!W] run data modify storage pk I[0] set value []

# maintain waiting position, loop
execute as @p at @s run tp @s 0 999999 0
data modify storage pk I insert 1 from storage pg ~.W[1]
data merge storage pk {H:1}

---

# cleanup
title @p clear
title @p reset

execute at @p run forceload add ~ ~
execute if score ?A pk matches 0 at @p run forceload add ~-80 ~-80 ~80 ~80
execute at @p run summon armor_stand ~ 0 ~ {Tags:["M"],Marker:1b,Invisible:1b}

---

# enter chunk loading loop only if necessary
execute unless score ?A pk matches 0 run data modify storage pk I[0] set value []

# wait until chunks are loaded
execute at @p \\
    if blocks ~-80 0 ~-80 ~-80 0 ~-80 ~-80 0 ~-80 all \\
    if blocks ~-80 0 ~80 ~-80 0 ~80 ~-80 0 ~80 all \\
    if blocks ~80 0 ~-80 ~80 0 ~-80 ~80 0 ~-80 all \\
    if blocks ~80 0 ~80 ~80 0 ~80 ~80 0 ~80 all \\
    run data modify storage pk I[0] set value []
data merge storage pk {H:1}
data modify storage pk I insert 1 from storage pg ~.W[3]

---

# prevent fall damage when async chunk loading is enabled
effect give @p resistance 3 255

# spreadplayers no matter how the player exited waiting mode
execute at @e[tag=M] run spreadplayers ~ ~ 0 72 under 84 false @p

# @p[tag=W] indicates to try again
tag @p remove W

# exit loop early if out of retries
execute if score $$_ pk matches 0 run data modify storage pk I[0] set value []
scoreboard players remove $$_ pk 1

# try again if standing on nether bricks
execute at @p if block ~ ~-1 ~ nether_bricks run tag @p add W

# try again if within 40 blocks horizontally of marker
execute at @p[tag=!W] \\
    positioned ~-40 0 ~-40 if entity @e[tag=M,dx=80,dy=99,dz=80] \\
    run tag @p add W

# try again if terrain isn't open enough (not enough air within 13x9x13)
execute as @p[tag=!W] at @s store result score @s pk \\
    if blocks ~-6 ~ ~-6 ~6 ~8 ~6 ~-6 ~ ~-6 masked
execute as @p[tag=!W,scores={pk=400..}] run tag @s add W

# loop if need to try again
execute if entity @p[tag=W] run data modify storage pk I insert 1 from storage pg ~.W[4]

---

execute at @e[tag=M] run forceload remove ~-80 ~-80 ~80 ~80
kill @e[tag=M]
""").substitute())


# Single-sequence utility programs.
# Each first instruction is intentionally invalid so that a given program can be loaded with just:
# `data modify storage pk I[0] set from storage pg ~.Z[...]`
UTIL_PROGRAMS = compile_spu_program(string.Template("""
# Loads the program at pg._ into the instruction buffer.
-
data modify storage pk I insert 1 from storage pg _[-1]
data remove storage pg _[-1]
execute if data storage pg _[0] run data modify storage pk I insert 1 from storage pg ~.Z[0]

---

# Teleports the player through the portal block at (8, 0/-64, 8).
-
execute at @p run forceload add ~ ~
execute at @p run summon armor_stand ~ ~1 ~ {Marker:1b,Invisible:1b,Tags:["Z"]}

execute at @p align xyz run tp @p ~.5 ~ ~.5
execute at @p if block 0 0 1 bedrock run clone 8 0 8 8 0 8 ~ ~ ~
execute if block 0 0 1 bedrock run setblock 8 0 8 air
execute at @p run clone 8 -64 8 8 -64 8 ~ ~ ~
setblock 8 -64 8 air

data merge storage pk {H:1}
data merge storage pk {H:1}
data merge storage pk {H:1}

execute at @e[tag=Z] run setblock ~ ~-1 ~ air
kill @e[tag=Z]

---

# Prepend each element of storage pk.R to pk.C as a singleton list;
# e.g. if pk.R = [1, 2, 3] then pk.C will start with [[3], [2], [1], ...]
-

data modify storage pk C prepend value [{Slot:0b}]
data modify storage pk C[0][0] merge from storage pk R[0]

data remove storage pk R[0]
execute if data storage pk R[0] run data modify storage pk I[0] set from storage pg ~.Z[2]

""").substitute())


MPK_LORE = '[\'{"text":"Created by ","extra":[{"text":"Knawk", "color":"aqua"}]}\']'


def give_mpk():
    # phase 3: build SPU
    phase3 = '[{}]'.format(','.join(f"'{escape(i, 's')}'" for i in [
        # always build SPU at (0, 0) to avoid duplicates.
        # no need to manually poll for chunk (0, 0) to load, even with async chunk loading,
        # because the following command blocks won't run until loaded anyway.
        r'execute in overworld run forceload add 0 0',

        # clear any existing SPU, otherwise setblocks fail
        r'fill 0 ~-1 0 4 ~-1 1 bedrock',
        # SPU main loop
        r'setblock 2 ~-1 0 chain_command_block[facing=east]{auto:1b,UpdateLastExecution:0b,Command:"%s"}'
            % ('data modify block ~1 ~ ~ Command set from storage pk I[0][0]',),
        r'setblock 3 ~-1 0 chain_command_block[facing=east]{auto:1b,UpdateLastExecution:0b,CustomName:"%s"}'
            % (escape('{"text":"MPK","color":"aqua"}', 'd'),),
        r'setblock 4 ~-1 0 chain_command_block[facing=south]{auto:1b,UpdateLastExecution:0b,Command:"%s"}'
            % ('data modify storage pk O set from block ~-1 ~ ~ LastOutput',),
        r'setblock 4 ~-1 1 chain_command_block[facing=west]{auto:1b,UpdateLastExecution:0b,Command:"%s"}'
            % ('data remove storage pk I[0][0]',),
        r'setblock 3 ~-1 1 chain_command_block[facing=west]{auto:1b,UpdateLastExecution:0b,Command:"%s"}'
            % ('execute if data storage pk H run setblock ~-2 ~ ~-1 air',),
        r'setblock 2 ~-1 1 chain_command_block[facing=west]{auto:1b,UpdateLastExecution:0b,Command:"%s"}'
            % ('execute unless data storage pk I[0][] run data remove storage pk I[0]',),
        r'setblock 1 ~-1 1 chain_command_block{auto:1b,UpdateLastExecution:0b,Command:"%s"}'
            % ('execute unless data storage pk I[] run setblock ~ ~ ~-1 air',),

        # add trigger last, then run main program
        r'setblock 0 ~-1 0 repeating_command_block[facing=east]{auto:1b,Command:"%s"}'
            % ('execute if data storage pk I[0] run setblock ~1 ~ ~ chain_command_block[facing=east]{auto:1b,UpdateLastExecution:0b,Command:\'data remove storage pk H\'}',),
        r'data modify storage pk I set from entity @e[tag=C,limit=1] HandItems[0].tag.I',
    ]))

    # phase 2: set up 1gt execution of phase 3
    phase2 = '[{}]'.format(','.join(f"'{escape(i, 's')}'" for i in [
        r'setblock ~ ~1 ~ chain_command_block[facing=up]{auto:1b,Command:"data remove entity @e[limit=1,tag=C] HandItems[0].tag.2[0]"}',
        r'gamerule commandBlockOutput false',
        r'execute in overworld run summon armor_stand ~ 0 ~ {Tags:["V"],Marker:1b}',
        r'execute as @e[tag=V] at @s unless block ~ ~ ~ bedrock run tp @s ~ -64 ~',
        r'execute at @e[tag=V] run fill ~ ~1 ~ ~15 ~1 ~ chain_command_block{auto:1b}',
        r'execute at @e[tag=V] run fill ~ ~1 ~1 ~15 ~1 ~1 chain_command_block{auto:1b,Command:"data remove entity @e[tag=C,limit=1] HandItems[0].tag.3[0]"}',
        r'execute at @e[tag=V] run fill ~ ~1 ~2 ~15 ~1 ~2 command_block{auto:1b,Command:"data modify block ~ ~ ~-2 Command set from entity @e[tag=C,limit=1] HandItems[0].tag.3[0]"}',
    ]))

    # phase 1: set up 1cmd/gt execution of phase 2, load programs into carrier
    phase1_new_cmd = 'data modify block ~ ~1 ~ Command set from entity @e[limit=1,tag=C] HandItems[0].tag.2[0]'
    phase1_cmd = 'data modify block ~ ~-1 ~ Command set value "%s"' % (phase1_new_cmd,)
    programs = ','.join(f'{k}:{p}' for k, p in {
        '2': phase2,
        '3': phase3,
        'I': MAIN_PROGRAM,
        'S': STRONGHOLD_PROGRAM,
        'L0': '{S:%s,O:%s,N:%s}' % (STRONGHOLD_SUBROUTINES[0], LOCATE_OVERWORLD_SUBROUTINES[0], LOCATE_NETHER_SUBROUTINES[0]),
        'L1': '{S:%s,O:%s,N:%s}' % (STRONGHOLD_SUBROUTINES[1], LOCATE_OVERWORLD_SUBROUTINES[1], LOCATE_NETHER_SUBROUTINES[1]),
        'L2': '{S:%s,O:%s,N:%s}' % (STRONGHOLD_SUBROUTINES[2], LOCATE_OVERWORLD_SUBROUTINES[2], LOCATE_NETHER_SUBROUTINES[2]),
        'N0': NETHER_TERRAIN_PROGRAM_SETUP,
        'N1': NETHER_TERRAIN_PROGRAM_SEARCH,
        'N2': NETHER_TERRAIN_PROGRAM_FINISH,
        'W': WAITING_MODE_PROGRAM,
        'Z': UTIL_PROGRAMS,
    }.items())
    program_carrier = '{id:armor_stand,Marker:1b,Invisible:1b,HandItems:[{Count:1b,id:egg,tag:{%s}}],Tags:["C"]}' % (programs,)
    phase1 = '{Time:1,BlockState:{Name:chain_command_block,Properties:{facing:up}},TileEntityData:{Command:"%s"},Passengers:[%s]}' % (
        escape(phase1_cmd, 'd'),
        program_carrier,
    )

    # phase 0: load phase 1 command block
    phase0_tag = '{auto:1b,Command:\'execute unless entity @e[tag=C,distance=..1.5] unless entity @e[type=falling_block,distance=..1.5] run summon falling_block ~ ~.5 ~ %s\'}' % (escape(phase1, 's'),)
    display = '{Name:\'%s\',Lore:%s}' % (
        '{"text":"MiniPracticeKit v0.5","bold":true,"italic":false,"color":"aqua"}',
        MPK_LORE,
    )
    phase0 = 'repeating_command_block{CustomModelData:1,BlockStateTag:{facing:"up"},BlockEntityTag:%s,display:%s}' % (
        phase0_tag,
        display,
    )
    print('give @p ' + phase0)


def give_stronghold_portal_book():
    commands = [
        # wait for player teleport
        "data merge storage pk {H:1}",

        "execute at @p run summon area_effect_cloud ~ ~ ~ {Tags:[p],Marker:1}",
        (
            "execute as @e[tag=p] at @s"
            # use player's yaw but not pitch
            " rotated as @p rotated ~ 0"
            # align to horizontal center of block
            " positioned ^1 ^ ^5 align xz positioned ~.5 ~ ~.5"
            " run tp @s ~ ~ ~ ~ ~"
        ),
        # adjust for other possible 5-way layout
        (
            "execute as @e[tag=p] at @s if block ^ ^2 ^6 smooth_stone_slab[type=double]"
            " run tp @s ^2 ^ ^"
        ),

        # roll d13
        "execute as @e[tag=p] store result score @s pk run data get entity @s UUID[0]",
        "scoreboard players set !m pk 13",
        "scoreboard players operation @e[tag=p] pk %= !m pk",

        # set orientation and position
        "execute as @e[tag=p,scores={pk=..4}] at @s run tp @s ~ ~ ~ ~90 ~",
        "execute as @e[tag=p,scores={pk=1}] at @s run tp @s ^ ^ ^1",
        "execute as @e[tag=p,scores={pk=2}] at @s run tp @s ^ ^ ^2",
        "execute as @e[tag=p,scores={pk=3}] at @s run tp @s ^ ^ ^3",
        "execute as @e[tag=p,scores={pk=4}] at @s run tp @s ^ ^ ^4",
        "execute as @e[tag=p,scores={pk=5}] at @s run tp @s ^-2 ^ ^-1",
        "execute as @e[tag=p,scores={pk=6}] at @s run tp @s ^-2 ^ ^",
        "execute as @e[tag=p,scores={pk=7}] at @s run tp @s ^-2 ^ ^1",
        "execute as @e[tag=p,scores={pk=8}] at @s run tp @s ^-2 ^ ^2",
        "execute as @e[tag=p,scores={pk=9}] at @s run tp @s ^-3 ^ ^-1",
        "execute as @e[tag=p,scores={pk=10}] at @s run tp @s ^-3 ^ ^",
        "execute as @e[tag=p,scores={pk=11}] at @s run tp @s ^-3 ^ ^1",
        "execute as @e[tag=p,scores={pk=12}] at @s run tp @s ^-3 ^ ^2",

        # build portal
        "execute at @e[tag=p] run fill ^2 ^-.5 ^ ^-1 ^3.5 ^ obsidian",
        "execute at @e[tag=p] run fill ^1 ^.5 ^ ^ ^2.5 ^ air",
        "execute at @e[tag=p] run setblock ^ ^ ^ fire",

        # turn around with 50% chance
        "execute as @e[tag=p] store result score @s pk run data get entity @s UUID[1]",
        "execute as @e[tag=p,scores={pk=0..}] at @s run tp @s ~ ~ ~ ~180 ~",

        "tp @p @e[tag=p,limit=1]",
    ]
    pages = f"pages:[{",".join('"' + escape(c, "d") + '"' for c in commands)}]"
    name = "Name:'{\"text\":\"AUTO\"}'"
    lore = "Lore:['{\"text\":\"Simulate double travel portal\"}']"
    display = f"display:{{{name},{lore}}}"
    print(f"give @p writable_book{{{pages},{display}}}")


def main():
    if len(sys.argv) == 1:
        give_mpk()
        return
    cmd = sys.argv[1]
    if cmd == "sh_portal":
        give_stronghold_portal_book()
    else:
        print(f"unknown command {cmd}")


if __name__ == '__main__':
    main()
