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
    tokenized_sentence_list = []
    i = 0
    with open(filename) as f:
        for line in f:
            i+=1
            if i%100 == 0:
                print i
                
            parts = re.split(' \| ', line)
            splitByPeriod = re.split('\.', parts[0])
            word = splitByPeriod[0]
            pos = splitByPeriod[1]
            sense = parts[1]
            context = parts[2]

            #Create word map
            if not word in word_map:
                word_map[word] = Word(word, pos)
            word_map[word].add_context(sense, context)

            #Create token list    
            tokenized_sentence = nltk.word_tokenize(line)
            tokenized_sentence.insert(0,'<s>')
            tokenized_sentence.append('<e>')
            tokenized_sentence_list.append(tokenized_sentence)

    return word_map, tokenized_sentence_list
    
def parse_senses_from_file(filename, outputFile):
    word_map = {}
    tokenized_sentence_list = []
    s = ""
    text_file = open(outputFile, "w")
    with open(filename) as f:
        for line in f:
            parts = re.split(' \| ', line)
            sense = parts[1]
            text_file.write(sense + "\n")
    text_file.close()

    return

# inverse document frequency is defined as the total number of documents in the corpus 
# divided by the number of total number of documents including that word.
def get_idf(tokenized_sentence_list):
    word_map = {}
    for sentence in tokenized_sentence_list:
        word_set = set(sentence)
        for word in word_set:
            if word in word_map:
                word_map[word] += 1.0
            else:
                word_map[word] = 1.0
    l = float(len(tokenized_sentence_list))
    for key,value in word_map.items():
        word_map[key] = l / word_map[key]
    return word_map




word_map, tokenized_sentence_list = parse_test_data(train_file)
#print get_idf(tokenized_sentence_list)
