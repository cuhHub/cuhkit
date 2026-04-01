# cuhkit

## 📚 | Overview
cuhkit, a CLI to streamline the development of cuhHub addons and mods, featuring:
- Projects system
    - Create an addon or mod project in a directory
- Project publishing (publishing addon/mod to cuhHub servers)
- Addon building
    - Import .lua files from web
    - Import .lua files from local
    - Combine .lua files into one
        - Use `.order.json` to ignore certain files, set build order, handle imports, etc.
    - Sync to game
- Mod building
    - Package into `.zip` for publishing
    - Sync to game

... and more!

Although made for cuhHub developers, you can use this for your own addons and mods too!

## 🔗 Links
- GitHub: https://github.com/cuhHub/cuhkit
- PyPi: https://pypi.org/project/cuhkit

## ⚙️ | Installing
### PIP
- Use `pip install cuhkit --upgrade`.
- Run with `py -m cuhkit` or `cuhkit` if in PATH.

***Requires Python 3.13+ (untested on earlier versions).***

### GitHub Releases
- Go to latest release.
- Download the cuhkit executable.
- Place it wherever and add to PATH. Use any time with `cuhkit`.

## ❔ | Usage
- Run `cuhkit --help` to see all commands (or `py -m cuhkit --help` if using pip).
- Get started with a project with `cuhkit new PROJECT_NAME --type PROJECT_TYPE` (`PROJECT_TYPE` = `addon` or `mod`)
    - For addon projects: If you encounter an error due to missing `playlist.xml` file when building, create an addon in Stormworks via the addon editor with the same folder name as the project name. The folder name is the name you type into the input when saving your addon in-game.

## ✨ | Credit
- **Cuh4** ([GitHub](https://github.com/Cuh4))