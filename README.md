# luatablegen

`luatablegen` takes a list of C structures and generates lua tables in C.<br/>
The input is in the form of a JSON file that describes the C structure and the Lua types you want.<br/>
Each structure will have it's own pair of C source and header. There is an option for an aggregate header which will include all the headers and in has a function that registers all the tables with Lua.<br/>
`luatablegen` will generate a lua file that includes default constructors for all tables which you can use in Lua with `require`. luatablegen will also generate a markdown file listing the methods for the tables.<br/>
For an example you can look under the test directory.<br/>

## table gen file

Each entry in the JSON file should have the following fields:<br/>
* field_name: a list of the names of the C structure field names.<br/>
* field_type: a list of the names of the C types for the C structure fields.<br/>
* lua_type: a list of the names of the lua types that the Lua table fields corresponding to the C structure fields will have.<br/>
* methods: a list of the methods that will be generated for the Lua table corresponding to the C structure.<br/>

## Options

```bash
  -h, --help            show this help message and exit
  --out OUT             output directory
  --tbg TBG             the table gen file
  --pre PRE             path to source code file to add after header
                        guard/extern c
  --post POST           path to source code file to add before header
                        guard/extern c end
  --luaheader LUAHEADER
                        path to lua header files
  --dbg                 debug
  --singlefile          should all the generated code be added to a single
                        file
  --makemacro           generate a makefile containing all objects in a macro
                        to be included by another makefile
  --outfile OUTFILE     name of the output file if signlefile is set, ignored
                        otherwise
  --headeraggr HEADERAGGR
                        header aggregate file name
  --lualibpath LUALIBPATH
                        where the lua module file will be placed
  --docpath DOCPATH     where the doc file will be placed
```

## TODO
* fields should be able to reference each other.<br/>
* add more options for the table fileds.<br/>
