# Your Addon
This is your addon. Add more files as you will, and be careful to update `.build.json` if needed.

- To build your addon: `cuhkit build`
- To sync your addon to Stormworks (building does this too): `cuhkit sync`
- To publish your addon to cuhHub: `cuhkit publish`
- To setup the addon if you cloned this addon and didn't create it yourself: `cuhkit setup`

Note that cuhkit will only find this project if executed from the same directory as the project `.json` file.

## ⚠️ Warning
Do not modify vehicles or `playlist.xml` in `src` - you WILL lose the changes when building this addon. Instead, modify them through Stormworks' in-game addon editor.

Every time you build this addon, cuhkit replaces all vehicles in `src` with the vehicles found in the Stormworks path for the addon rather than the other way around (with `cuhkit setup` being the exception and doing it the other way around). The same applies to `playlist.xml`.