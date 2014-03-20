import parser
import ngram

# word_map is a map of word strings to word objects
# tokenized sentence list is a 
train_file = "training_data.data"
test_file = "test_data.data"
vaildation_file = "validation_data.data"
output_file = "supervised_output.csv"

word_map, tokenized_sentence_list = parser.parse_train_data(train_file)
unclassified_words = parser.parse_test_data(test_file)
idf = parser.get_idf(tokenized_sentence_list)
feature_set = set({}) #initialized later

unagram_weight = 1.0
bigram_weight = 1.0

within_sentence_weight = 2.0
outside_sentence_weight = 1.0

idf_cutoff = 2.0

def get_sense_count(word_map):
    word_to_sense_to_count_map = {}
    for word_object in word_map.values():
        sense_to_count_map = {}
        for sense, context_list in word_object.sense_id_map.items():
            sense_to_count_map[sense] = float(len(context_list))
        word_to_sense_to_count_map[word_object.word] = sense_to_count_map
    return word_to_sense_to_count_map

def get_features(idf, tokenized_sentence_list):
    feature_set = set({})

    for sentence in tokenized_sentence_list:
        for feature in sentence:
            if idf[feature] > idf_cutoff and feature not in feature_set:
                feature_set.add(feature)
    return feature_set

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

def get_word_count(word_map, tokenized_sentence_list):
    context_word_count = {}
    global_word_count = {}

    for feature in feature_set:
        global_word_count[feature] = 1.0

    for word_object in word_map.values():
        sense_to_word_count_map = {}
        for sense, context_list in word_object.sense_id_map.items():
            word_count_map = {}
            for feature in feature_set:
                word_count_map[feature] = 1.0

            for context in context_list:
                word_list = context.prev_sentences + context.prev_context + context.after_context + context.after_sentences
                for feature in set(word_list):
                    if feature in feature_set:
                        word_count_map[feature] += 1.0
                        global_word_count[feature] += 1.0
            sense_to_word_count_map[sense] = word_count_map    
        context_word_count[word_object.word] = sense_to_word_count_map
    return context_word_count, global_word_count

# from a word_map creates a map of words to senses
def get_ngram_map(word_map, n):
    word_to_sense_to_ngram_map = {}
    for word_object in word_map.values():
        sense_to_ngram_map = {}
        for sense, context_list in word_object.sense_id_map.items():
            sense_to_ngram_map[sense] = create_ngram_from_context_list(word_object.word,context_list,n)
        word_to_sense_to_ngram_map[word_object.word] = sense_to_ngram_map
    return word_to_sense_to_ngram_map

def create_ngram_from_context_list(word, context_list, n):
    tokenized_context_list = []
    for context in context_list:
        tokenized_context = ["<s>"]
        tokenized_context.extend(context.prev_context)
        tokenized_context.append(word)
        tokenized_context.extend(context.after_context)
        tokenized_context.append("<e>")
        tokenized_context_list.append(tokenized_context)
    probabilityTable, _, _ = ngram.create_smoothed_ngram_probability_table(tokenized_context_list,n)
    return probabilityTable

def get_ngram_probability(word, context, ngram_map, n):
    #tokenized_context = ["<s>"]
    tokenized_context = []
    tokenized_context.extend(context.prev_context)
    tokenized_context.append(word)
    tokenized_context.extend(context.after_context)
    #tokenized_context.append("<e>")

    word_ngram = ngram_map[word]

    accumulated_probability = {}
    for sense in word_ngram.keys():
        accumulated_probability[sense] = 1.0
    if n == 1:
        for sense, ngram in word_ngram.items():
            for token in tokenized_context:
                if token in ngram:
                    accumulated_probability[sense] *= ngram[token]
                else:
                    if "<UNK>" in ngram:
                        accumulated_probability[sense] *= ngram["<UNK>"]
                    else:
                        min_prob = 1.0
                        for token, prob in ngram:
                            if prob < min_prob:
                                min_prob = prob
                        ngram["<UNK>"] = min_prob
                        accumulated_probability[sense] *= min_prob


    else:
        for sense, ngram in word_ngram.items():
            prev_token = None;
            for token in tokenized_context:
                if prev_token == None:
                    prev_token = token
                else:
                    if prev_token in ngram:
                        if token in ngram[prev_token]:
                            accumulated_probability[sense] *= ngram[prev_token][token] 
                            prev_token = token
                        else: 
                            token = "<UNK>"
                            accumulated_probability[sense] *= ngram[prev_token][token] 
                            prev_token = token
                    else: 
                        prev_token = "<UNK>"
                        if token in ngram[prev_token]:
                            accumulated_probability[sense] *= ngram[prev_token][token] 
                            prev_token = token
                        else: 
                            token = "<UNK>"
                            accumulated_probability[sense] *= ngram[prev_token][token] 
                            prev_token = token
    return accumulated_probability

