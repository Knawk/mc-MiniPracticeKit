# MiniPracticeKit

MiniPracticeKit (MPK) is a versatile Minecraft speedrunning practice kit that fits in a single command block.
You can use it to:

- set your inventory/gamemode/difficulty
- teleport to the Nether/End
- teleport directly to the stronghold starter staircase
- teleport to good blind travel coordinates
- locate structures (bastion, fortress, buried treasure, shipwreck, monument)
- run your own commands on-demand (for example, to force the dragon to perch)

Demo: Eye spy / Stronghold enter ([view on YouTube](https://www.youtube.com/watch?v=zGqgCFJYtR0&list=PL3xWUYc3vlEl4QRGBrZFiGGBLKh6V3KhS))

[eyespy.webm](https://github.com/Knawk/mc-MiniPracticeKit/assets/1924194/c1247755-e4c0-4d28-be68-6a976fd10072)

Demo: Blind travel / Nether exit ([view on YouTube](https://www.youtube.com/watch?v=-hzr26j5DuQ&list=PL3xWUYc3vlEl4QRGBrZFiGGBLKh6V3KhS))

[blind.webm](https://github.com/Knawk/mc-MiniPracticeKit/assets/1924194/1e363083-3538-46d8-aeb3-b6889a2e0bb9)

([Full demo playlist](https://www.youtube.com/playlist?list=PL3xWUYc3vlEl4QRGBrZFiGGBLKh6V3KhS))

The MPK uses only vanilla Minecraft features: there's no need to install any mods or maintain a separate practice instance.
Save it to a creative hotbar in your main instances so you always have it on hand!
It also works in Minecraft versions 1.15 to 1.20 - you can even directly copy your `hotbar.nbt` file between compatible instances and it'll just work.

## Basic usage

Download [`hotbar.nbt`](https://github.com/Knawk/mc-MiniPracticeKit/raw/master/hotbar.nbt) and place it in your `.minecraft` folder (while the instance isn't running).
(Back up your existing `hotbar.nbt` file if you have one.)
This will give you a saved hotbar that includes the MPK, along with some presets for 1.16.1 Any% RSG:

- Nether enter (like logwet's Noverworld mod)
- Fortress enter (sets your inventory and shows nearby fortresses, you pick one to teleport to)
- Nether exit / blind travel (like logwet's Blinded mod)
- Stronghold enter / Eye Spy
- End enter

To use the presets:

1. Create a new world in creative mode.
2. Load the saved hotbar, which includes the MPK and the preset barrels.
3. Drop the desired preset barrel, and place the MPK.

See the "How to customize" section below to learn how to make your own preset barrels.

<details>

<summary>Alternative: get the MPK without overriding your saved hotbars</summary>

1. Open or create a Minecraft world in creative mode.
2. Give yourself a command block by running `/give @p command_block`, and place it.
3. Copy the contents of [`give-mpk.txt`](/give-mpk.txt) into the command block, and click "Done".
4. Activate the command block (for example, with a button) to get a MiniPracticeKit. You can save it to a creative hotbar for easy access.

</details>

## How to customize the MPK's behavior

When you place the MiniPracticeKit, it looks for nearby "trigger items" to determine what actions to perform.
The permitted trigger items and the corresponding actions are described below.

|Trigger|Action|Notes|
|-|-|-|
|Chest|Give the items in the chest to the player.|If multiple chests are found, items are given in the order that the chests were dropped.|
|Netherrack, End Stone|Teleport the player to the corresponding dimension. (Netherrack = Nether, End Stone = End)|Incompatible with other teleport actions (and each other).|
|Obsidian|Teleport the player to good first-ring blind coordinates (through the Nether into the overworld).|Incompatible with other teleport actions. Can be slow because it searches for open nether terrain.|
|End Portal Frame|Teleport the player to a stronghold's starter staircase.|Incompatible with other teleport actions. Always goes to the same stronghold in each world.|
|Grass Block, Iron Sword, Map, Ender Eye|Set the player's gamemode to Creative, Survival, Adventure, or Spectator, respectively. (The triggers match the F3+F4 gamemode menu icons.)|Incompatible with each other.|
|Leather/Golden/Iron/Diamond Helmet|Set the player's difficulty to Peaceful, Easy, Normal, or Hard, respectively.|Incompatible with each other.|
|Heart of the Sea, Oak Boat, Prismarine|`/locate` the related Overworld structure and show the results in chat. (Heart of the Sea = buried treasure, Oak Boat = shipwreck, Prismarine = monument)|Locating buried treasures in 1.19+ can be very slow.|
|Gilded Blackstone, Blaze Rod|`/locate` the related Nether structure in each of the four close Nether quadrants, and show the results in chat. (Gilded Blackstone = bastion, Blaze Rod = fortress)||
|Book and Quill|Give the player a potion, that when thrown, runs each of the book's pages as a command. If the book is named (via anvil), the name is copied to the potion so you can tell it apart from others.|Each page should contain a command exactly as it would be typed into chat: no extra space before or after, and no newlines. One potion is given per book.|
|Book and Quill, named "AUTO"|Run each of the book's pages as a command. The commands are run *after* any teleport/gamemode/difficulty actions.|Each page should contain a command exactly as it would be typed into chat: no extra space before or after, and no newlines.|
|Barrel|Treat the items in the barrel as trigger items. This allows you combine several trigger items into a single trigger item, like the presets in [`hotbar.nbt`](https://github.com/Knawk/mc-MiniPracticeKit/raw/master/hotbar.nbt).|Recursion is not supported; barrels inside barrels will not be "unpacked".|
