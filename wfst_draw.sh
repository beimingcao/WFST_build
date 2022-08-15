#!/bin/bash

fstdraw --isymbols=F_WFST_isym.fst --osymbols=F_WFST_osym.fst B_WFST.model > B_WFST.dot
dot -Tpng B_WFST.dot > B_WFST.png


fstdraw B_WFST.model > B_WFST_num.dot
dot -Tpng B_WFST_num.dot > B_WFST_num.png
