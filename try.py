import sys, math, os
from os.path import isfile, join
from os import walk, listdir
import recommend

q = '出國留學'

ret = recommend.getarticle(q)

print(ret)