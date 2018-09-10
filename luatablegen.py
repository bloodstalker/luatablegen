#!/usr/bin/python3

import argparse
import code
import json
import os
import readline
import signal
import sys
import datetime
import xml.etree.ElementTree

C_STRUCT = ['typedef struct XXX {', '}XXX;']
HEADER_GUARD = ['\n#ifndef _XXX_H\n#define _XXX_H\n', '#endif //end of inclusion guard\n\n']
EXTERN_C = ['#ifdef __cplusplus\nextern "C" {\n#endif\n', '#ifdef __cplusplus\n}\n#endif //end of extern c\n']
BEGIN_NOTE = "//Generated Automatically by luatablegen."
HEADER_LIST = ['#include "HHHlua.h"\n', '#include "HHHlauxlib.h"\n',
               '#include "HHHlualib.h"\n', '#include <inttypes.h>\n',
               '#include <stdbool.h>\n']
CONVERT = ['static XXX* convert_XXX (lua_State* __ls, int index) {\n',
           '\tXXX* dummy = (XXX*)lua_touserdata(__ls, index);\n',
           '\tif (dummy == NULL) printf("XXX:bad user data type.\\n");\n',
           '\treturn dummy;\n}\n']
CHECK = ['static XXX* check_XXX(lua_State* __ls, int index) {\n',
        '\tXXX* dummy;\n',
        '\tluaL_checktype(__ls, index, LUA_TUSERDATA);\n'
        '\tdummy = (XXX*)luaL_checkudata(__ls, index, "XXX");\n',
        '\tif (dummy == NULL) printf("XXX:bad user data type.\\n");\n',
        '\treturn dummy;\n}\n']
PUSH_SELF = [ 'XXX* push_XXX(lua_State* __ls) {\n',
            '\tlua_checkstack(__ls, 1);\n',
            '\tXXX* dummy = lua_newuserdata(__ls, sizeof(XXX));\n',
            '\tluaL_getmetatable(__ls, "XXX");\n',
            '\tlua_setmetatable(__ls, -2);\n',
            '\treturn dummy;\n}\n']
PUSH_ARGS = ['int XXX_push_args(lua_State* __ls, XXX* _st) {\n',
             '\tlua_checkstack(__ls, NNN);\n', '\treturn 0;\n}\n']
NEW = ['int new_XXX(lua_State* __ls) {\n', '\tlua_checkstack(__ls, NNN);\n',
       '\tXXX* dummy = push_XXX(__ls);\n', '\treturn 1;\n}\n']
GETTER_GEN = ['static int getter_XXX_YYY(lua_State* __ls) {\n',
              '\tXXX* dummy = check_XXX(__ls, 1);\n',
              '\tlua_pop(__ls, -1);\n',
              '\treturn 1;\n}\n']
SETTER_GEN = ['static int setter_XXX_YYY(lua_State* __ls) {\n',
              '\tXXX* dummy = check_XXX(__ls, 1);\n',
              '\tlua_settop(__ls, 1);\n',
              '\treturn 1;\n}\n']
REGISTER_TABLE_METHODS = ['static const luaL_Reg XXX_methods[] = {\n',
                          '\t{0,0}\n};\n']
REGISTER_META = ['static const luaL_Reg XXX_meta[] = {\n',
                 '\t{0, 0}\n};\n']
# table register for global lua tables
TABLE_REGISTER_G =  ['int XXX_register(lua_State* __ls) {\n',
  'lua_checkstack(__ls, 4);\n'
  'lua_newtable(__ls);\n',
  'luaL_setfuncs(__ls, XXX_methods, 0);\n',
  'lua_setglobal(__ls, "XXX");\n',
  'luaL_newmetatable(__ls, "XXX");\n',
  'luaL_setfuncs(__ls, XXX_meta, 0);\n',
  'lua_pushliteral(__ls, "__index");\n',
  'lua_pushvalue(__ls, -3);\n',
  'lua_rawset(__ls, -3);\n',
  'lua_pushliteral(__ls, "__metatable");\n',
  'lua_pushvalue(__ls, -3);\n',
  'lua_rawset(__ls, -3);\n',
  'lua_setglobal(__ls , "XXX");\n'
  'return 0;\n}\n']
# table register function for anonymous lua tables
TABLE_REGISTER =  ['int XXX_register(lua_State* __ls) {\n',
  'lua_checkstack(__ls, 4);\n'
  'lua_newtable(__ls);\n',
  'luaL_setfuncs(__ls, XXX_methods, 0);\n',
  'luaL_newmetatable(__ls, "XXX");\n',
  'luaL_setfuncs(__ls, XXX_meta, 0);\n',
  'lua_pushliteral(__ls, "__index");\n',
  'lua_pushvalue(__ls, -3);\n',
  'lua_rawset(__ls, -3);\n',
  'lua_pushliteral(__ls, "__metatable");\n',
  'lua_pushvalue(__ls, -3);\n',
  'lua_rawset(__ls, -3);\n',
  'lua_setglobal(__ls , "XXX");\n'
  'return 0;\n}\n']
