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

print get_results(sys.argv[1], sys.argv[2])