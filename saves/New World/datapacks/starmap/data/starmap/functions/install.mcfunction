# Star Map installer
# Put this file here:
#   datapack/StarMap/data/starmap/functions/install.mcfunction
#
# Then in Minecraft, run:
#   /function starmap:install
#
# This schedules each placement chunk so the full star map does not run all at once.
# Times are in ticks: 20 ticks = 1 second.

say Starting Star Map generation. Placement chunks are scheduled over time.

schedule function starmap:placever1 1t append
schedule function starmap:placever2 200t append
schedule function starmap:placever3 400t append
schedule function starmap:placever4 600t append
schedule function starmap:placever6 900t append
schedule function starmap:placever8 1100t append
schedule function starmap:placever8a 1300t append
schedule function starmap:placever8b 1340t append
schedule function starmap:placever8c 1380t append
schedule function starmap:placever8d 1420t append
schedule function starmap:placever8e 1460t append
schedule function starmap:placever8f 1500t append
schedule function starmap:placever8g 1540t append
schedule function starmap:placever8h 1580t append
schedule function starmap:placever8i 1620t append
schedule function starmap:labels_near 1700t append

say Star Map generation scheduled. Wait for all chunks to finish.
