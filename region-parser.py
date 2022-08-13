#!python 3
import os, io, re
from pathlib import Path
file_to_parse = 'regions.txt'
path = Path(file_to_parse)
regions_list = []
f = io.open(path, mode="r", encoding="utf-8")

region_re = re.compile('(-?\d+)(" selected="selected)?">(.+)(<)')

with f as file:
    for line in file:
    #line = str(file_to_parse.readlines())
        print(line+'\n')
        mo = region_re.search(line)
        print(mo)
        regions_list.append(mo.group(1) +','+mo.group(3))

path = Path('parsed-'+file_to_parse)
parsed_file = open(path, 'w', encoding='utf-8')

for line in regions_list:
    parsed_file.write(line+'\n')