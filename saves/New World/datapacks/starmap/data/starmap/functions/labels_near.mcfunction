kill @e[type=minecraft:text_display,tag=starmap_label]
execute as @e[type=minecraft:armor_stand,tag=starmap_star,distance=..15] at @s run summon minecraft:text_display ~ ~2 ~ {Tags:["starmap_label"],billboard:"center",scale:[0.7f,0.7f,0.7f],text:'{"nbt":"CustomName","entity":"@s","interpret":true}'}
