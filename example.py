import openfst_python as fst

f = fst.Fst()
s0 = f.add_state()
s1 = f.add_state()
s2 = f.add_state()

f.add_arc(s0, fst.Arc(1, 2, fst.Weight(f.weight_type(), 3.5), s1))
f.add_arc(s0, fst.Arc(1, 3, fst.Weight(f.weight_type(), 2.5), s2))

f.set_start(s0)
f.set_final(s2, fst.Weight(f.weight_type(), 1.5))
print(f)
