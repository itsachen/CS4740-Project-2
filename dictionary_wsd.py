import nltk
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet as wn
import xml.etree.ElementTree as ET
from Parser import Word, Sense

# Lesk with IDF, stemming or lemmatizing for definitions?
# Also could use WordNet to search through synonyms as well

# 1) Develop a metric that rewards overlaps for non-consecutive words
# 2) Find relevant words around target word, filter using IDF. For each specific word.
# 3) LOL

class Dictionary:
    def __init__(self):
       self.dictionary = {}

    def __getitem__(self,k):
        return self.dictionary[k]

    def build_from_xml(self, filename='dictionary_no_examples.xml'):
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
                    sense_gloss = nltk.word_tokenize(sense_item.attrib['gloss'])
                    sense = Sense(sense_id, sense_wordnet_ids, sense_gloss)
                    word_object.add_sense(sense)
                self.dictionary[word_object.word] = word_object

# Finds relevance between two lemmatized words, focused around word_one
def find_relevance(word_one, word_two):
    print "lol marseille"

def test():
    d = Dictionary()
    d.build_from_xml()
    return d
