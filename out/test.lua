
print("Start of REPL test\n")
--global_type_t = require("global_type_t")

print(type(global_type_t))
for k,v in pairs(global_type_t) do
  if type(v) == "function" then
    print(k, v)
  end
end

--local gt = global_type_t()
local gt = global_type_t:mutability()
local gt = global_type_t:new()
print("End of REPL test\n")