SOURCE_FILE_NAME='XXX_luatablegen.c'
HEADER_FILE_NAME='XXX_luatablegen.h'
LUA_PUSH_TABLE = """
int pushluatable_YYY(lua_State* ls, XXX array) {
  if (!lua_checkstack(ls, 3)) {
    printf("Not enough space on the lua stack.");
    return -1;
  }
  lua_newtable(ls);
  uint64_t i = 1U;
  while(1) {
    if (array[i] == NULL) break;
    lua_pushinteger(ls, i+1);
    WWW_push_args(ls, array[i]);
    new_WWW(ls);
    lua_settable(ls, -3);
    i++;
  }
  return 0;
}
"""
LUA_PUSH_TABLE_SIMPLE_TYPE = """
int pushluatable_YYY(lua_State* ls, XXX array) {
  if (!lua_checkstack(ls, 3)) {
    printf("Not enough space on the lua stack.");
    return -1;
  }
  lua_newtable(ls);
  uint64_t i = 1U;
  while(1) {
    if (array[i] == NULL) break;
    lua_pushinteger(ls, i+1);
    lua_pushZZZ(ls, array[i]);
    lua_settable(ls, -3);
    i++;
  }
  return 0;
}
"""

LUA_PUSH_TABLE_SIMPLE_TYPE_SIG = 'int pushluatable_YYY(lua_State* ls, XXX array);\n'
LUA_PUSH_TABLE_SIG = "int pushluatable_YYY(lua_State* ls, XXX array);\n"
LUA_PUSH_TABLE_CALL = "pushluatable_YYY(lua_State* ls, WWW, XXX array);\n"

LUA_LIB = ["local wasm = {}\n\n", "return wasm\n"]
LUA_SETMETA_NEW = ["setmetatable(XXX, {__call =\n", "\tfunction(selfAAA)\n",
                   "\t\tlocal t = self.new(AAA)\n", "\t\treturn t\n\tend\n\t}\n)\n"]
LUA_TO_GENERIC = "lua_to_YYY(__ls, ZZZ);\n"
LUA_TO_GENERIC_DEF = "YYY lua_to_YYY(lua_State* ls, XXX array, ZZZ) {}\n"

def lua_type_resolver(type_str):
    if type_str == "int8":
        return "integer"
    elif type_str == "uint8":
        return "integer"
    elif type_str == "int16":
        return "integer"
    elif type_str == "uint16":
        return "integer"
    elif type_str == "int32":
        return "integer"
    elif type_str == "uint32":
        return "integer"
    elif type_str == "int64":
        return "integer"
    elif type_str == "uint64":
        return "integer"
    elif type_str == "int128":
        return "integer"
    elif type_str == "uint128":
        return "integer"
    elif type_str == "float":
        return "number"
    elif type_str == "double":
        return "number"
    elif type_str == "bool":
        return "integer"
    elif type_str == "uchar":
        return "number"
    elif type_str == "schar":
        return "number"
    elif type_str == "string":
        return "string"
    else: return "lightuserdata"

def simple_type_resovler(type_str):
    if type_str == "int8":
        return "int8_t"
    elif type_str == "uint8":
        return "uint8_t"
    elif type_str == "int16":
        return "int16_t"
    elif type_str == "uint16":
        return "uint16_t"
    elif type_str == "int32":
        return "int32_t"
    elif type_str == "uint32":
        return "uint32_t"
    elif type_str == "int64":
        return "int64_t"
    elif type_str == "uint64":
        return "uint64_t"
    elif type_str == "int128":
        return "int128_t"
    elif type_str == "uint128":
        return "uint128_t"
    elif type_str == "float":
        return "float"
    elif type_str == "double":
        return "double"
    elif type_str == "bool":
        return "uint8_t"
    elif type_str == "uchar":
        return "uint8_t"
    elif type_str == "schar":
        return "int8_t"
    elif type_str == "string":
        return "char*"
    elif type_str == "FT::conditional":
        return "void*"
    else: return type_str

