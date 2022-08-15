#!/bin/bash

fstdraw --isymbols=F_WFST_isym.fst --osymbols=F_WFST_osym.fst F_WFST > F_WFST.dot
dot -Tpng F_WFST.dot > F_WFST.png
