def create_unigram_frequency_table(parsed_list, unk):
    frequencyTable = {}
    wordSet = set()
    for token_list in parsed_list:
        for token in token_list:
            if unk and token not in wordSet:
                wordSet.add(token)
                token = '<UNK>'
            if token in frequencyTable:
                frequencyTable[token] += 1
            else:
                frequencyTable[token] = 1
    return frequencyTable

def create_bigram_frequency_table(parsed_list, unk):
    frequencyTable = {}
    wordSet = set()
    if unk :
        unigramFreqTable = create_unigram_frequency_table(parsed_list, False)
        for token in unigramFreqTable :
            if unigramFreqTable[token] == 1 :
                wordSet.add(token)
    
    for token_list in parsed_list:
        token_list_length = len(token_list)
        for i in range(token_list_length):
            if i < token_list_length - 1:
                current_word = token_list[i]
                next_word = token_list[i+1]
                if unk and current_word in wordSet:
                    current_word = '<UNK>'
                if unk and next_word in wordSet :
                    next_word = '<UNK>'
                if current_word in frequencyTable:
                    if next_word in frequencyTable[current_word]:
                        frequencyTable[current_word][next_word] += 1
                    else:
                        frequencyTable[current_word][next_word] = 1
                else:
                    frequencyTable[current_word] = {next_word:1}
    return frequencyTable, wordSet

def create_ngram_frequency_table(parsed_list, n, unk):
    frequencyTable = {}
    wordSet = set()

    for token_list in parsed_list:
        # Append additional sentence start symbols
        for _ in range(n-2):
            token_list.insert(0,'<s>')
        token_list_length = len(token_list)
        for i in range(token_list_length - n + 1):
            # Create the ngram
            ngram = []
            for j in range(i,i+n):
                token = token_list[j] 
                if unk and token not in wordSet :
                    wordSet.add(token)
                    token_list[j] = '<UNK>'
                    token = '<UNK>'
                ngram.append(token)
            update_frequency_table(ngram, frequencyTable, wordSet)
    return frequencyTable, wordSet

# Recursively update the frequency table
def update_frequency_table(ngram, frequency_table, wordSet):
    if len(ngram) == 1:
        if ngram[0] in frequency_table:
            frequency_table[ngram[0]] += 1
        else:
            frequency_table[ngram[0]] = 1
    else:
        if ngram[0] not in frequency_table:
            frequency_table[ngram[0]] = {}
        update_frequency_table(ngram[1:], frequency_table[ngram[0]], wordSet)
                
                
def get_ngram_counts(frequencyTable, counts, totalNgrams, n):
    if n == 1 : 
        for token in frequencyTable :
            freq = frequencyTable[token]
            if frequencyTable[token] in counts :
                counts[freq] += 1
                totalNgrams += 1
            else :
                counts[freq] = 1
                totalNgrams += 1
        return counts, totalNgrams

    for token in frequencyTable:
        counts, totalNgrams = get_ngram_counts(frequencyTable[token], counts, totalNgrams, n-1)
    return counts, totalNgrams
    
def smooth_ngram_frequency_table(frequencyTable, wordSet, n):
    if n == 1:
        return frequencyTable, 1.0
    counts = {}
    totalNgrams = 0
    #Get counts for N1, N2, etc.
    counts,totalNgrams = get_ngram_counts(frequencyTable, {}, 0, n)
    #Determine what frequency counts to smooth
    i = 1
    maxCount = 0
    while i in counts :
        maxCount = i-1
        i += 1
    
    #Smooth frequencies
    for token in frequencyTable :
        for token2 in frequencyTable[token] :
            freq = frequencyTable[token][token2]
            if freq < maxCount :
                frequencyTable[token][token2] = float(freq + 1) * counts[freq + 1] / counts[freq]
    return frequencyTable, float(len(wordSet)) / totalNgrams

def smooth_frequencies(frequencyTable, n, counts, maxCount):
    if n == 1 :
        for token in frequencyTable :
            freq = frequencyTable[token]
            if freq < maxCount :
                frequencyTable[token] = float(freq + 1) * counts[freq + 1] / counts[freq]
    else:
        for token in frequencyTable :
            frequencyTable = smooth_frequencies(frequencyTable[token], n - 1, counts, maxCount)
    return frequencyTable
        
    
    
    
#Returns the new frequency table and an "unknown" probability
def smooth_bigram_frequency_table(frequencyTable, wordSet):
    counts = {}
    totalBigrams = 0
    #Get counts for N1, N2, etc.
    for token in frequencyTable :
        for token2 in frequencyTable[token] :
            freq = frequencyTable[token][token2]
            if frequencyTable[token][token2] in counts :
                counts[freq] += 1
                totalBigrams += 1
            else :
                counts[freq] = 1
                totalBigrams += 1
    #Determine what frequency counts to smooth
    i = 1
    maxCount = 0
    while i in counts :
        maxCount = i-1
        i += 1
    
    #Smooth frequencies
    for token in frequencyTable :
        for token2 in frequencyTable[token] :
            freq = frequencyTable[token][token2]
            if freq < maxCount :
                frequencyTable[token][token2] = float(freq + 1) * counts[freq + 1] / counts[freq]
                
    print len(wordSet)
    print totalBigrams
    return frequencyTable, float(len(wordSet)) / totalBigrams