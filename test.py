import sys
test_file = "validation_data.data"

def get_results(testFile, outFile):
    numCorrect = 0
    total = 0
    testArray = []
    resultArray = []
    with open(testFile) as f:
        for line in f:
            testArray.append(line)
    with open(outFile) as f:
        for line in f:
            resultArray.append(line)
    
    for i in range(0, min(len(testArray), len(resultArray))):
        if testArray[i] == resultArray[i]:
            numCorrect+=1
        total+=1
    return float(numCorrect)/total


def convert_results_to_submission(textFile, outputFile):
    text_file = open(outputFile, "w")
    text_file.write("Id,Prediction\n")
    with open(textFile) as f:
        i = 1
        for line in f:
            text_file.write(str(i) + "," + line)
            i+=1
    text_file.close()
    
def compute_hard_and_soft_score(textFile, outputFile):
    numCorrect = 0
    softScoreTotal = 0
    total = 0
    testArray = []
    resultArray = []
    softScore = []
    with open(textFile) as f:
        for line in f:
            line = line.rstrip('\n')
            testArray.append(line)
    with open(outputFile) as f:
        for line in f:
            line = line.rstrip('\n')
            arr = line.split(", ")
            resultArray.append(arr[0])
            softScore.append(arr[1])
    
    for i in range(0, min(len(testArray), len(resultArray))):
        if testArray[i] == resultArray[i]:
            numCorrect+=1
            softScoreTotal += float(softScore[i])
        else:
            softScoreTotal += (1 - float(softScore[i]))
        total+=1
    print "hard score: " + str(float(numCorrect)/total)
    print "soft score: " + str(float(softScoreTotal)/total)
        
def remove_every_other_line(inFile, outFile):
    text_file = open(outFile, "w")
    i = 0
    with open(inFile) as f:
        for line in f:
            if i % 2 == 0:
                text_file.write(line)
            i+=1
    text_file.close()
#print get_results(sys.argv[1], sys.argv[2])    
#convert_results_to_submission(sys.argv[1], sys.argv[2])
#compute_hard_and_soft_score(sys.argv[1], sys.argv[2])

#remove_every_other_line(sys.argv[1], sys.argv[2])
