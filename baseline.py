import Parser
import re
import random

def most_common_baseline(word_map):
    text_file = open("mostCommon.txt", "w")
    with open("test_data.data") as f:
        for line in f:
            parts = re.split(' \| ', line)
            splitByPeriod = re.split('\.', parts[0])
            word = splitByPeriod[0]
            sense_map = word_map[word].sense_id_map
            mostCommonSense = 1
            mostCommonSenseCount = 0
            for key, value in sense_map.items():
                if len(value) > mostCommonSenseCount:
                    mostCommonSense = key
                    mostCommonSenseCount = len(value)
            text_file.write(mostCommonSense + "\n")
    text_file.close()
    
def random_baseline(word_map):
    text_file = open("random.txt", "w")
    with open("validation_data.data") as f:
        for line in f:
            parts = re.split(' \| ', line)
            splitByPeriod = re.split('\.', parts[0])
            word = splitByPeriod[0]
            sense_map = word_map[word].sense_id_map
            keyList = []
            for key, _ in sense_map.items():
                keyList.append(key)
            i = random.randint(0, len(keyList)-1)
            text_file.write(keyList[i] + "\n")
    text_file.close()

word_map, _ = Parser.parse_train_data("training_data.data")
most_common_baseline(word_map)
#random_baseline(word_map)