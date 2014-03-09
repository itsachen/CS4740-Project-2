import nltk
import re

sentence_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

train_file = "training_data.data"

class Word:
    def __init__(self,word, pos):
        self.word = word
        self.pos = pos
        self.sense_id_map = {}
    
    def add_context(self, sense, context): 
        if sense in self.sense_id_map:
            self.sense_id_map[sense].append(Context(context))
        else:
            self.sense_id_map[sense] = [Context(context)]

    def toString(self):
        s = self.word + " : " + self.pos + "\n"
        for counter, context_list in self.sense_id_map.items():
            for context in context_list:
                s += str(counter) + " " + context.toString() + "\n"
        return s        

class Context:
    def __init__(self, context):
        context_split = re.split('%%', context)
        self.prev_sentences = []
        self.after_sentences = []

        prev_sentences1 = sentence_tokenizer.tokenize(context_split[0])
        after_sentences1 = sentence_tokenizer.tokenize(context_split[2])

        self.prev_context = nltk.word_tokenize(prev_sentences1.pop())
        self.after_context = nltk.word_tokenize(after_sentences1.pop(0))

        for sentence in prev_sentences1:
            for wd in nltk.word_tokenize(sentence):
                self.prev_sentences.append(wd)
        for sentence in after_sentences1:
            for wd in nltk.word_tokenize(sentence):
                self.after_sentences.append(wd)

    def toString(self):
        s = ""
        for token in self.prev_sentences:
            s += " " + token
        s += " ##" 
        for token in self.prev_context:
            s += " " + token
        s += " ####" 
        for token in self.after_context:
            s += " " + token
        s += " ##" 
        for token in self.after_sentences:
            s += " " + token
        return s


def parse_test_data(filename):
    word_map = {}
    with open(filename) as f:
        linecounter = 0
        for line in f:
            if linecounter < 50:
                parts = re.split(' \| ', line)
                word = re.split('\.', parts[0])[0]
                pos = re.split('\.', parts[0])[1]
                sense = parts[1]
                context = parts[2]

                #print word + " # " + pos + " # " + sense + " # " + context

                if not word in word_map:
                    word_map[word] = Word(word, pos)
                word_map[word].add_context(sense, context)
                linecounter += 1

    return word_map     

map1 = parse_test_data(train_file)
print len(map1)
for x in map1:
    print map1[x].toString()
