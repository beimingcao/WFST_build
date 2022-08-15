import openfst_python as fst

fst_path = 'B_WFST.model'

fst_model = fst.Fst.read(fst_path)



for arc in fst_model.arcs(0):
    print(arc.weight)
