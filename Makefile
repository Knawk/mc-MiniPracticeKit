SHELL := /bin/bash

copy:
	python mpk.py | tee >(clip.exe) >(wc) >/dev/null