def type_resolver(elem, elem_list):
    if "isaggregate" in elem.attrib:
        type_str = elem.attrib["name"]
    else:
        type_str = elem.attrib["type"]
    type_name = elem.attrib["name"]
    if type_str == "int8":
        return "int8_t"
    elif type_str == "uint8":
        return "uint8_t"
    elif type_str == "int16":
        return "int16_t"
    elif type_str == "uint16":
        return "uint16_t"
    elif type_str == "int32":
        return "int32_t"
    elif type_str == "uint32":
        return "uint32_t"
    elif type_str == "int64":
        return "int64_t"
    elif type_str == "uint64":
        return "uint64_t"
    elif type_str == "int128":
        return "int128_t"
    elif type_str == "uint128":
        return "uint128_t"
    elif type_str == "float":
        return "float"
    elif type_str == "double":
        return "double"
    elif type_str == "bool":
        return "uint8_t"
    elif type_str == "uchar":
        return "uint8_t"
    elif type_str == "schar":
        return "int8_t"
    elif type_str == "string":
        return "char*"
    elif type_str == "FT::conditional":
        return "void*"
    elif type_str.find("self::") == 0:
        for node in elem_list:
            if elem.attrib["type"][6:] == node.tag:
                return node.attrib["name"]
    else: return type_str

def get_def_node(type_str, elem_list):
    for node in elem_list:
        if type_str == node.attrib["name"]:
            return node

def get_def_node_tag(type_str, elem_list):
    for node in elem_list:
        if type_str == node.tag:
            return node

def get_elem_count(elem):
    if "count" in elem.attrib:
        try:
            if str(int(elem.attrib["count"])) == elem.attrib["count"]:
                return int(elem.attrib["count"])
            else: return -1
        except ValueError:
            return -1
    else:
        return 1

def SigHandler_SIGINT(signum, frame):
    print()
    sys.exit(0)

def get_filename(filename):
    if filename[-1] == "/":
        c_source = filename + c_filename
    else:
        c_source = "/" + c_filename

class Argparser(object):
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--out", type=str, help="output directory")
        parser.add_argument("--tbg", type=str, help="the table gen file")
        parser.add_argument("--pre", type=str, help="path to source code file to add after header guard/extern c")
        parser.add_argument("--post", type=str, help="path to source code file to add before header guard/extern c end")
        parser.add_argument("--luaheader", type=str, help="path to lua header files")
        parser.add_argument("--dbg", action="store_true", help="debug", default=False)
        parser.add_argument("--singlefile", action="store_true", help="should all the generated code be added to a single file", default=False)
        parser.add_argument("--makemacro", action="store_true", help="generate a makefile containing all objects in a macro to be included by another makefile", default=False)
        parser.add_argument("--anon", action="store_true", help="generate anonymous lua tables if true, global if false", default=True)
        parser.add_argument("--outfile", type=str, help="name of the output file if signlefile is set, ignored otherwise")
        parser.add_argument("--headeraggr", type=str, help="header aggregate file name")
        parser.add_argument("--lualibpath", type=str, help="where the lua module file will be placed")
        parser.add_argument("--docpath", type=str, help="where the doc file will be placed")
        parser.add_argument("--xml", type=str, help="same as --tbg but use an xml file instead")
        parser.add_argument("--tbldefs", type=str, help="path to the definitions tablegen creates")
        self.args = parser.parse_args()

