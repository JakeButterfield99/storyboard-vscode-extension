# Crank Storyboard VS Code Extension

### Usage

Extension will automatically load in open Lua files.

### Update Lua Doc references

**requires Python 3.10+*

Find the path to your `.doclua` files.

MacOS:
```
/Applications/Crank_Software/Storyboard_Designer/Storyboard.app/Contents/Eclipse/plugins/com.crank.gdt.lua_7.2.0.202207270823/resources/lua/api/gre.doclua
```

Run the `src/tool/doclua.py` script with the path to the .doclua file you want to generate snippets from. E.g:
```
python3 doclua.py /Applications/Crank_Software/Storyboard_Designer/Storyboard.app/Contents/Eclipse/plugins/com.crank.gdt.lua_7.2.0.202207270823/resources/lua/api/gre.doclua
```

Copy the generated `snippets.json` file to `src/snippets/` and rename (currently accepted names are `gre.json` and `gredom.json`, can be adjusted in `package.json`)