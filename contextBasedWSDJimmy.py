import Parser
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet as wn

train_file = "training_data.data"
test_file = "test_data.data"
validation_file = "validation_data.data"
output_file = "supervised_output.csv"
lmtzr = WordNetLemmatizer()
NUM_NGRAMS_OBSERVED = 5

word_map, tokenized_sentence_list = Parser.parse_train_data(train_file)
unclassified_words = Parser.parse_test_data(test_file)
idf = Parser.get_idf(tokenized_sentence_list)

def get_sense_count(word_map):
    word_to_sense_to_count_map = {}
    for word_object in word_map.values():
        sense_to_count_map = {}
        for sense, context_list in word_object.sense_id_map.items():
            sense_to_count_map[sense] = float(len(context_list))
        word_to_sense_to_count_map[word_object.word] = sense_to_count_map
    return word_to_sense_to_count_map

def get_sense_probability(word_map):
    word_to_sense_probability_map = {}
    for word_object in word_map.values():
        sense_probabiltiy = {}
        counter = 0.0
        for sense, context_list in word_object.sense_id_map.items():
            counter += float(len(context_list))
        for sense, context_list in word_object.sense_id_map.items():
            sense_probabiltiy[sense] = float(len(context_list)) / counter
        word_to_sense_probability_map[word_object.word] = sense_probabiltiy
    return word_to_sense_probability_map

#conside prev and after contexts the same for now
def create_unigram_from_context(word_map):
    word_to_sense_to_unigram_counts = {}
    numWords = 0
    for word_object in word_map.values():
        if not word_object.word in word_to_sense_to_unigram_counts:
            word_to_sense_to_unigram_counts[word_object.word] = {}
        for sense, context_list in word_object.sense_id_map.items():
            wordSet = set()
            if not sense in word_to_sense_to_unigram_counts[word_object.word]:
                word_to_sense_to_unigram_counts[word_object.word][sense] = {}
            for context in context_list :
                prev, after = context.prev_context, context.after_context
                for i in range(len(prev)-NUM_NGRAMS_OBSERVED -1, len(prev)-1):
                    if i < 0 :
                        continue
                    token = lmtzr.lemmatize(prev[i])
                    if token in word_to_sense_to_unigram_counts[word_object.word][sense]:
                        word_to_sense_to_unigram_counts[word_object.word][sense][token] += 1
                    else:
                        word_to_sense_to_unigram_counts[word_object.word][sense][token] = 1
                        if token not in wordSet :
                            wordSet.add(token)
                            numWords +=1
                for i in range(len(after)-NUM_NGRAMS_OBSERVED-1, len(after)-1):
                    if i < 0 :
                        continue
                    token = lmtzr.lemmatize(after[i])
                    if token in word_to_sense_to_unigram_counts[word_object.word][sense]:
                        word_to_sense_to_unigram_counts[word_object.word][sense][token] += 1
                    else:
                        word_to_sense_to_unigram_counts[word_object.word][sense][token] = 1
                        if token not in wordSet :
                            wordSet.add(token)
                            numWords +=1
    word_to_sense_to_unigram_prob = {} 
    for word_object in word_map.values():
        word_to_sense_to_unigram_prob[word_object.word] = {}
        for sense, _ in word_object.sense_id_map.items():
            word_to_sense_to_unigram_prob[word_object.word][sense] = {}
            count = 0
            for token in word_to_sense_to_unigram_counts[word_object.word][sense]:
                count += word_to_sense_to_unigram_counts[word_object.word][sense][token]
                #if word_to_sense_to_unigram_counts[word_object.word][sense][token] == 1 :
            for token in word_to_sense_to_unigram_counts[word_object.word][sense]:
                word_to_sense_to_unigram_prob[word_object.word][sense][token] = (word_to_sense_to_unigram_counts[word_object.word][sense][token] + 1) / (float(count) + numWords + 1)
            word_to_sense_to_unigram_prob[word_object.word][sense]['<UNK>'] = 1 / float(numWords)
            #print word_to_sense_to_unigram_prob[word_object.word][sense]['<UNK>'] 
                
    return word_to_sense_to_unigram_prob

def score_validation_set(unclassified_words, unigram_model, word_map):
    word_to_sense_probability_map = get_sense_probability(word_map)
    text_file = open("jimmy.txt", "w")
    for word_object in unclassified_words:
        bestSense = 0
        bestProbability = 0
        for sense in unigram_model[word_object.word]:
            unigram_probability = unigram_model[word_object.word][sense]
            probability = word_to_sense_probability_map[word_object.word][sense]
            context = word_object.sense_id_map[0][0]
            prev, after = context.prev_context, context.after_context
            for i in range(len(prev)-NUM_NGRAMS_OBSERVED-1, len(prev)-1):
                if i < 0 :
                    probability *= unigram_probability['<UNK>']
                    continue
                token = lmtzr.lemmatize(prev[i])
                if token in unigram_probability:
                    probability *= unigram_probability[token]
                else:
                    probability *= unigram_probability['<UNK>']
            for i in range(len(after)-NUM_NGRAMS_OBSERVED-1, len(after)-1):
                if i < 0 :
                    probability *= unigram_probability['<UNK>']
                    continue
                token = lmtzr.lemmatize(after[i])
                if token in unigram_probability:
                    probability *= unigram_probability[token]
                else:
                    probability *= unigram_probability['<UNK>']
            if probability > bestProbability:
                bestProbability = probability
                bestSense = sense
        text_file.write(bestSense + "\n")
    text_file.close()
    
word_to_sense_probability_map = get_sense_probability(word_map)
print get_sense_count(word_map)
print get_sense_probability(word_map)
print "unigram"
unigram_model = create_unigram_from_context(word_map)
score_validation_set(unclassified_words, unigram_model, word_map)