# MiniPracticeKit

MiniPracticeKit (MPK) is a versatile Minecraft speedrunning practice kit that fits in a single command block.
You can use it to:

- set your inventory/gamemode/difficulty
- teleport to the Nether/End
- teleport directly to the stronghold starter staircase
- teleport to good blind travel coordinates
- locate structures (bastion, fortress, buried treasure, shipwreck, monument)
- run your own commands on-demand (for example, to force the dragon to perch)

Demo: Eye spy / Stronghold enter

[eyespy.webm](https://github.com/Knawk/mc-MiniPracticeKit/assets/1924194/c1247755-e4c0-4d28-be68-6a976fd10072)

Demo: Blind travel / Nether exit
  
[blind.webm](https://github.com/Knawk/mc-MiniPracticeKit/assets/1924194/1e363083-3538-46d8-aeb3-b6889a2e0bb9)

The MPK uses only vanilla Minecraft features: there's no need to install any mods or maintain a separate practice instance.
Save it to a creative hotbar in your main instances so you always have it on hand!
It also works in Minecraft versions 1.15 to 1.20 - you can even directly copy your `hotbar.nbt` file between compatible instances and it'll just work.

## Basic usage

Download `hotbar.nbt` and place it in your `.minecraft` folder (while the instance isn't running).
(Back up the existing `hotbar.nbt` file if you have one.)
This will give you a saved hotbar that includes the MPK, along with some presets for 1.16.1 Any% RSG:

- Nether enter (like logwet's Noverworld mod)
- Fortress enter (sets your inventory and shows nearby fortresses, you pick one to teleport to)
- Nether exit / blind travel (like logwet's Blinded mod)
- Stronghold enter / Eye Spy
- End enter

To use the presets:

1. Create a new world in creative mode.
2. Load the saved hotbar, which includes the MPK and the presets.
3. Drop the desired preset, and place the MPK.

See the "How to customize" section below to learn how to make your own presets.

<details>

<summary>Alternative: get the MPK without overriding your saved hotbars</summary>

1. Open or create a Minecraft world in creative mode.
2. Give yourself a command block by running `/give @p command_block`, and place it.
3. Copy the following command into the command block, and click "Done".
4. Activate the command block (for example, with a button) to get a MiniPracticeKit. You can save it to a creative hotbar for easy access.

</details>

## How to customize the MPK's behavior

When you place the MiniPracticeKit, it looks for nearby "trigger items" to determine what actions to perform.
The permitted trigger items and the corresponding actions are described below.

TODO
