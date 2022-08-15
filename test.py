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
    sp_path = config['token_setup']['sp_path']

    path_list = contact2paths(contact_list, sp_path = sp_path, win_size = win_size, word_level = word_level)

    print(path_list)
