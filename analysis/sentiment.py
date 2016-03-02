from nltk.tokenize import TweetTokenizer
import csv

# Word,Positive,Negative,Anger,Anticipation,Disgust,Fear,Joy,Sadness,Surprise,Trust
# 0   , 1      , 2      , 3   , 4          , 5     , 6  , 7 , 8     , 9      , 10

with open('NRC-english.csv', 'rb') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=' ', quotechar='|')

    fear_words = []
    positive_words = []
    negative_words = []

    for row in csv_reader:
        word = row[0].split(',')
        #print(word[6])

        if word[1] == '1':
            #fear_words.append(word[0])
            positive_words.append(word[0])
        if word[2] == '1':
            #fear_words.append(word[0])
            negative_words.append(word[0])

    #print(positive_words)

#print positive_words

#tokens = ['ability', 'absolute', 'blablabla']
tknzr = TweetTokenizer(preserve_case=False)

with open('cnn2.txt', "r") as word_list:
    #words = word_list.read().split()
    cnn_words = tknzr.tokenize(word_list.read())

positive_score = 0
negative_score = 0

for t in cnn_words:
    if t in positive_words:
        positive_score += 1
    if t in negative_words:
        negative_score += 1


# print "positive density: "
# print positive_score/len(cnn_words)
# print "negative density: "
# print float(negative_score/len(cnn_words))
print len(cnn_words)
print positive_score
print negative_score
