#!/usr/bin/ python

"""
Query the Reddit Hive

"""
import praw
import random
import sys
import regex
import os
import re
import random
import nltk
import shutil
import csv
import numpy
import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
from collections import defaultdict
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.classify import util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews
from praw.models import MoreComments
from unidecode import unidecode

markov_corp = dict()
company_rank = defaultdict(int)
upvote_list = []
corp = []
companies = []
client_id = 'cDR30pGXp_dJgQ'
client_secret = 'LR1-X94V6H9Xo6YA3KMdoA2JMVA'
reddit = praw.Reddit(client_id=client_id.strip(),
                     client_secret=client_secret.strip(),
                     user_agent='LousBot test')

lastResort = ["10/10", "Instructions unclear", "This.", "kek", "I am a simple man.", "Upvoted.", "Can confirm", "THIS", "Sigh", "ssh bby is ok", "hnnnng"]

def receive_connection():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('localhost', 8080))
    server.listen(1)
    client = server.accept()[0]
    server.close()
    return client


def send_message(client, message):
    print(message)
    client.send('HTTP/1.1 200 OK\r\n\r\n{}'.format(message).encode('utf-8'))
    client.close()

def getInput(sentence):

    reject = re.compile(r"(^')|('$)|\s'|'\s|[\"(\(\)\[\])]")
    try:
        #UCS-4
        myre = re.compile(u'['
                        u'\U0001F300-\U0001F64F'
                        u'\U0001F680-\U0001F6FF'
                        u'\u2600-\u26FF\u2700-\u27BF]+',
                        re.UNICODE)
    except re.error:
        #UCS-2
        myre = re.compile(u'('
                        u'\ud83c[\udf00-\udfff]|'
                        u'\ud83d[\udc00-\ude4f\ude80-\udeff]|'
                        u'[\u2600-\u26FF\u2700-\u27BF])+',
                        re.UNICODE)
                        

    decoded = myre.sub('',sentence)
                        
    decoded = filter(regex.compile('^[a-zA-Z \/.?"@%&:;,=+-_^*#!><()\p{L}]+$').match, decoded)
                        
    return decoded.strip()

def word_split(sentence):
    return re.split(re.compile(r"\s+"), sentence)

def addCompany(name):
    in_comp = open('tmp/companies', 'r')
    for line in in_comp:
        if line.lower().strip() == name.lower().strip():
            print "Already present"
            return "Already present"
    in_comp.close()
    with open("tmp/companies", "a") as myfile:
        myfile.write(name + "\n")
    myfile.close()
    print "Added "+ name +"\n"
    return "Added "+ name +"\n"

def listCompanies():
    in_comp = open('tmp/companies', 'r')
    c = 1
    for line in in_comp:
        print str(c) + ". " + line
        c += 1
    in_comp.close()
    return c-1
                        
def remCompany(name):
    in_comp = open('tmp/companies', 'r')
    list = []
    c = 0
    found = False
    for line in in_comp:
        if line.lower().strip() != name.lower().strip():
            c += 1
            list.append(line)
        else:
            found = True
    in_comp.close()
                        
    in_comp = open('tmp/companies', 'w')
    for i in range(c):
        in_comp.write(list[i])
    in_comp.close()
    
    if found == False:
        print "Not Found\n"
    else:
        print "Removed "+ name +"\n"

def bayes(message):
    negids = movie_reviews.fileids('neg')
    posids = movie_reviews.fileids('pos')
                        
    negfeats = [(word_feats(movie_reviews.words(fileids=[f])), 'neg') for f in negids]
    posfeats = [(word_feats(movie_reviews.words(fileids=[f])), 'pos') for f in posids]

    trainfeats = negfeats[:] + posfeats[:]
                        
    classifier = NaiveBayesClassifier.train(trainfeats)
    return classifier.classify(word_feats(message))

def clearScores():
    folder = 'scores'
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            #elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)

def getQuery(update):
    quit = False
                        
    in_comp = open('tmp/companies', 'r')
    count_comp = 0
    companies = []
    for line in in_comp:
        count_comp += 1
        companies.append(line)
    in_comp.close()
    company_rank = defaultdict(int)

    temp_count = 0
    while quit == False:
        if temp_count == count_comp:
            quit = True
            print count_comp
        else:
                        msg = companies[temp_count]
                        temp_count += 1
                        
                        if os.path.isfile("tmp/raw/" + getInput(msg) + '.raw') == False or update == True:
                            print "Analyzing " + getInput(msg)
                            getRedditPosts(reddit, getInput(msg))


                        # Build the model.
                        #text_model = markovify.Text(text)
                        
                        company_rank[msg] = getScore(getInput(msg), temp_count, count_comp, update)
                        
    count_t = 1
    stringRet = []
    for w in sorted(company_rank, key=company_rank.get, reverse=True):
        print str(count_t) + ". " + str(w) + " " + str(company_rank[w]) + "\n"
        stringRet.append(str(count_t) + ") " + str(w).strip() + " : " + str(company_rank[w]) )
        count_t +=1
    return stringRet
                        
