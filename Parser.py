import nltk
import re

sentence_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

train_file = "training_data.data"


def parse_test_data(filename):
    word_map = {}
    with open(filename) as f:
        for line in f:
            parts = re.split('\|', line)
            word = re.split('.', parts[0])[0]
            pos = re.split('.', parts[0])[1]
            iden = parts[1]
            context = nltk.word_tokenize(parts[2])

            if word in word_map:
                pos_map = word_map[word]
                if pos in pos_map:
                    iden_map = pos_map[pos]
                    if iden in iden_map:
                        iden_map[iden].append(context)
                    else:
                        iden_map[iden] = [context]  
                else:
                    pos_map[pos] = {iden:[context]}
            else: 
                word_map[word] = {pos:{iden:[context]}} 
    return word_map     


print parse_test_data(train_file)         
