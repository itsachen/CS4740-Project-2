import Parser
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
import test

#Add context from previous sentences
#Add cooccurrence features?
#add lemmatizer matches target

train_file = "training_data.data"
test_file = "test_data.data"
validation_file = "validation_data.data"
output_file = "supervised_output.csv"
lmtzr = WordNetLemmatizer()
idf_cutoff = 2.0

NUM_NGRAMS_OBSERVED = 5
NUM_COMMON_WORDS = 5
stopwords = stopwords.words('english')
word_map, tokenized_sentence_list = Parser.parse_train_data(train_file)
unclassified_words = Parser.parse_test_data(test_file)

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
 
def get_target_probability(word_map):
    word_to_sense_to_target_probability_map = {}
    for word_object in word_map.values():
        sense_to_target_count_map = {}
        for sense, context_list in word_object.sense_id_map.items():
            count = 1
            if sense not in sense_to_target_count_map:
                sense_to_target_count_map[sense] = {}
            for context in context_list:
                count +=1
                target = context.target
                if target in sense_to_target_count_map[sense]:
                    sense_to_target_count_map[sense][target] += 1
                else:
                    sense_to_target_count_map[sense][target] = 1
            for target in sense_to_target_count_map[sense]:
                sense_to_target_count_map[sense][target] /= float(count + 1)
            sense_to_target_count_map[sense]['<UNK>'] = 1 / float(count + 1)
        word_to_sense_to_target_probability_map[word_object.word] = sense_to_target_count_map
    return word_to_sense_to_target_probability_map

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
                word_to_sense_to_unigram_counts[word_object.word][sense]['left'] = {}
                word_to_sense_to_unigram_counts[word_object.word][sense]['right'] = {}
            for context in context_list :
                prev, after = context.prev_context, context.after_context
                for i in range(len(prev)-NUM_NGRAMS_OBSERVED -1, len(prev)-1):
                    if i < 0 :
                        continue
                    token = lmtzr.lemmatize(prev[i])
                    if token in word_to_sense_to_unigram_counts[word_object.word][sense]['left']:
                        word_to_sense_to_unigram_counts[word_object.word][sense]['left'][token] += 1
                    else:
                        word_to_sense_to_unigram_counts[word_object.word][sense]['left'][token] = 1
                        if token not in wordSet :
                            wordSet.add(token)
                            numWords +=1
                for i in range(len(after)-NUM_NGRAMS_OBSERVED-1, len(after)-1):
                    if i < 0 :
                        continue
                    token = lmtzr.lemmatize(after[i])
                    if token in word_to_sense_to_unigram_counts[word_object.word][sense]['right']:
                        word_to_sense_to_unigram_counts[word_object.word][sense]['right'][token] += 1
                    else:
                        word_to_sense_to_unigram_counts[word_object.word][sense]['right'][token] = 1
                        if token not in wordSet :
                            wordSet.add(token)
                            numWords +=1
    word_to_sense_to_unigram_prob = {} 
    for word_object in word_map.values():
        word_to_sense_to_unigram_prob[word_object.word] = {}
        for sense, _ in word_object.sense_id_map.items():
            word_to_sense_to_unigram_prob[word_object.word][sense] = {}
            word_to_sense_to_unigram_prob[word_object.word][sense]['left'] = {}
            count = 0
            for token in word_to_sense_to_unigram_counts[word_object.word][sense]['left']:
                count += word_to_sense_to_unigram_counts[word_object.word][sense]['left'][token]
                #if word_to_sense_to_unigram_counts[word_object.word][sense][token] == 1 :
            for token in word_to_sense_to_unigram_counts[word_object.word][sense]['left']:
                word_to_sense_to_unigram_prob[word_object.word][sense]['left'][token] = (word_to_sense_to_unigram_counts[word_object.word][sense]['left'][token] + 1) / (float(count) + numWords + 1)
            word_to_sense_to_unigram_prob[word_object.word][sense]['left']['<UNK>'] = 1 / float(numWords)
            
            word_to_sense_to_unigram_prob[word_object.word][sense]['right'] = {}
            count = 0
            for token in word_to_sense_to_unigram_counts[word_object.word][sense]['right']:
                count += word_to_sense_to_unigram_counts[word_object.word][sense]['right'][token]
                #if word_to_sense_to_unigram_counts[word_object.word][sense][token] == 1 :
            for token in word_to_sense_to_unigram_counts[word_object.word][sense]['right']:
                word_to_sense_to_unigram_prob[word_object.word][sense]['right'][token] = (word_to_sense_to_unigram_counts[word_object.word][sense]['right'][token] + 1) / (float(count) + numWords + 1)
            word_to_sense_to_unigram_prob[word_object.word][sense]['right']['<UNK>'] = 1 / float(numWords)
                
    return word_to_sense_to_unigram_prob

