import random
import math


# -*- coding:utf-8 -*-
class ItemBasedCF:
    def __init__(self, datafile=None, encoding='utf-8'):
        self.encoding = encoding
        self.datafile = datafile
        self.readData()
        self.splitData(3, 47)

    def readData(self, datafile=None):
        """
        read the data from the data file which is a data set
        """
        self.datafile = datafile or self.datafile
        self.encoding = "UTF-8"
        self.data = []
        for line in open(self.datafile):
            userid, itemid, record, mtime = line.split("\t")  
            self.data.append((userid, itemid, int(record)))  

    def splitData(self, k, seed, data=None, M=8):
        """
        split the data set
        testdata is a test data set
        traindata is a train set
        """
        self.testdata = {}  
        self.traindata = {}
        data = data or self.data  
        random.seed(seed)
        for user, item, record in self.data:
            if random.randint(0, M) == k:
                self.testdata.setdefault(user, {})
                # testdata[user]={}
                self.testdata[user][item] = record  
            else:
                self.traindata.setdefault(user, {})
                self.traindata[user][item] = record  

    def ItemSimilarity(self, train=None):  
        """
        calculate co-rated users between items
        """
        train = train or self.traindata
        C = dict()  
        N = dict()
        for u, items in train.items():  
            for i in items.keys():
                N.setdefault(i, 0)
                N[i] += 1
                for j in items.keys():
                    if i == j:
                        continue
                    C.setdefault(i, {})
                    C[i].setdefault(j, 0)
                    C[i][j] += 1
                    
        self.itemSimBest = dict()
        for i, related_items in C.items():  
            self.itemSimBest.setdefault(i, {})
            for j, cij in related_items.items():  
                self.itemSimBest[i].setdefault(j, 0)
                self.itemSimBest[i][j] = cij / math.sqrt(N[i] * N[j])
                

    def ItemSimilarity_IUF(self, train=None):  
        """
        calculate co-rated users between items
        """
        train = train or self.traindata
        C = dict()
        N = dict()
        for u, items in train.items():
            for i in items.keys():
                N.setdefault(i, 0)
                N[i] += 1
                for j in items.keys():
                    if i == j:
                        continue
                    C.setdefault(i, {})
                    C[i].setdefault(j, 0)
                    C[i][j] += 1 / math.log(1 + len(items) * 1.0)  
        self.itemSimBest = dict()
        for i, related_items in C.items():
            self.itemSimBest.setdefault(i, {})
            for j, cij in related_items.items():
                self.itemSimBest[i].setdefault(j, 0)
                self.itemSimBest[i][j] = cij / math.sqrt(N[i] * N[j])  

    def recommend(self, user, train=None, k=8, nitem=40):
        train = train or self.traindata
        rank = dict()
        ru = train.get(user)  
        for i, pi in ru.items():
            for j, wj in sorted(self.itemSimBest[i].items(), key=lambda x: x[1], reverse=True)[0:k]:
                if j in ru:  
                    continue
                rank.setdefault(j, 0)
                rank[j] += pi * wj
        return dict(sorted(rank.items(), key=lambda x: x[1], reverse=True)[0:nitem])  

    def recallAndPrecision(self, train=None, test=None, k=8, nitem=10):
        """
        get the recall and precision
        """
        train = train or self.traindata
        test = test or self.testdata
        hit = 0
        recall = 0
        precision = 0
        for user in train.keys():
            tu = test.get(user, {})
            rank = self.recommend(user, train=train, k=k, nitem=nitem)
            for item, ratings in rank.items():
                if item in tu:  
                    hit += 1
            recall += len(tu)  
            precision += nitem
        return hit / (recall * 1.0), hit / (precision * 1.0)

    def coverage(self, train=None, test=None, k=8, nitem=10):
        train = train or self.traindata
        test = test or self.testdata
        recommend_items = set()
        all_items = set()
        for user in train.keys():
            for item in train[user].keys():
                all_items.add(item) 
            rank = self.recommend(user, train=train, k=k, nitem=nitem)
            for item, ratings in rank.items():
                recommend_items.add(item)  
        return len(recommend_items) / (len(all_items) * 1.0)

    def popularity(self, train=None, test=None, k=8, nitem=10):
        """
        get the popularity
        """
        train = train or self.traindata
        test = test or self.testdata
        item_popularity = dict()
        for user, items in train.items():
            for item in items.keys():
                item_popularity.setdefault(item, 0)
                item_popularity[item] += 1
        ret = 0
        n = 0
        for user in train.keys():
            rank = self.recommend(user, train=train, k=k, nitem=nitem)
            for item, ratings in rank.items():
                ret += math.log(1 + item_popularity[item])
                n += 1
        return ret / (n * 1.0)

    def recpop(self, train=None, test=None, k=8, nitem=10):
        """
        get the popularity
        """
        train = train or self.traindata
        test = test or self.testdata
        item_popularity = dict()
        for user, items in train.items():
            for item in items.keys():
                item_popularity.setdefault(item, 0)
                item_popularity[item] += 1
        ret = 0
        n = 0
        for user in train.keys():
            rank = self.recommend(user, train=train, k=k, nitem=nitem)
            for item, ratings in rank.items():
                ret += math.log(1 + item_popularity[item])
                n += 1
        return rank, ret / (n * 1.0)


