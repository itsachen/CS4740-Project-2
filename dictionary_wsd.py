import nltk
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet as wn
import xml.etree.ElementTree as ET
from Parser import Word, Sense

lmtzr = WordNetLemmatizer()

# Lesk with IDF, stemming or lemmatizing for definitions?
# Also could use WordNet to search through synonyms as well

# 1) Develop a metric that rewards overlaps for non-consecutive words
# 2) Find relevant words around target word, filter using IDF. For each specific word.
#    Also some words aren't even in the dictionary?
#    Use wordnet?
# 3) LOL

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

                    tagged_gloss = nltk.pos_tag(nltk.word_tokenize(sense_item.attrib['gloss']))
                    lemmatized_gloss = [lmtzr.lemmatize(x[0],get_pos(x)) for x in tagged_gloss]

                    examples = []
                    split_examples = sense_item.attrib['examples'].split(' | ')
                    for example in split_examples:
                        tagged_example = nltk.pos_tag(nltk.word_tokenize(example))
                        lemmatized_example = [lmtzr.lemmatize(x[0],get_pos(x)) for x in tagged_example]
                        examples.append(lemmatized_example)

                    sense = Sense(sense_id, sense_wordnet_ids, lemmatized_gloss, examples)
                    word_object.add_sense(sense)
                self.dictionary[word_object.word] = word_object

# Target is a Word object
# Features should be a list of lemmatized strings
def find_best_sense(dictionary,target,features):
    if target.word not in dictionary.dictionary:
        print "Target word not in dictionary.xml"
        return
    target_word = dictionary.dictionary[target.word]
    features_context = [] # Contains all of the features glosses and examples, list of lists

    for feature in features:
        lemmatized_feature_word = lmtzr.lemmatize(feature) # Perhaps do lemmatizing outside find_relevance?
        feature_word_synsets = wn.synsets(lemmatized_feature_word)
        feature_signature = []

        for synset in feature_word_synsets:
            lemma, pos, sense_num = synset.name.split('.')
            tokenized_tagged_definition = nltk.pos_tag(nltk.word_tokenize(synset.definition))
            tokenized_lemmatized_definition = [lmtzr.lemmatize(x[0],get_pos(x)) for x in tokenized_tagged_definition]
            feature_signature.append(tokenized_lemmatized_definition)

            for example in synset.examples:
                tokenized_tagged_example = nltk.pos_tag(nltk.word_tokenize(example))
                tokenized_lemmatized_example = [lmtzr.lemmatize(x[0],get_pos(x)) for x in tokenized_tagged_example]
                feature_signature.append(tokenized_lemmatized_example)
        features_context.append(feature_signature)

    best_sense = '1' # Replace with most referenced maybe
    max_score = 0
    for sense in target_word.senses:
        score = calculate_sense_score(sense, features_context)
        if score > max_score:
            max_score = score
            best_sense = sense.id

    return best_sense
    
# The metric 
def calculate_sense_score(target_sense, context_signature):
    # Build target_sense signature
    # Compare
    return 0

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
