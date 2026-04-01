--[[
    Consider using libraries in your addon to easily organise your code.

    Libraries store common, reusable code that can be used across different
    parts of your addon.
]]

MyLib = {}

function MyLib.doSomething()
    server.announce("cuhkit", "Hello from my cuhkit addon!")
end