def ngram_classifier(unclassified_words, word_map):
    output = []

    unagram = get_ngram_map(word_map, 1)
    bigram = get_ngram_map(word_map, 2)
    for word in unclassified_words:
        sense_scores = {}
        context = word.sense_id_map[0][0]
        for sense, score in get_ngram_probability(word.word, context, unagram, 1).items():
            sense_scores[sense] = score * unagram_weight
        for sense, score in get_ngram_probability(word.word, context, bigram, 2).items():
            sense_scores[sense] += score * bigram_weight

        #determine output
        current_max = 0.0
        current_sense = 0
        for sense, score in sense_scores.items():
            if score >= current_max:
                current_sense = sense
                current_max = score
        output.append(current_sense)
    return output

def wsd_classifier(unclassified_words, word_map):
    output = []

    sense_count = get_sense_count(word_map)
    sense_probabiltiy = get_sense_probability(word_map)
    context_word_count, global_word_count = get_word_count(word_map, tokenized_sentence_list)

    for word in unclassified_words:
        sense_scores = {}

        context = word.sense_id_map[0][0]
        outside_sentences_feature_list = context.prev_sentences + context.after_sentences
        within_sentences_feature_list = context.prev_context + context.after_context
        trained_word = word_map[word.word]

        for sense in trained_word.sense_id_map.keys():
            sense_scores[sense] = 1.0

        for feature in set(outside_sentences_feature_list):
            if feature in feature_set:
                for sense in trained_word.sense_id_map.keys():
                    if feature in context_word_count[word.word][sense]:
                        probabilty_feature_given_sense = context_word_count[word.word][sense][feature] / sense_count[word.word][sense]
                        probabilty_sense = sense_probabiltiy[word.word][sense]
                        probabilty_feature = global_word_count[feature]
                        sense_scores[sense] *= outside_sentence_weight * probabilty_feature_given_sense * probabilty_sense / probabilty_feature

        for feature in set(within_sentences_feature_list):
            if feature in feature_set:
                for sense in trained_word.sense_id_map.keys():
                    if feature in context_word_count[word.word][sense]:
                        probabilty_feature_given_sense = context_word_count[word.word][sense][feature] / sense_count[word.word][sense]
                        probabilty_sense = sense_probabiltiy[word.word][sense]
                        probabilty_feature = global_word_count[feature]
                        sense_scores[sense] *= within_sentence_weight * probabilty_feature_given_sense * probabilty_sense / probabilty_feature

        #determine output
        current_max = 0.0
        current_sense = 0
        for sense, score in sense_scores.items():
            if score >= current_max:
                current_sense = sense
                current_max = score
        output.append(current_sense)
    return output

def write_to_file(filename, prediction_list):
    file_object = open(filename, 'w+')    
    file_object.write('Id,Prediction\n')
    counter = 1
    for line in prediction_list:
        file_object.write(str(counter) + "," + line + '\n')
        counter += 1
    file_object.close()
    return len(prediction_list)

feature_set = get_features(idf, tokenized_sentence_list)
wsd = wsd_classifier(unclassified_words, word_map)
print str(write_to_file(output_file, wsd))