def score_validation_set(unclassified_words, unigram_model, word_map, outputFile):
    word_to_sense_probability_map = get_sense_probability(word_map)
    target_word_probability_map = get_target_probability(word_map)
    text_file = open("output.txt", "w")
    for word_object in unclassified_words:
        bestSense = 0
        bestProbability = 0
        if word_object.word not in unigram_model:
            bestSense = 1
        else:
            for sense in unigram_model[word_object.word]:
                unigram_probability = unigram_model[word_object.word][sense]
                probability = word_to_sense_probability_map[word_object.word][sense]
                context = word_object.sense_id_map[0][0]
                prev, after = context.prev_context, context.after_context
                
                for i in range(len(after)-NUM_NGRAMS_OBSERVED-1, len(after)-1):
                    unigram_probability_right = unigram_probability['right']
                    if i < 0 :
                        #probability *= unigram_probability_right['<UNK>']
                        continue
                    token = lmtzr.lemmatize(after[i])
                    if token not in stopwords:
                        if token in unigram_probability_right:
                            probability *= unigram_probability_right[token]
                        else:
                            probability *= unigram_probability_right['<UNK>']
                if context.target in target_word_probability_map[word_object.word][sense]:
                    probability *= target_word_probability_map[word_object.word][sense][context.target]
                else:
                    probability *= target_word_probability_map[word_object.word][sense]['<UNK>']
                if probability > bestProbability:
                    bestProbability = probability
                    bestSense = sense
        text_file.write(str(bestSense) + "\n")
    text_file.close()
    
#I'm lazy so I'm just copying my other method and changing the output
def soft_score(unclassified_words, unigram_model, word_map, outputFile):
    word_to_sense_probability_map = get_sense_probability(word_map)
    target_word_probability_map = get_target_probability(word_map)
    text_file = open("output.txt", "w")
    for word_object in unclassified_words:
        totalSense = 0
        bestSense = 0
        bestProbability = 0
        if word_object.word not in unigram_model:
            bestSense = 1
            totalSense = 1
        else:
            for sense in unigram_model[word_object.word]:
                unigram_probability = unigram_model[word_object.word][sense]
                probability = word_to_sense_probability_map[word_object.word][sense]
                context = word_object.sense_id_map[0][0]
                prev, after = context.prev_context, context.after_context
                for i in range(len(prev)-NUM_NGRAMS_OBSERVED-1, len(prev)-1):
                    unigram_probability_left = unigram_probability['left']
                    if i < 0 :
                        #probability *= unigram_probability_left['<UNK>']
                        continue
                    token = lmtzr.lemmatize(prev[i])
                    if token not in stopwords:
                        if token in unigram_probability_left:
                            probability *= unigram_probability_left[token]
                        else:
                            probability *= unigram_probability_left['<UNK>']
                for i in range(len(after)-NUM_NGRAMS_OBSERVED-1, len(after)-1):
                    unigram_probability_right = unigram_probability['right']
                    if i < 0 :
                        #probability *= unigram_probability_right['<UNK>']
                        continue
                    token = lmtzr.lemmatize(after[i])
                    if token not in stopwords:
                        if token in unigram_probability_right:
                            probability *= unigram_probability_right[token]
                        else:
                            probability *= unigram_probability_right['<UNK>']
                if context.target in target_word_probability_map[word_object.word][sense]:
                    probability *= target_word_probability_map[word_object.word][sense][context.target]
                else:
                    probability *= target_word_probability_map[word_object.word][sense]['<UNK>']
                if probability > bestProbability:
                    bestProbability = probability
                    bestSense = sense
                totalSense +=probability
        text_file.write(str(bestSense) + ", " + str(float(bestProbability) / totalSense) + "\n")
    text_file.close()
    
word_to_sense_probability_map = get_sense_probability(word_map)
print get_sense_count(word_map)
print get_sense_probability(word_map)
print "unigram"
unigram_model = create_unigram_from_context(word_map)
score_validation_set(unclassified_words, unigram_model, word_map, "output.txt")
#test.compute_hard_and_soft_score("validation_senses.txt", "output.txt")
test.convert_results_to_submission("output.txt", "outputSubmission.txt")
