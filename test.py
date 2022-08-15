import os
import yaml
import json

def json2list(json_path):
    f = open(json_path)
    data = json.load(f)
    contact_list = []
    contacts = data['contacts']
    for c in contacts:
        contact_list.append(c.upper().replace(' ', '\u2581').replace('-', ' '))
    return contact_list



def contact2paths(contact_list, sp_path, win_size=999, word_level=False):
    import sentencepiece as spm

    sp = spm.SentencePieceProcessor()
    sp.Load(sp_path)

    path_list = []
    for l in contact_list:
        words = l.split('\u2581')
        contact_token = []
        for w in words:
            pieces = sp.EncodeAsPieces(w.upper())
            contact_token += pieces
            if word_level == True:
                if len(pieces) > win_size:
                    for i in range(len(pieces)-win_size):
                        path_list.append(pieces[i:i+win_size])
                else:
                    path_list.append(pieces)

        if word_level == False:
            if len(contact_token) > win_size:
                    for i in range(len(contact_token)-win_size):
                        path_list.append(contact_token[i:i+win_size])
            else:
                path_list.append(contact_token)

    return path_list


def encode_paths(path_list, units_path):

    f = open(units_path, 'r')
    units = f.readlines()
    f.close()
    token_list = []
    code_list = []
    for l in units:
        l = l.strip().split(' ')
        token_list.append(l[0])
        code_list.append(l[1])
    
    encoded_path_list = []

    for p in path_list:
        p_l = []
        for t in p:
            # Add 1, since wfst require eps to be 0
            p_l += [int(code_list[token_list.index(t)])+1]

        encoded_path_list.append(p_l)

    return encoded_path_list

def build_F_WFST(encoded_path_list, F_WFST_score, add_backarc = True):
    import openfst_python as fst

    f = fst.Fst()
    states = {}
    states[0] = f.add_state()
    
    f.set_start(states[0])
    state_idx = 1
    for p in encoded_path_list:
        
        states[state_idx] = f.add_state()
        f.add_arc(states[0], fst.Arc(p[0], p[0], fst.Weight(f.weight_type(),F_WFST_score), states[state_idx]))
        if add_backarc == True:
            f.add_arc(states[state_idx], fst.Arc(p[0], p[0], fst.Weight(f.weight_type(),F_WFST_score), states[0]))
        for i in range(len(p)):
            states[state_idx + 1] = f.add_state()
            f.add_arc(states[state_idx], fst.Arc(p[i], p[i], fst.Weight(f.weight_type(),F_WFST_score), states[state_idx+1]))
           
            if add_backarc == True:
                f.add_arc(states[state_idx+1], fst.Arc(0, 0, fst.Weight(f.weight_type(), F_WFST_score*(-1-i)), states[0]))
            state_idx += 1

        if add_backarc == False:
            f.set_final(states[state_idx])

    if add_backarc == True:
        f.set_final(states[0])

    f = fst.determinize(f)
 #   f.minimize()
   
    return f

def make_iosymbol_list(path_list, units_path, FST_name = 'F_WFST'):

    f = open(units_path, 'r')
    units = f.readlines()
    f.close()
    token_list = []
    code_list = []
    for l in units:
        l = l.strip().split(' ')
        token_list.append(l[0])
        code_list.append(l[1])
    
    all_p = []
    for p in path_list:
        all_p += p

    unique_symbols = []
    for x in all_p:
        if x not in unique_symbols:
            unique_symbols.append(x)

    with open(FST_name + '_isym.fst', 'w') as f:
        f.write('<eps> 0')
        f.write('\n')
        for sym in unique_symbols:
            idx = str(int(code_list[token_list.index(sym)]) + 1)
            f.write(sym)
            f.write(' ')
            f.write(idx + '\n')


    with open(FST_name + '_osym.fst', 'w') as f:
        f.write('<eps> 0')
        f.write('\n')
        for sym in unique_symbols:
            idx = str(int(code_list[token_list.index(sym)]) + 1)
            f.write(sym)
            f.write(' ')
            f.write(idx + '\n')
    return unique_symbols


if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--conf_dir', default = 'resources/wfst_conf.yaml')
    args = parser.parse_args()
    config_path = args.conf_dir
    config = yaml.load(open(config_path, 'r'), Loader = yaml.FullLoader)

    contact_json = config['contact_json']
    contact_list = json2list(contact_json)

    trie_base = config['F_WFST_setup']['trie_base']
    word_level = config['F_WFST_setup']['word_level']
    win_size = config['F_WFST_setup']['win_size']
    F_LM_name = config['LM_setup']['F_LM_name']
    F_LM_order = config['LM_setup']['F_LM_order']
    sp_path = config['LM_setup']['sp_path']
    units_path = config['LM_setup']['unit_path']

    path_list = contact2paths(contact_list, sp_path = sp_path, win_size = win_size, word_level = word_level)

    F_WFST_score = config['LM_setup']['F_WFST_score']
    F_WFST_backtrack = config['F_WFST_setup']['back_track']
    B_WFST_score = config['LM_setup']['B_WFST_score']
 
    encoded_path_list = encode_paths(path_list, units_path)
    F_WFST = build_F_WFST(encoded_path_list, F_WFST_score, add_backarc = F_WFST_backtrack)

    F_WFST.write('F_WFST')
    make_iosymbol_list(path_list, units_path)
    F_WFST.draw('F_WFST.gv') 
