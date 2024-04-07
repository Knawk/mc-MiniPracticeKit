# Changelog

## v0.6

New features:

- The Nether Exit preset now includes a potion to re-blind on the surface (for cave/underground blinds)
- The Eye Spy preset now randomizes where in the initial 5-way it builds the double travel portal location
- The provided `hotbar.nbt` now includes an "Extras" chest with additional helpful AUTO and potion scripts, allowing you to:
  - equip an offhand item (cooked salmon by default)
  - give yourself an item with 50% chance (diamond sword by default)
  - give yourself piglin barters (18 barters by default), e.g. to practice clearing inventory before/during fortress split
- Potion scripts can now be given custom potion colors and lore to distinguish them more easily (see the Book triggers in the Nether Exit preset as examples)
  - The `CustomPotionColor` and `display.Lore` NBT tags of a Book trigger is merged into the potion's NBT tag, so to use these features you must use commands

Changes:

- When teleporting to a bastion or fortress, you'll now automatically face in the structure's general direction
- The post-bastion presets (Fortress Enter, Nether Exit, Eye Spy) now randomize the duration of fire resistance (2:00–3:00), which gold armor (helmet/chestplate/leggings), and which level of soul speed you get

Bug fixes:

- Returning to the Nether from a blind / first portal now works correctly when using the Ranked client (like in the Nether Exit preset, or any triggers that teleport you directly to the Nether), whereas your return portal would previously appear near (0, 0)
- Fixed the stronghold double travel portal sometimes failing to generate in 1.17+
- Fixed temporary chests not being removed when activating the MPK in newer versions

## v0.5

New features:

- Use white shulker box triggers to obtain items in a random order
  - These work just like chest triggers, except the items are shuffled
- The Eye Spy preset now creates a lit portal and places you next to it (as if double traveling into the stronghold), for more realistic pre-emptive practice

Changes:

- The post-bastion presets now randomize the order of the inner inventory items (excluding hotbar and top left flint-and-steel), using the new white shulker box trigger

## v0.4

New features:

- Use brown/red/orange/yellow shulker box triggers to obtain a random selection of items
  - Each of these 4 colors acts as a separate "pool" - for example, if there are multiple red shulker box triggers, you'll obtain the items from exactly one of them
- Select "blind modes" to choose whether to automatically build the portal and/or go through it to the Overworld

## v0.3

New features:

- Add triggers for teleporting to nearby Nether structures

## v0.2

Fixes:

- Fix no-trigger warning always appearing
- Avoid occasional fall damage when teleporting to stronghold in 1.17+

## v0.1

Initial release.
