import string
import nltk
from nltk.stem.porter import *
from stop_words import get_stop_words

stop_words = get_stop_words('en')
stop_words.extend(list(string.punctuation))
stemmer = PorterStemmer()

out_f = open("output_test", "rb")
desc_f = open("test.desc", "rb")
data_f = open("test.data", "rb")

cities = ["amsterdam","antwerp", "asheville", "athens", "austin", "barcelona", "berlin","boston", "brussels", "chicago", "copenhagen", "denver", "dublin", "edinburgh", "geneva", "hong kong", "london", "los angeles", "madrid", "mallorca", "manchester", "melbourne", "montreal", "nashville","new orleans","new york", "nyc", "northern rivers", "oakland", "paris", "portland", "quebec city", "rome", "san diego", "san francisco", "santa cruz", "seattle"]

# stemmed
keywords = ["park", "beach", "supermarket", "downtown", "bar", "restaur", "shop"]

wordD = {}
uniq_cnt_dict = {}
len_dict = {}
junk = cnt = 0

share_words_with_data = {}
share_stem_with_data = {}

share_words_with_desc = {}
share_stem_with_desc = {}

city_all = city_wrong = 0
keyw_all = keyw_wrong = 0

BLEUscore = 0.0

def getAvg(mydict):
    return sum([k*v for k, v in mydict.iteritems()])/float(cnt)

def isJunk(words):
    # current criteria:
    # 1. a word appears too lot (> 5) in nearby positions
    # 2. a word appears too lot in the whole sentence (> 50% of non-stop words)
    word_pos = {}
    dup_word_cnt = {}
    tot_cnt = {}
    tot_words = 0

    for i in range(0, len(words)):
        w = words[i]
        if w in word_pos and i - word_pos[w] <= 3:
            dup_word_cnt[w] = dup_word_cnt.get(w, 0)+1

        word_pos[w] = i
        tot_cnt[w] = tot_cnt.get(w, 0)+1
        tot_words += 1

    for w, c in tot_cnt.iteritems():
        if c > tot_words/2 and dup_word_cnt[w] >= 5:
            return True

    return False


def getStemWords(words):
    stemmed_word_set = set()
    for w in words:
        try:
            stem = stemmer.stem(w)
            stemmed_word_set.add(stem)
        except:
            pass            
    return stemmed_word_set

def cmpData(out_line, out_words):
    global city_all, city_wrong, keyw_all, keyw_wrong
    data_line = data_f.readline().strip()
    for city in cities:
        if city in out_line:
            city_all += 1
            if city == "nyc":
                city = "new york"
            if city not in data_line:
                city_wrong += 1
                #print line
                #print data_info[cnt]
            break

    data_words = data_line.split()
    data_word_set = set(data_words)
    out_word_set = set(out_words)
    shared_words = len(out_word_set.intersection(data_word_set))
    share_words_with_data[shared_words] = share_words_with_data.get(shared_words, 0)+1

    stemmed_out_word_set = getStemWords(out_words)
    stemmed_data_word_set = getStemWords(data_words)
    shared_stemms = len(stemmed_out_word_set.intersection(stemmed_data_word_set))
    share_stem_with_data[shared_stemms] = share_stem_with_data.get(shared_stemms, 0)+1

    for keyw in keywords:
        if keyw in stemmed_out_word_set:
            keyw_all += 1
            if keyw not in stemmed_data_word_set:
                keyw_wrong += 1
    

def cmpDesc(line, out_words):
    global BLEUscore
    desc_line = desc_f.readline().strip()
    desc_words = desc_line.split()
    desc_word_set = set(desc_words)
    out_word_set = set(out_words)
    shared_words = len(desc_word_set.intersection(out_word_set))
    share_words_with_desc[shared_words] = share_words_with_desc.get(shared_words, 0)+1

    stemmed_out_word_set = getStemWords(out_words)
    stemmed_desc_word_set = getStemWords(desc_words)
    shared_stemms = len(stemmed_desc_word_set.intersection(stemmed_out_word_set))
    share_stem_with_desc[shared_stemms] = share_stem_with_desc.get(shared_stemms, 0)+1

    raw_out_words = line.split()
    BLEUscore += nltk.translate.bleu_score.sentence_bleu([desc_words], raw_out_words)
    

def parseLine(line):
    global junk
    words = line.split()
    filter_words = []
    cur_len = len(words)
    #avg_len += cur_len
    len_dict[cur_len] = len_dict.get(cur_len, 0)+1

    for w in words:
        if w in stop_words:
            continue
        filter_words.append(w)
        wordD[w] = wordD.get(w, 0)+1
    
    word_set = set(filter_words)
    uniques = len(word_set)
    #avg_uniq += uniques
    uniq_cnt_dict[uniques] = uniq_cnt_dict.get(uniques, 0)+1

    cmpData(line, filter_words)
    cmpDesc(line, filter_words)
    if isJunk(filter_words):
        junk += 1

for line in out_f:
    line = line.strip()
    parseLine(line)
    cnt += 1

print "junk ratio:", junk/float(cnt)
print "description length", getAvg(len_dict), len_dict
print "unique tokens:", getAvg(uniq_cnt_dict), uniq_cnt_dict
sorted_list = sorted(wordD.items(), key=lambda x:x[1], reverse=True)
print "token frequency:", [w for (w, c) in sorted_list[:50]]
print "###Compare with the data input"
print "share tokens with data:", getAvg(share_words_with_data), share_words_with_data, "share stems with data:", getAvg(share_stem_with_data), share_stem_with_data
print "mentioned city:", city_all, "false mention:", city_wrong
print "mentioned keyword:", keyw_all, "not appeared in data:", keyw_wrong
print "###Compare with the expected description"
print "share tokens with desc:", getAvg(share_words_with_desc), share_words_with_desc, "share stems with desc:", getAvg(share_stem_with_desc), share_stem_with_desc
print "BLEU score:", BLEUscore/cnt

out_f.close()
desc_f.close()
data_f.close()