def testItemBasedCF():
    cf = ItemBasedCF('C:/Users/HP/Desktop/u1.data')
    cf.ItemSimilarity()
    print("%.13s%3s%20s%20s%20s%20s" % ("             ", 'K', "recall", 'precision', 'coverage', 'popularity'))
    for k in [5, 10, 20, 40, 80, 160, 320, 640, 1280]:
        recall, precision = cf.recallAndPrecision(k=k)
        coverage = cf.coverage(k=k)
        popularity = cf.popularity(k=k)
        print("%.13s%3d%19.3f%%%19.3f%%%19.3f%%%20.3f" % (
            "ItemCF       ", k, recall * 100, precision * 100, coverage * 100, popularity))


def RecommandPopularity():
    print("%.13s%3s%13s%16s" % ("             ", "id", "popularity", "recommandlist"))
    cf = ItemBasedCF('C:/Users/HP/Desktop/u1.data')
    cf.ItemSimilarity_IUF()
    for k in [40]:
        recommandlist, popularity = cf.recpop(k=k)
        # recommandlist = cf.recommend(user=id, train=None, k=k, nitem=None)
        print("%.13s%13.3f" % ("ItemCF_IUF   ", popularity), "%16s" % (recommandlist))


def testUserBasedCF_IUF():
    cf = ItemBasedCF('C:/Users/HP/Desktop/u1.data')
    cf.ItemSimilarity()
    print("%.13s%3s%20s%20s%20s%20s" % ("             ", 'K', "recall", 'precision', 'coverage', 'popularity'))
    # for k in [10]:
    #   recall, precision = cf.recallAndPrecision(k=k)
    #   coverage = cf.coverage(k=k)
    #   popularity = cf.popularity(k=k)
    #   print("%.13s%3d%19.3f%%%19.3f%%%19.3f%%%20.3f" % (
    #      "ItemCF       ", k, recall * 100, precision * 100, coverage * 100, popularity))
    cf.ItemSimilarity_IUF()
    for k in [10]:
        recall, precision = cf.recallAndPrecision(k=k)
        coverage = cf.coverage(k=k)
        popularity = cf.popularity(k=k)
        print("%.13s%3d%19.3f%%%19.3f%%%19.3f%%%20.3f" % (
            "ItemCF_IUF   ", k, recall * 100, precision * 100, coverage * 100, popularity))


if __name__ == "__main__":
    x = int(input("Please enter an integer(1,ItemCF  2,ItemCF_IUF  3,recommand_popularity):"))
    if x == 1:
        testItemBasedCF()
    elif x == 2:
        testUserBasedCF_IUF()
    elif x == 3:
        RecommandPopularity()
