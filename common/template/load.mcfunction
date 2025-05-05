##
 # run on reload
##
clear @e[type=minecraft:player] minecraft:shulker_spawn_egg[minecraft:enchantments={sharpness:255}]
clear @e[type=minecraft:player] minecraft:shulker_spawn_egg[minecraft:enchantments={sharpness:127}]

execute as @e[tag=clear_location] run kill @e[tag=clear_location]
execute as @e[tag=clear_location] run kill @e[tag=clear_location]
execute as @e[tag=player_video] run kill @e[tag=player_video]
execute as @e[tag=cc_clear] run kill @e[tag=cc_clear]

give @e[type=minecraft:player] minecraft:shulker_spawn_egg[minecraft:entity_data={id:"armor_stand",Invisible:True,Invulnerable:True,NoGravity:True,Tags:[origin_location]},minecraft:enchantments={sharpness:255},custom_name='{"text": "play","color":"green"}']
give @e[type=minecraft:player] minecraft:shulker_spawn_egg[minecraft:entity_data={id:"armor_stand",Invisible:True,Invulnerable:True,NoGravity:True,Tags:[clear_location]},minecraft:enchantments={sharpness:127},custom_name='{"text": "clear","color":"red"}']

schedule function video:check/slowcheck 18t