def scanComp(msg):
    query = getInput(msg)

    if os.path.isfile("tmp/raw/" + query + '.raw') == False:
        print "Analyzing " + query
        getRedditPosts(reddit, query)
                        
    curr = getScore(query, 0, 0, False)

    stringRet = []
    input_file = open("tmp/scores/" + query + '.score', 'r')
    for line in input_file:
        stringRet.append(line)
    input_file.close()

    addCompany(msg)

    return stringRet
                    
def extract_features(document):
    document_words = set(document)
    features = {}
    word_features = get_word_features(corp)
    for word in word_features:
        features['contains(%s)' % word] = (word in document_words)
    return features

def word_feats(words):
    return dict([(word, True) for word in words])

def get_words_in_corp(t):
    all_words = []
    for (words, sentiment) in t:
        all_words.extend(words)
    return all_words

def get_word_features(wordlist):
    wordlist = nltk.FreqDist(wordlist)
    word_features = wordlist.keys()
    return word_features
                        
def getScore(query, temp_count, count_comp, update):
    if os.path.isfile("tmp/scores/" + query + '.score') == True and update == False:
        input_file = open("tmp/scores/" + query + '.score', 'r')
        toRet = ""
        for line in input_file:
            toRet = line
        input_file.close()
        return float(line)

    input_file = open("tmp/raw/" + query + '.raw', 'r')
    count_lines = 0
    corp = []
    upvote_list = []
    curr_ind = 0
    for line in input_file:
        if curr_ind % 2 == 1:
            upvote_list.append(line)
        else:
            corp.append(line)
            count_lines += 1
        curr_ind+=1
    input_file.close()

    target = open("tmp/scores/" + query + ".score", 'w+')
    sid = SentimentIntensityAnalyzer()
    sumTot = 0
    sumPos = 0
    sumNeg = 0
    sumComp = 0
    sumNeu = 0
    for i in range(count_lines):
        ss = sid.polarity_scores(corp[i])
        target.write(corp[i])
        up = int(upvote_list[i])
        target.write("Upvotes: " + str(up) + "\n")
        sumTot += abs(up)
        for k in ss:
            if k == "neg":
                sumNeg += up*ss[k]
                target.write("Neg: " + str(up*ss[k]))
            if k == "pos":
                sumPos += up*ss[k]
                target.write("Pos: " + str(up*ss[k]))
            if k == "compound":
                sumComp += up*ss[k]
                target.write("Comp: " + str(up*ss[k]))
            if k == "neu":
                sumNeu += up*ss[k]
                target.write("Neu: " + str(up*ss[k]))
            target.write("\n")
    if sumTot == 0:
        sumTot = 0.001
    if temp_count == 0 and count_comp == 0:
        output = query + " Total: " + str(sumTot) + " Neg: " + str(sumNeg/sumTot) + " Neu: " + str(sumNeu/sumTot) + " Pos: " + str(sumPos/sumTot) + " Comp: " + str(sumComp/sumTot)+ "\n"
    else:
        output = "(" + str(temp_count) + "/" + str(count_comp) + ") " + query + " Total: " + str(sumTot) + " Neg: " + str(sumNeg/sumTot) + " Neu: " + str(sumNeu/sumTot) + " Pos: " + str(sumPos/sumTot) + " Comp: " + str(sumComp/sumTot)+ "\n"
    print output
    target.write(output)
                        
    target.write(str(sumComp/sumTot))
    return sumComp/sumTot
                        
def eval(filename):

    print "Input your judgements as floats, where most negative sentiment is -4 and most positive sentiment is 4.\n"

    filename = filename + ".score"
    if os.path.isfile('tmp/scores/' + filename):
            in_comp = open('tmp/scores/' + filename, 'r')
            count_comp = 0
            targetc = open('tmp/statistic/' + filename + "_compute", 'w+')
            targeth = open('tmp/statistic/' + filename + "_human", 'w+')
            currLine = ""
            sum = 0
            upvTot = 0
            for line in in_comp:
                if count_comp % 6 == 0: #
                    currLine = line
                elif (count_comp-1) % 6 == 0:
                    print currLine
                    if line.find(': ') == -1:
                        targetc.write(line)
                        print "Model: " + line
                        targeth.write(str(sum/upvTot))
                        print "Human: " + str(sum/upvTot)
                    else:
                        while True:
                            try:
                                x = raw_input("Input your judgement [-4, 4]: ")
                                indUp = line.find(': ')
                                upv = int(line[indUp+2:].strip())
                                calc = upv*float(x)
                            except ValueError:
                                print("Sorry, I didn't understand that.")
                                continue
                            else:
                                break
                        upvTot += abs(upv)
                        sum += calc
                        targeth.write(currLine + str(calc) + "\n")
                elif (count_comp+1) % 6 == 0:
                    colon = line.find(': ')
                    targetc.write(currLine + str(line)[colon+2:])
                count_comp += 1

            in_comp.close()
            targetc.close()
            targeth.close()
                        