class TbgParser(object):
    def __init__(self, argparser):
        #self.tbg_file = json.load(open(argparser.args.tbg))
        self.argparser = argparser
        self.time = datetime.datetime.now().isoformat()
        print(self.time)
        self.def_elems = []
        self.read_elems = []

    def begin(self, c_source, struct_name, h_filename, is_source):
        c_source.write("\n")
        c_source.write("// automatically generated by luatablegen\n")
        c_source.write("// " + self.time + "\n")
        for header in HEADER_LIST:
            if self.argparser.args.luaheader:
                c_source.write(header.replace("HHH", self.argparser.args.luaheader+"/"))
            else:
                c_source.write(header.replace("HHH", ""))
        c_source.write('#include "./tabledefs.h"\n')
        if not is_source: c_source.write(HEADER_GUARD[0].replace("XXX", struct_name))
        if not is_source: c_source.write(EXTERN_C[0])
        if is_source: c_source.write("#include " + '"./' +h_filename+ '"\n')
        c_source.write("\n")
        if self.argparser.args.pre:
            pre_file = open(self.argparser.args.pre)
            for line in pre_file:
                c_source.write(line)
            pre_file.close()
        c_source.write("\n")

    def gen_lua_table_push_def(self, node, struct_name):
        type_name = type_resolver(child, self.def_elems+self.read_elems)
        type_ref_node = get_def_node(type_name, self.def_elems+self.read_elems)
        count = get_elem_count(node, self.def_elems+self.read_elems)
        if count == -1:
            count_node_name = node.attrib["count"][6:]
        if count == 1:
            pointer = ""
        else:
            pointer += "*"
        yyy = node.atttrib["name"]
        if type_ref_node:
            pointer += "*"
            xxx = type_ref_node.attrib["name"]
            zzz = "push_" + type_ref_node.attrib["name"]
            return LUA_PUSH_TABLE.replace("XXX", xxx+pointer).replace("YYY", yyy).replace("ZZZ", zzz)
        else:
            xxx = node.attrib["name"]
            zzz = "lua_push" + node.attrib["luatype"]
            return LUA_PUSH_TABLE_SIMPLE_TYPE.replace("XXX", xxx+pointer).replace("YYY", yyy).replace("ZZZ", zzz)

    def gen_lua_table_push_call(self, node, arg_pos):
        type_name = type_resolver(node, self.def_elems+self.read_elems)
        type_ref_node = get_def_node(type_name, self.def_elems+self.read_elems)
        count = get_elem_count(node)
        pointer = ""
        if count == 1:
            pointer = ""
        else:
            pointer += "*"
        yyy = node.attrib["name"]
        if type_ref_node:
            pointer += "*"
            xxx = type_ref_node.attrib["name"]
            zzz = "push_" + type_ref_node.attrib["name"]
        else:
            xxx = node.attrib["name"]
            zzz = "lua_push" + node.attrib["luatype"]
        return [type_resolver(node, self.elems) + pointer + node.attrib["name"], LUA_PUSH_TABLE_CALL.replace("XXX", xxx+pointer).replace("YYY", yyy).replace("WWW", repr(arg_pos))]

    def gen_luato_generic(self, struct_name, field_name, arg_pos):
        parent = get_def_node(struct_name, self.elems)
        child = get_def_node(field_name, self.elems)
        return "check_" + struct_name + "(__ls," + repr(arg_pos) + ");\n"

    def struct(self, c_source, field_names, field_types, struct_name):
        c_source.write("typedef struct {\n")
        for field_type, field_name in zip(field_types, field_names):
            c_source.write("\t" + field_type + " " + field_name + ";\n")
        c_source.write("}" +struct_name+ ";\n")
        c_source.write("\n")

    def convert(self, c_source, struct_name):
        for line in CONVERT:
            c_source.write(line.replace("XXX", struct_name))
        c_source.write("\n")

    def check(self, c_source, struct_name):
        for line in CHECK:
            c_source.write(line.replace("XXX", struct_name))
        c_source.write("\n")

    def push_self(self, c_source, struct_name):
        for line in PUSH_SELF:
            c_source.write(line.replace("XXX", struct_name))
        c_source.write("\n")

    def read_xml(self):
        tree = xml.etree.ElementTree.parse(self.argparser.args.xml)
        root = tree.getroot()
        read_tree = xml.etree.ElementTree.Element("read")
        def_tree = xml.etree.ElementTree.Element("def")
        for child in root:
            if child.tag == "Read":
                read_tree = child
            if child.tag == "Definition":
                def_tree = child
        for child in read_tree:
            self.read_elems.append(child)
        for child in def_tree:
            self.def_elems.append(child)
        read_iter = read_tree.iter(tag=None)
        def_iter = def_tree.iter(tag=None)
        self.read_iter = read_iter
        self.def_iter = def_iter
        self.struct_names = []
        self.lua_types = []
        lua_type = []
        self.field_names = []
        field_name = []
        self.field_types = []
        field_type = []
        for node in self.read_elems+self.def_elems:
            self.struct_names.append(node.attrib["name"])
            for child in node:
                field_name.append(child.attrib["name"])
                field_type.append(child.attrib["type"])
                lua_type.append(child.attrib["luatype"])
            self.field_types.append(field_type)
            field_type = []
            self.field_names.append(field_name)
            field_name = []
            self.lua_types.append(lua_type)
            lua_type = []
        self.elems = self.def_elems + self.read_elems

    def push_args(self, c_source, struct_name, field_names, lua_types):
        dummy = str()
        c_source.write(PUSH_ARGS[0].replace("XXX", struct_name))
        c_source.write("\tlua_checkstack(__ls, " + repr(len(field_names)) + ");\n")
        for field_name, lua_type in zip(field_names, lua_types):
            if lua_type == "integer": dummy = "\tlua_pushinteger(__ls, _st->"+field_name+");\n"
            elif lua_type == "lightuserdata": dummy = "\tlua_pushlightuserdata(__ls, _st->"+field_name+");\n"
            elif lua_type == "number": dummy = "\tlua_pushnumber(__ls, _st->"+field_name+");\n"
            elif lua_type == "string": dummy = "\tlua_pushstring(__ls, _st->"+field_name+");\n"
            elif lua_type == "boolean": dummy = "\tlua_pushboolean(__ls, _st->"+field_name+");\n"
            elif lua_type == "table":
                parent = get_def_node(struct_name, self.elems)
                child = get_def_node(field_name, self.elems)
                if not child:
                    for kid in parent:
                        if kid.attrib["name"] == field_name: child = kid
                dummy = "\tpushluatable_" + type_resolver(child, self.elems) +"(__ls, _st->"+field_name+");\n"
            elif lua_type == "conditional":
                parent = get_def_node(struct_name, self.elems)
                child = get_def_node(field_name, self.elems)
                if not child:
                    for kid in parent:
                        if kid.attrib["name"] == field_name: child = kid
                cond_node = get_def_node_tag(child.attrib["condition"][6:], [child for child in parent])
                for childer in child:
                    c_source.write("if (_st->" + cond_node.attrib["name"] + "==" + childer.text + ")\n")
                    if childer.attrib["luatype"] == "integer": c_source.write("lua_pushinteger(__ls, _st->" + child.attrib["name"] + ");\n")
                    elif childer.attrib["luatype"] == "number":c_source.write("lua_pushnumber(__ls, _st->" + child.attrib["name"] + ");\n")
                    elif childer.attrib["luatype"] == "string":c_source.write("lua_pushstring(__ls, _st->" + child.attrib["name"] + ");\n")
                    elif childer.attrib["luatype"] == "table":
                        count = get_elem_count(childer)
                        if count == 1:
                            ref_type_node = get_def_node_tag(childer.attrib["type"][6:], self.elems)
                            c_source.write("push_" + ref_type_node.attrib["name"] + "(__ls, _st->" + child.attrib["name"] + ");\n")
                    else: pass
            else:
                print("bad lua_type entry in the json file")
                sys.exit(1)
            c_source.write(dummy)
            dummy = str()
        c_source.write(PUSH_ARGS[2])
        c_source.write("\n")

    def new(self, c_source, struct_name, field_types, field_names, lua_types):
        dummy = str()
        rev_counter = -len(field_types)
        c_source.write(NEW[0].replace("XXX", struct_name))
        c_source.write("\tlua_checkstack(__ls, " + repr(len(field_names)) + ");\n")
        for lua_type, field_name, field_type in zip(lua_types, field_names, field_types):
            parent = get_def_node(struct_name, self.elems)
            child = get_def_node(field_name, self.elems)
            for kid in parent:
                if kid.attrib["name"] == field_name: child = kid
            if lua_type == "integer": dummy = "\t"+simple_type_resovler(field_type) +" "+field_name+" = "+"luaL_optinteger(__ls,"+repr(rev_counter)+",0);\n"
            elif lua_type == "lightuserdata": dummy = "\t"+field_type +" "+field_name+" = "+"lua_touserdata(__ls,"+repr(rev_counter)+");\n"
            elif lua_type == "number": pass
            elif lua_type == "string":dummy = "\t"+simple_type_resovler(field_type) +" "+field_name+" = "+"lua_tostring(__ls,"+repr(rev_counter)+");\n"
            elif lua_type == "boolean": pass
            elif lua_type == "table":
                temp = self.gen_lua_table_push_call(child, rev_counter)
                temp2 = self.gen_luato_generic(struct_name, field_name, rev_counter)
                dummy = temp[0] + "=" + temp2
            elif lua_type == "conditional":
                dummy = "void* " + child.attrib["name"] + "=" + self.gen_luato_generic(struct_name, field_name, rev_counter)
            else:
                print("bad lua_type entry in the json file")
                sys.exit(1)
            rev_counter += 1
            c_source.write(dummy)
            dummy = str()
        c_source.write(NEW[2].replace("XXX", struct_name))
        for field_name in field_names:
            c_source.write("\tdummy->" + field_name + " = " + field_name + ";\n")
        c_source.write(NEW[3].replace("XXX", struct_name))
        c_source.write("\n")

    def getter(self, c_source, struct_name, field_names, field_types, lua_types):
        dummy = str()
        for field_name, lua_type in zip(field_names, lua_types):
            c_source.write(GETTER_GEN[0].replace("XXX", struct_name).replace("YYY", field_name))
            c_source.write(GETTER_GEN[1].replace("XXX", struct_name))
            c_source.write(GETTER_GEN[2])
            if lua_type == "integer": dummy = "\tlua_pushinteger(__ls, dummy->"+field_name+");\n"
            elif lua_type == "lightuserdata": dummy = "\tlua_pushlightuserdata(__ls, dummy->"+field_name+");\n"
            elif lua_type == "number": dummy = "\tlua_pushnumber(__ls, dummy->"+field_name+");\n"
            elif lua_type == "string": dummy = "\tlua_pushstring(__ls, dummy->"+field_name+");\n"
            elif lua_type == "boolean": dummy = "\tlua_pushboolean(__ls, dummy->"+field_name+");\n"
            elif lua_type == "table":
                parent = get_def_node(struct_name, self.elems)
                child = get_def_node(field_name, self.elems)
                if not child:
                    for kid in parent:
                        if kid.attrib["name"] == field_name: child = kid
                dummy = "\tpushluatable_" + type_resolver(child, self.elems) +"(__ls, dummy->"+field_name+");\n"
            elif lua_type == "conditional":
                pass
            else:
                print("bad lua_type entry in the json file")
                sys.exit(1)
            c_source.write(dummy)
            dummy = str()
            c_source.write(GETTER_GEN[3])
        c_source.write("\n")

    def setter(self, c_source, struct_name, field_names, field_types, lua_types):
        dummy = str()
        for field_name, lua_type in zip(field_names, lua_types):
            c_source.write(SETTER_GEN[0].replace("XXX", struct_name).replace("YYY", field_name))
            c_source.write(SETTER_GEN[1].replace("XXX", struct_name))
            if lua_type == "integer": dummy = "\tdummy->" + field_name + " = " + "luaL_checkinteger(__ls, 2);\n"
            elif lua_type == "lightuserdata": dummy ="\tdummy->" + field_name + " = " + "luaL_checkudata(__ls, 2, "+'"'+field_name+"_t"+'"'+");\n"
            elif lua_type == "number": dummy ="\tdummy->" + field_name + " = " + "luaL_checknumber(__ls, 2);\n"
            elif lua_type == "string": dummy ="\tdummy->" + field_name + " = " + "luaL_checkstring(__ls, 2);\n"
            elif lua_type == "boolean": pass
            elif lua_type == "table": dummy = "\t;\n"
            elif lua_type == "conditional":
                pass
            else:
                print("bad lua_type entry in the json file")
                sys.exit(1)
            c_source.write(dummy)
            dummy = str()
            c_source.write(SETTER_GEN[2])
            c_source.write(SETTER_GEN[3])
        c_source.write("\n")

    def gc(self):
        pass
    def tostring(self):
        pass

    def register_table_methods(self, c_source, struct_name, field_names):
        c_source.write(REGISTER_TABLE_METHODS[0].replace("XXX", struct_name))
        c_source.write('\t{"new", ' + "new_" + struct_name + "},\n")
        for field_name in field_names:
            c_source.write("\t{" + '"set_' + field_name + '"' + ", " + "setter_"+struct_name +"_"+ field_name + "},\n")
        for field_name in field_names:
            c_source.write("\t{" + '"' + field_name + '", ' + "getter_"+struct_name+"_"+field_name+"},\n")
        c_source.write(REGISTER_TABLE_METHODS[1])
        c_source.write("\n")

    def register_table_meta(self, c_source, struct_name):
        c_source.write(REGISTER_META[0].replace("XXX", struct_name))
        c_source.write(REGISTER_META[1])
        c_source.write("\n")

    def register_table(self, c_source, struct_name):
        # if anon tables were selected
        if self.argparser.args.anon:
            for line in TABLE_REGISTER:
                c_source.write(line.replace("XXX", struct_name))
        # if global tables were selected
        else:
            for line in TABLE_REGISTER_G:
                c_source.write(line.replace("XXX", struct_name))

    def end(self, c_source, is_source):
        if self.argparser.args.post:
            c_source.write("\n")
            post_file = open(self.argparser.args.post)
            for line in post_file:
                c_source.write(line)
            post_file.clsoe()
        c_source.write("\n")
        if not is_source: c_source.write(EXTERN_C[1])
        if not is_source: c_source.write(HEADER_GUARD[1])
        c_source.write("\n")

    def docgen_md(self, d_source, struct_name, field_names, field_types, lua_types):
        d_source.write("## " + "__"  + struct_name + "__"  + ":\n")
        d_source.write("\n")
        d_source.write("### " + "_" + "getter fields" + "_" + ":\n")
        for field_name,lua_type in zip(field_names, lua_types):
            d_source.write(struct_name + ":" + field_name + "()" + " -- ")
            if lua_type == "lightuserdata":
                d_source.write("return type: " + field_name + "_t" + "<br/>" + "\n")
            else:
                d_source.write("return type: " + lua_type + "<br/>" + "\n")
        d_source.write("\n")
        d_source.write("### " + "_" + "setter fields" + "_" + ":\n")
        for field_name,lua_type in zip(field_names, lua_types):
            d_source.write("set_" + struct_name + ":" + field_name + "()" + " -- ")
            if lua_type == "lightuserdata":
                d_source.write("arg type: " + field_name + "_t" + "<br/>" + "\n")
            else:
                d_source.write("arg type: " + lua_type + "<br/>" + "\n")
        d_source.write("\n")
        d_source.write("### " + "_" + "constructors" + "_" + ":\n")
        d_source.write(struct_name + ":new() -- needs all the args<br/>\n")
        d_source.write(struct_name + "() -- lazy constructor<br/>\n")
        d_source.write("\n")
        d_source.write("\n")

    def luagen(self):
        l_source = open(self.argparser.args.lualibpath, "w")
        l_source.write("-- automatically generated by luatablegen\n")
        l_source.write("-- " + self.time + "\n")
        l_source.write(LUA_LIB[0])
        for k, v in self.tbg_file.items():
            struct_name = k
            field_names = v['field_name']
            field_types = v['field_type']
            lua_types = v['lua_type']
            l_source.write(LUA_SETMETA_NEW[0].replace("XXX", struct_name))
            arg_list_str = str()
            for i in range(0, len(field_names)):
                arg_list_str += ", arg" + repr(i)
            l_source.write(LUA_SETMETA_NEW[1].replace("AAA", arg_list_str))
            l_source.write(LUA_SETMETA_NEW[2].replace("AAA", arg_list_str[2:]))
            l_source.write(LUA_SETMETA_NEW[3])
            arg_list_str = str()
            l_source.write("\n")

        l_source.write(LUA_LIB[1])

    def gen_table_def(self):
        tbl_source = open(self.argparser.args.tbldefs + "/tabledefs.c", "w")
        tbl_header = open(self.argparser.args.tbldefs + "/tabledefs.h", "w")
        tbl_source.write("// automatically generated by luatablegen\n")
        tbl_header.write("// automatically generated by luatablegen\n")
        tbl_source.write("//" + self.time + "\n")
        tbl_header.write("//" + self.time + "\n")
        for header in HEADER_LIST[0:4]:
            if self.argparser.args.luaheader:
                tbl_source.write(header.replace("HHH", self.argparser.args.luaheader+"/"))
                tbl_header.write(header.replace("HHH", self.argparser.args.luaheader+"/"))
            else:
                tbl_source.write(header.replace("HHH", ""))
                tbl_header.write(header.replace("HHH", ""))
        tbl_source.write('#include "../wasm.h"\n')
        tbl_header.write('#include "../wasm.h"\n')
        tbl_tag_list = []
        simple_table_list = []
        for elem in self.elems:
            for node in elem:
                count_replacement = ""
                type_name = type_resolver(node, self.def_elems+self.read_elems)
                type_ref_node = get_def_node(type_name, self.def_elems+self.read_elems)
                # if node has attribute aggregate
                if type_ref_node and type_ref_node.tag not in tbl_tag_list:
                    tbl_tag_list.append(type_ref_node.tag)
                    count = get_elem_count(node)
                    pointer = ""
                    if count == -1:
                        for node2 in elem:
                            if node2.tag == node.attrib["count"][6:]:
                                count_replacement = node2.attrib["name"]
                    if count == 1:
                        pointer = "*"
                    else:
                        pointer += "*"
                    yyy = node.attrib["name"]
                    if type_ref_node:
                        pointer += "*"
                        xxx = type_ref_node.attrib["name"]
                        zzz = "push_" + type_ref_node.attrib["name"]
                    else:
                        xxx = node.attrib["name"]
                        zzz = "lua_push" + node.attrib["luatype"]
                    #if pointer == "*": continue
                    tbl_source.write(LUA_PUSH_TABLE.replace("XXX", xxx+pointer).replace("YYY", xxx).replace("WWW", xxx))
                    tbl_header.write(LUA_PUSH_TABLE_SIG.replace("XXX", xxx+pointer).replace("YYY", xxx))
                # if node is simple type
                else:
                    count = get_elem_count(node)
                    simple_type = simple_type_resovler(node.attrib["type"])
                    if count != 1 and simple_type not in simple_table_list:
                        simple_table_list.append(simple_type)
                        yyy = node.attrib["name"]
                        xxx = simple_type_resovler(node.attrib["type"])
                        # lightuserdata types are being handled elsewhere
                        if simple_type == "lightuserdata": continue
                        lua_type = lua_type_resolver(node.attrib["type"])
                        tbl_source.write(LUA_PUSH_TABLE_SIMPLE_TYPE.replace("YYY", xxx).replace("XXX", simple_type+"*").replace("ZZZ", lua_type))
                        tbl_header.write(LUA_PUSH_TABLE_SIMPLE_TYPE_SIG.replace("YYY", xxx).replace("XXX", simple_type+"*"))

    def run(self):
        header_aggr_list = []
        table_reg_list = []
        self.read_xml()
        self.gen_table_def()

        if self.argparser.args.singlefile:
            c_source = open(self.argparser.args.outfile, "w")
        if self.argparser.args.docpath:
            d_source = open(self.argparser.args.docpath, "w")
            d_source.write("The lazy constructors are inside wasm.lua.\n")
            d_source.write("```lua\nlocal wasm = require(\"wasm\")\n```\n")
        #for k, v in self.tbg_file.items():
        for struct_name, field_names, field_types, lua_types in zip(self.struct_names, self.field_names, self.field_types, self.lua_types):
            if not self.argparser.args.singlefile:
                c_filename = struct_name + "_tablegen.c"
                h_filename = struct_name + "_tablegen.h"
                if self.argparser.args.out[-1] == "/":
                    c_source = open(self.argparser.args.out + c_filename, "w")
                    header_aggr_list.append("./" + h_filename)
                    h_source = open(self.argparser.args.out + h_filename, "w")
                else:
                    c_source = open(self.argparser.args.out + "/" + c_filename, "w")
                    header_aggr_list.append("./" + h_filename)
                    h_source = open(self.argparser.args.out + "/" + h_filename, "w")
            # source file
            self.begin(c_source, struct_name, h_filename, True)
            self.convert(c_source, struct_name)
            self.check(c_source, struct_name)
            self.push_self(c_source, struct_name)
            self.push_args(c_source, struct_name, field_names, lua_types)
            self.new(c_source, struct_name, field_types, field_names, lua_types)
            self.getter(c_source, struct_name, field_names, field_types, lua_types)
            self.setter(c_source, struct_name, field_names, field_types, lua_types)
            self.register_table_methods(c_source, struct_name, field_names)
            self.register_table_meta(c_source, struct_name)
            self.register_table(c_source, struct_name)
            self.end(c_source, True)
            if not self.argparser.args.singlefile: c_source.close()
            # header file
            self.begin(h_source, struct_name, h_filename, False)
            h_source.write(CONVERT[0].replace("XXX", struct_name).replace(" {\n", ";\n"))
            h_source.write(CHECK[0].replace("XXX", struct_name).replace(" {\n", ";\n"))
            h_source.write(PUSH_SELF[0].replace("XXX", struct_name).replace(" {\n", ";\n"))
            h_source.write(PUSH_ARGS[0].replace("XXX", struct_name).replace(" {\n", ";\n"))
            h_source.write(NEW[0].replace("XXX", struct_name).replace(" {\n", ";\n"))
            for field_name, lua_type in zip(field_names, lua_types):
                h_source.write(GETTER_GEN[0].replace("XXX", struct_name).replace("YYY", field_name).replace(" {\n", ";\n"))
            for field_name, lua_type in zip(field_names, lua_types):
                h_source.write(SETTER_GEN[0].replace("XXX", struct_name).replace("YYY", field_name).replace(" {\n", ";\n"))
            table_reg_list.append(struct_name + "_register(__ls);\n")
            h_source.write(TABLE_REGISTER[0].replace("XXX", struct_name).replace(" {\n", ";\n"))
            self.end(h_source, False)
            # docs
            if self.argparser.args.docpath:
                self.docgen_md(d_source, struct_name, field_names, field_types, lua_types)
        # header aggregate
        if self.argparser.args.headeraggr:
            name = self.argparser.args.headeraggr
            dummy = name[name.rfind("/"):]
            aggr_header = open(self.argparser.args.headeraggr.replace(".h", ".c"), "w")
            aggr_header_h = open(self.argparser.args.headeraggr, "w")
            aggr_header.write("// automatically generated by luatablegen\n")
            aggr_header_h.write("// automatically generated by luatablegen\n")
            aggr_header.write("// " + self.time + "\n")
            aggr_header_h.write("// " + self.time + "\n")
            aggr_header_h.write(HEADER_GUARD[0].replace("XXX", "WASM_TABLES_AGGR"))
            aggr_header_h.write(EXTERN_C[0])
            aggr_header.write("\n")
            for item in header_aggr_list:
                aggr_header.write("#include " + '"' + item + '"\n')
                aggr_header_h.write("#include " + '"' + item + '"\n')
            aggr_header.write("#include " + '".' + dummy + '"\n')
            aggr_header.write("\n")
            aggr_header.write("void reg_tablegen_tables(lua_State* __ls) {\n")
            aggr_header_h.write("void reg_tablegen_tables(lua_State* __ls);\n")
            for func_sig in table_reg_list:
                aggr_header.write("\t" + func_sig)
                if self.argparser.args.anon:
                    pass
                else:
                    aggr_header.write("\t" + "lua_pop(__ls, 1);\n")
            aggr_header.write("}\n")
            aggr_header_h.write(EXTERN_C[1])
            aggr_header_h.write(HEADER_GUARD[1])
            aggr_header.write("\n")
        if self.argparser.args.makemacro:
            if self.argparser.args.out[-1] == "/":
                m_source = open(self.argparser.args.out + "tablegen.mk", "w")
            else:
                m_source = open(self.argparser.args.out + "/" + "tablegen.mk", "w")
        # generate lua module
        #self.luagen()
        if self.argparser.args.docpath:
            d_source.write("_automatically generated by luatablegen._<br/>\n")
            d_source.write("_" + self.time + "_")

# write code here
def premain(argparser):
    signal.signal(signal.SIGINT, SigHandler_SIGINT)
    #here
    parser = TbgParser(argparser)
    parser.run()

def main():
    argparser = Argparser()
    if argparser.args.dbg:
        try:
            premain(argparser)
        except Exception as e:
            print(e.__doc__)
            if e.message: print(e.message)
            variables = globals().copy()
            variables.update(locals())
            shell = code.InteractiveConsole(variables)
            shell.interact(banner="DEBUG REPL")
    else:
        premain(argparser)

if __name__ == "__main__":
    main()
