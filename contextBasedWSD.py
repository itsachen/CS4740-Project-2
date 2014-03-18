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

unagram_weight = 1.0
bigram_weight = 1.0


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
    probabilityTable, prob, wordSet = ngram.create_smoothed_ngram_probability_table(tokenized_context_list,n)
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
        for sense, ngram in word_ngram.items():
            prev_token = None;
            for token in tokenized_context:
                if prev_token == None:
                    prev_token = token
                else:
                    if prev_token in ngram and token in ngram[prev_token]:
                        accumulated_probability[sense] *= ngram[prev_token][token] 
                        prev_token = token
    return accumulated_probability

def word_sense_disambiguation(unclassified_words, word_map):
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

def write_to_file(filename, prediction_list):
    file_object = open(filename, 'w+')    
    file_object.write('Id,Prediction\n')
    counter = 1
    for line in prediction_list:
        file_object.write(str(counter) + ",1" + '\n')
        counter += 1
    file_object.close()
    return len(prediction_list)

wsd = word_sense_disambiguation(unclassified_words, word_map)
print str(write_to_file(output_file, wsd))

