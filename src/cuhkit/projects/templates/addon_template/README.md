# Your Addon
## Info
This is your addon. Add more files as you will, and be careful to update `.build.json` if needed.

- To build your addon: `cuhkit build`
- To sync your addon to Stormworks (building does this too): `cuhkit sync`
- To publish your addon to cuhHub: `cuhkit publish`
- To setup the addon if you cloned this addon and didn't create it yourself: `cuhkit setup`

Note that cuhkit will only find this project if executed from the same directory as the project `.json` file.

## `.build.json`
For `.build.json` schema, see the [cuhkit source code](https://github.com/cuhHub/cuhkit) and find `addon_builder.py`.

## Useful Addon Tools
- [Noir](https://github.com/cuhHub/Noir): An addon framework providing a clean OOP-based architecture for addons with class support. Comes with built-in libraries and services to speed up development. Simply download `Noir.lua` and make sure it is at the top of the final addon build (see `.build.json`).
- [SSSWTool](https://github.com/Avril112113/SSSWTool): A tool for building Stormworks addons like cuhkit, but also providing stacktraces, build actions and more. Both SSSWTool and cuhkit can be used together.

## Intellisense
Assuming you're using [Visual Studio Code](https://code.visualstudio.com/), install the [Lua extension](https://marketplace.visualstudio.com/items?itemName=sumneko.lua) and intellisense will be provided thanks to the `intellisense.lua` file.

Intellisense adds auto-completion, linting and more!

## ⚠️ Warning
Do not modify vehicles or `playlist.xml` in `src` - you WILL lose the changes when building this addon. Instead, modify them through Stormworks' in-game addon editor.

Every time you build this addon, cuhkit replaces all vehicles in `src` with the vehicles found in the Stormworks path for the addon rather than the other way around (with `cuhkit setup` being the exception and doing it the other way around). The same applies to `playlist.xml`.