def evaluate():

    data = []
    comp_names = ['Company', 'Model', 'Human']
    data.append(comp_names)
    company_name = ""
    for file in os.listdir('tmp/statistic'):
        ind = file.find(".score")
        if file[:ind] != company_name:
            company_name = file[:ind]
            dataOne = []
            dataOne.append(company_name)
        if file.endswith(".score_compute") or file.endswith(".score_human"):
            fullpath = os.path.join('tmp/statistic', file)
            input_file = open(fullpath, 'r')
            toAdd = ""
            for line in input_file:
                toAdd = line
            input_file.close()
            dataOne.append(toAdd.strip())
        if file.endswith(".score_human"):
            data.append(dataOne)
                        
    b = open('tmp/test.csv', 'w+')
    a = csv.writer(b)
    a.writerows(data)
    b.close()
    print "Created CSV\n"
    
    test = pd.read_csv('tmp/test.csv', sep=',')
    sns.set_style("darkgrid")
    fig, ax = plt.subplots()
    sns.pointplot(x="Company", y="Human", data=test, ax=ax, color='b')
    sns.pointplot(x="Company", y="Model", data=test, ax=ax, color='r')
    ax.set(xlabel='Companies', ylabel='Compound Sentiment')
    ax.set_title('Reddit Sentiment as Judged by Human and Model')
    ax.legend(handles=ax.lines[::len(test)+1], labels=["Human","Model"])
                        
    ax.set_xticklabels([t.get_text() for t in ax.get_xticklabels()])

    plt.gcf().autofmt_xdate()
    fig.savefig('tmp/graph.png')
    sns.plt.show()



def getRedditPosts(reddit, query):
    all = reddit.subreddit("all")

    target = open("tmp/raw/" + query + ".raw", 'w+')

    for i in all.search(query + " company", sort='top', syntax='cloudsearch', limit=5):
            link = i.url

            i.comments.replace_more(limit=2)
            for top_level_comment in i.comments:
                line = getInput(top_level_comment.body.strip()).lower()
                words = word_split(line)
                if len(words) < 2:
                    continue
                
                if line.find(query.lower()) > -1:
                    target.write(line + '\n')
                    target.write(str(top_level_comment.ups) + "\n")

    target.close()


def main():

    nltk.download('vader_lexicon', '../nltk_data')
    nltk.download('movie_reviews', '../nltk_data')
    nltk.data.path.append('../nltk_data')
    in_comp = open('tmp/companies', 'r')
        

    menu = \
                        "============================================================\n"\
                        "==         The Reddit Hivemind Sentiment Analysis         ==\n"\
                        "==                                                        ==\n"\
                        "============================================================\n"\
                        "                                                            \n"\
                        "  OPTIONS:                                                    \n"\
                        "  1 = Fast scan using last updated data                       \n"\
                        "  2 = Medium scan to re-calc scores from corpora              \n"\
                        "  3 = Scan all companies from scratch (~30 sec/company)       \n"\
                        "  4 = List companies                                          \n"\
                        "  5 = Add company                                             \n"\
                        "  6 = Remove company                                          \n"\
                        "  7 = Input Survey Data for Test Evaluation                   \n"\
                        "  8 = Graph Test Evaluation                                   \n"\
                        "  9 = Quit                                                    \n"\
                        "                                                              \n"\
                        "============================================================\n".format()
    while True:
        sys.stderr.write(menu)
        option = raw_input("Enter Option: ")
        if option == "1":
            getQuery(False)
        elif option == "2":
            clearScores()
            getQuery(False)
        elif option == "3":
            getQuery(True)
        elif option == "4":
            listCompanies()
        elif option == "5":
            addCompany(raw_input("Enter Name: "))
        elif option == "6":
            remCompany(raw_input("Enter Name: "))
        elif option == "7":
            listCompanies()
            eval(raw_input("Enter Company to Eval: "))
        elif option == "8":
            evaluate()
        elif option == "9":
            exit(0)
        else:
            sys.stderr.write("Input seems not right, try again\n")
    return 0


if __name__ == '__main__':
    sys.exit(main())
