#include "../lua5/lauxlib.h"
#include "../lua5/lua.h"
#include "../lua5/lualib.h"
#include "./wasm_tables.h"
#include <inttypes.h>
#include <stdio.h>

#pragma weak main
int main(int argc, char **argv) {
  lua_State *ls = luaL_newstate();
  luaL_openlibs(ls);
  reg_tablegen_tables(ls);
}
