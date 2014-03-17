from Parser import *
from probabilityTable import *
from frequencyTable import *
import random
outList = parse_hotel_reviews()
cumulativeTable = create_frequency_table_bigram(outList)
print cumulativeTable