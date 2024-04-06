# MiniPracticeKit v0.6

MiniPracticeKit (MPK) is a versatile Minecraft speedrunning practice kit that fits in a single command block.

You can use it to:

- set your inventory (set items, random items, or a mix of both)
- set your gamemode and difficulty
- teleport to the Nether/End
- teleport to terrain near Nether structures
- teleport directly to the stronghold starter staircase
- teleport to good blind travel coordinates (and optionally build a portal and/or go through to the Overworld)
- locate structures (bastion, fortress, buried treasure, shipwreck, monument)
- run your own commands on-demand (for example, to force the dragon to perch)

**Skip to [How to install and use MiniPracticeKit](#how-to-install-and-use-minipracticekit) for download and usage instructions.**

The MPK uses only vanilla Minecraft features: there's no need to install any mods or maintain a separate practice instance.
Save it to a creative hotbar in your [Ranked](https://mcsrranked.com/) and main instances so you always have it on hand!
It also works in Minecraft versions 1.15 to 1.20.4 - you can even directly copy your `hotbar.nbt` file between compatible instances and it'll just work.

## Demo videos (click to watch)

### Eye spy / Stronghold enter

<a href="https://www.youtube.com/watch?v=zGqgCFJYtR0&list=PL3xWUYc3vlEl4QRGBrZFiGGBLKh6V3KhS" target="_blank">
  <img src="https://img.youtube.com/vi/zGqgCFJYtR0/0.jpg" width="480">
</a>

### Blind travel / Nether exit

<a href="https://www.youtube.com/watch?v=-hzr26j5DuQ&list=PL3xWUYc3vlEl4QRGBrZFiGGBLKh6V3KhS" target="_blank">
  <img src="https://img.youtube.com/vi/-hzr26j5DuQ/0.jpg" width="480">
</a>

([Full demo playlist](https://www.youtube.com/playlist?list=PL3xWUYc3vlEl4QRGBrZFiGGBLKh6V3KhS))

## How to install and use MiniPracticeKit

### Installing MPK for the first time

1. If your Minecraft instance is open, close it.
2. Go to your instance's `.minecraft` folder. If there's a `hotbar.nbt` file there, make a copy as backup.
3. Download [`hotbar.nbt`](https://github.com/Knawk/mc-MiniPracticeKit/raw/master/hotbar.nbt) and place it directly in the `.minecraft` folder.

Then start your Minecraft instance and continue to the [Using MPK and presets](#using-mpk-and-presets) section.

### Using MPK and presets

1. Create a new world in Creative mode.
2. Load the slot-1 saved hotbar (with default controls, hold `c` and press `1`). You should see several "preset barrels", and the MPK command block in the last slot.
3. Drop the preset barrel for the split you want to play, and then place the MPK command block.

If you want to edit the inventory in the presets, make other changes, or create your own preset barrels,
then see the [How to customize MPK behavior](#how-to-customize-mpk-behavior) section.

### Updating MPK

If you haven't customized any of the presets, you can update the MPK by simply following the instructions in the [Installing MPK for the first time](installing-mpk-for-the-first-time) section.

If you want to just update the MPK command block without losing your presets, you can do the following:

1. Open or create a Minecraft world in Creative mode.
2. Give yourself a command block by running `/give @p command_block`, and place it.
3. Go to [give-mpk.txt](https://raw.githubusercontent.com/Knawk/mc-MiniPracticeKit/dev/give-mpk.txt), and copy all of the text to your clipboard.
4. Paste the text you just copied into the command block, and click "Done".
5. Activate the command block (for example, with a button) to receive the latest MPK command block (you can hover over the item to see the version number).
6. Replace the old MPK command block with the new one, and save your new hotbar (with default controls, hold `c` and press `1`).

## How to customize MPK behavior

When you place the MiniPracticeKit, it looks for nearby "trigger items" to determine what actions to perform.
They're designed to be easy to customize in-game so you don't need to download or learn any external tools.
The permitted trigger items and the corresponding actions are described below.

|Trigger|Action|Notes|
|-|-|-|
|Chest|Give the items in the chest to the player. If multiple chests are found, items are given in the order that the chests were dropped.|To get a chest with items into your inventory, hold CTRL and press pick-block on a chest with the items you want.|
|White Shulker Box|Gives the items in the shulker box to the player, in a random order.|To get a shulker box with items into your inventory, hold CTRL and press pick-block on a shulker box with the items you want.|
|Brown/Red/Orange/Yellow Shulker Boxes|Picks one random shulker box of each color, and gives its items to the player.|To get a shulker box with items into your inventory, hold CTRL and press pick-block on a shulker box with the items you want.|
|Netherrack, End Stone|Teleport the player to the corresponding dimension. (Netherrack = Nether, End Stone = End)|Incompatible with other teleport actions (and each other).|
|Obsidian|Teleport the player to good first-ring blind coordinates. The number of obsidian items in the stack determine what happens at those coordinates. 1 item = build a portal and go through to the Overworld; 2 items = build a portal only; 3 items = don't build a portal.|Incompatible with other teleport actions. Can be slow because it searches for open nether terrain.|
|End Portal Frame|Teleport the player to a stronghold's starter staircase.|Incompatible with other teleport actions. Always goes to the same stronghold in each world.|
|Gilded Blackstone, Blaze Rod|Send in chat the coordinates of the related Nether structure(s) in each of the four close Nether quadrants, and put the player in teleport-waiting mode. In this mode, if you click on one of the coordinates in chat and press Enter/Return, then you will be teleported near those coordinates (at most 64 blocks away). (Gilded Blackstone = bastion, Blaze Rod = fortress)|Incompatible with other teleport actions. To exit teleport-waiting mode, simply change gamemode.|
|Grass Block, Iron Sword, Map, Ender Eye|Set the player's gamemode to Creative, Survival, Adventure, or Spectator, respectively. (The triggers match the F3+F4 gamemode menu icons.)|Incompatible with each other.|
|Leather/Golden/Iron/Diamond Helmet|Set the player's difficulty to Peaceful, Easy, Normal, or Hard, respectively.|Incompatible with each other.|
|Heart of the Sea, Oak Boat, Prismarine|`/locate` the related Overworld structure and show the coordinates in chat. (Heart of the Sea = buried treasure, Oak Boat = shipwreck, Prismarine = monument)|Locating buried treasures in 1.19+ can be very slow.|
|Book and Quill|Give the player a potion, that when thrown, runs each of the book's pages as a command. If the book is named (via anvil), the name is copied to the potion so you can tell it apart from others.|Each page should contain a command exactly as it would be typed into chat: no extra space before or after, and no newlines. One potion is given per book.|
|Book and Quill, named "AUTO"|Run each of the book's pages as a command. The commands are run *after* any teleport/gamemode/difficulty actions.|Each page should contain a command exactly as it would be typed into chat: no extra space before or after, and no newlines.|
|Barrel|Treat the items in the barrel as trigger items. This allows you combine several trigger items into a single trigger item, like the presets in [`hotbar.nbt`](https://github.com/Knawk/mc-MiniPracticeKit/raw/master/hotbar.nbt).|To get a barrel with items into your inventory, hold CTRL and press pick-block on a barrel with the items you want. Recursion is not supported; barrels inside barrels will not be "unpacked".|
