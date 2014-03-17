import parser, ngram

# word_map is a map of word strings to word objects
# tokenized sentence list is a 
train_file = "training_data.data"
test_file = "test_data.data"

word_map, tokenized_sentence_list = parser.parse_train_data(train_file)

bigram_weight = 1.0
unagram_weight = 1.0


# from a word_map creates a map of words to senses
def get_ngram_map(word_map):
	word_to_sense_to_unagram_map = {}
	word_to_sense_to_bigram_map = {}
	for word_object in word_map.values():
		sense_to_unagram_map = {}
		sense_to_bigram_map = {}
		for sense, context_list in word_object.sense_id_map.items():
			sense_to_unagram_map[sense] = create_ngram_from_context_list(word_object.word,context_list,1)
			sense_to_bigram_map[sense] = create_ngram_from_context_list(word_object.word,context_list,2)
		word_to_sense_to_unagram_map[word_object.word] = sense_to_unagram_map
		word_to_sense_to_bigram_map[word_object.word] = sense_to_bigram_map
	return word_to_sense_to_bigram_map

def create_ngram_from_context_list(word, context_list, n):
	tokenized_context_list = []
	for context in context_list:
		tokenized_context = ["<s>"]
		tokenized_context.extend(context.prev_context)
		tokenized_context.append(word)
		tokenized_context.extend(context.after_context)
		tokenized_context.append("<e>")
		tokenized_context_list.append(tokenized_context)
	return ngram.create_smoothed_ngram_probability_table(tokenized_context_list,n)

def get_ngram_probability(word, context, ngram_map, n):
	tokenized_context = ["<s>"]
	tokenized_context.extend(context.prev_context)
	tokenized_context.append(word)
	tokenized_context.extend(context.after_context)
	tokenized_context.append("<e>")

	word_ngram = ngram_map[word]

	accumulated_probability = {}
	for sense in word_ngram.keys():
		accumulated_probability[sense] = 1.0
	if n == 1:
		for token in tokenized_context:
			for sense, ngram in word_ngram:
				accumulated_probability[sense] *= ngram[token] 
	else:
		prev_token = None;
		for token in tokenized_context:
			if prev_token == None:
				prev_token = token
			else:
				for sense, ngram in word_ngram:
					accumulated_probability[sense] *= ngram[prev_token][token] 
				prev_token = token
	return accumulated_probability

def word_sense_disambiguation(unclassified_words):
	return None
	

print get_ngram_map(word_map)