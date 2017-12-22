#!/usr/bin/env python



def bysize(words):
	ret = {}
	for w in words:
		if len(w) not in ret:
			ret[len(w)] = set()
		ret[len(w)].add(w)
	return ret


test = "kldjflkjdflk jdlkf lkj flksjd flkjs dlfkj sldfjldjfljasddfsjd fiojsadofjsoij fosijf oisjdofijosijfoisjdfi jsdijfsdjfoasdjf"
ok = test.split()
what = bysize(ok)
print(what)

