#!/usr/bin/bash
cd $(dirname $0)
if [[ -d ./out ]]; then :;else mkdir ./out;fi
./luatablegen.py --tbg ./test/wasmtablegen.json --out ./out --luaheader /home/bloodstalker/devi/hell2/bruiser/lua-5.3.4/src --pre ./test/wasmheader.txt --headeraggr ./out/wasm_tables.h --lualibpath ./out/wasm.lua --docpath ./out/wasm.md --xml ./test/luwasm.xml --tbldefs ./out/ --anon --name wasm
clang-format ./out/*.c ./out/*.h -i
for filename in ./out/*.c; do
  gcc -c $filename > /dev/null 2>&1
  if [[ $? != 0 ]]; then
    echo $filename did not compile.
  fi
done
rm *.o
