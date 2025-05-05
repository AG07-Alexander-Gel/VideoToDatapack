##
 # loop that checks every 18 ticks
##
execute as @e[tag=origin_location] run execute at @s run function video:frames/frame0
execute as @e[tag=clear_location] run execute at @s run function video:frames/clear
schedule function video:check/slowcheck 30t
