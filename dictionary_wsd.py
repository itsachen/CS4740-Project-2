import nltk
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet as wn
import xml.etree.ElementTree as ET
from Parser import Word, Sense, get_idf

lmtzr = WordNetLemmatizer()
LEMMATIZE = False # Lemmatize gloss and examples

class Dictionary:
    def __init__(self):
       self.dictionary = {}

    def __getitem__(self,k):
        return self.dictionary[k]

    def build_from_xml(self, filename='dictionary.xml'):
        with open(filename) as f:
            root = ET.fromstring(f.read())

            for word_item in root:
                word, pos = word_item.attrib['item'].split('.')
                word_object = Word(word, pos)
                
                for sense_item in word_item:
                    sense_id = sense_item.attrib['id']

                    sense_wordnet_ids = sense_item.attrib['wordnet'].split('.')
                    if (len(sense_wordnet_ids) == 1) and (sense_wordnet_ids[0] == ''):
                        sense_wordnet_ids = []

                    gloss = []
                    if LEMMATIZE:
                        tagged_gloss = nltk.pos_tag(nltk.word_tokenize(sense_item.attrib['gloss']))
                        gloss = [lmtzr.lemmatize(x[0],get_pos(x)) for x in tagged_gloss]
                    else:
                        gloss = nltk.word_tokenize(sense_item.attrib['gloss'])

                    examples = []
                    split_examples = sense_item.attrib['examples'].split(' | ')
                    for example_sentence in split_examples:
                        example = []
                        if LEMMATIZE:
                            tagged_example = nltk.pos_tag(nltk.word_tokenize(example_sentence))
                            example = [lmtzr.lemmatize(x[0],get_pos(x)) for x in tagged_example]
                        else:
                            example = nltk.word_tokenize(example_sentence)
                        examples.append(example)

                    sense = Sense(sense_id, sense_wordnet_ids, gloss, examples)
                    word_object.add_sense(sense)
                self.dictionary[word_object.word] = word_object

# Target is a Word object
# Features should be a list of lemmatized strings (carry weight?)
def find_best_sense(dictionary,target,features):
    if target.word not in dictionary.dictionary:
        print "Target word not in dictionary.xml"
        return
    target_word = dictionary.dictionary[target.word]

    # Building up the features documents
    features_context = [[]] # Contains all of the features glosses and examples, list of lists
    for feature in features:
        feature_word_synsets = wn.synsets(feature)
        feature_signature = []

        for synset in feature_word_synsets:
            lemma, pos, sense_num = synset.name.split('.')
            synset_definition = []
            if LEMMATIZE:
                tokenized_tagged_definition = nltk.pos_tag(nltk.word_tokenize(synset.definition))
                synset_definition = [lmtzr.lemmatize(x[0],get_pos(x)) for x in tokenized_tagged_definition]
            else:
                synset_definition = nltk.word_tokenize(synset.definition)
            feature_signature.append(synset_definition)

            for example in synset.examples:
                tokenized_final_example = []
                if LEMMATIZE:
                    tokenized_tagged_example = nltk.pos_tag(nltk.word_tokenize(example))
                    tokenized_final_example = [lmtzr.lemmatize(x[0],get_pos(x)) for x in tokenized_tagged_example]
                else:
                    tokenized_final_example = nltk.word_tokenize(example)
                feature_signature.append(tokenized_final_example)
        features_context += feature_signature

    # IDF based weights of tokens
    shared_signature = [[]] # Complete list of documents (glosses/examples) shared between target and features
    shared_signature += features_context
    target_sense_signatures = {}
    for sense_id,sense in target_word.senses.iteritems():
        target_sense_signatures[sense_id] = []
        target_sense_signatures[sense_id].append(sense.gloss)
        target_sense_signatures[sense_id] += sense.examples
        shared_signature += target_sense_signatures[sense_id]
    idf_map = get_idf(shared_signature)

    # Determining best sense
    best_sense = '1' # Replace with most referenced maybe
    max_score = -1
    for sense_id,sense in target_word.senses.iteritems():

        target_sense_signature = target_sense_signatures[sense_id]
        score = 0.0

        for target in target_sense_signature:
            for context in features_context:
                score += calculate_overlap_score(idf_map, target, context)
        score = score / len(target_sense_signature) # Average the scores by the number of examples provided

        if score > max_score:
            max_score = score
            best_sense = sense_id
    print max_score
    return best_sense

# Overlaps of size n are weighted in a way...
# Score of an n-sized overlap is n + n-1 +...0
def calculate_overlap_score(idf_map, target_token_list, context_token_list):
    score = 0.0
    if len(context_token_list) == 0:
        return score
    for i in range(len(target_token_list)):
        original_i = i
        for j in range(len(context_token_list)):
            i = original_i
            matched = []
            while i < len(target_token_list) and j < len(context_token_list):
                if target_token_list[i] == context_token_list[j]:
                    matched.append(target_token_list[i])
                    i += 1
                    j += 1
                else:
                    break
            if len(matched) >= 2:
                # print matched
                acc = 0.0
                for match in matched:
                    acc += idf_map[match]
                weight = acc / len(matched)
                score += weight
    return score

# x is a tuple of (word, POS)
def get_pos(x):
    (word, pos) = x
    if pos.startswith('J'):
        return wn.ADJ
    elif pos.startswith('V'):
        return wn.VERB
    elif pos.startswith('N'):
        return wn.NOUN
    else:
        return wn.ADV

# Test
d = Dictionary()
d.build_from_xml()
# print find_best_sense(d,d['president'], "bills constitution provisions congress laws violate office".split(' '))
