import copy

class Apriori(object):
    
    def convertToTransactionsItems(self, tidata):  #pass in formatted 3d array of biclusters
        tilist = []
        itemset = set()
        for i in range(0, len(tidata)):
            tilist.append([])
            for j in range(0, len(tidata[i])):
                tilist[i].append(set())
                for k in range(0, len(tidata[i][j])):
                    tilist[i][j].add(tidata[i][j][k])
                    if j == 1:
                        itemset.add(tidata[i][j][k])
        itemlist = self.buildInitItemList(itemset)
        return tilist, itemlist
    
    def buildInitItemList(self, itemset):
        i = 0
        itemlist = []
        for n in itemset: 
            itemlist.append([set([n])])  #structure: [0][{item}, support]
            itemlist[i].append(0) #all support starts at zero
            i += 1
        return itemlist
    
    def getDataFormattedItemList(self, data, itemlist):
        translationlist = []
        translationlist = copy.deepcopy(itemlist)
        for i in range(0, len(translationlist)):
            for j in range(0, len(translationlist[i])):
                if j == 0:
                    for k in range(0, len(translationlist[i][0])):
                        itemlocation = translationlist[i][0][k]
                        translationlist[i][0][k] = data[itemlocation][0]
                else:
                    attrlocation = translationlist[i][j]
                    translationlist[i][j] = data[0][attrlocation]
        return translationlist
        
    def buildNextItemList(self, itemlist):
        nextitemlist = []
        foundduplicate = False    
        k = 0
        for i in range(0, len(itemlist)):
            for j in range(i, len(itemlist)):
                if i != j:
                    for n in range(0, len(nextitemlist)):
                        if set(itemlist[i][0].union(itemlist[j][0])).intersection(nextitemlist[n][0]) == nextitemlist[n][0]:
                            foundduplicate = True
                    if foundduplicate == False:
                        nextitemlist.append([itemlist[i][0].union(itemlist[j][0])])
                        nextitemlist[k].append(0)
                        k+=1
                    foundduplicate = False
        return nextitemlist
                
    def filterSupport(self, minsupport, itemlist, soarlist):
        filtereditemlist = []
        for i in range(0, len(itemlist)):
            if itemlist[i][1] >= minsupport:
                filtereditemlist.append(itemlist[i])
                soarlist.append(itemlist[i])
        return filtereditemlist, soarlist
            
    def getSupport(self, tilist, itemlist):
        for i in range(0, len(tilist)):
            for j in range(0, len(itemlist)):
                if tilist[i][0].intersection(itemlist[j][0]) == itemlist[j][0]:
                    itemlist[j][1] += 1 / len(tilist) # converts support count to normalized percentage
        return itemlist
    
    def getSupportOnlyAssociationRules(self, minsupport, tidata):
        tilist, updateitemlist  = self.convertToTransactionsItems(tidata)
        soarlist = []
        while updateitemlist:
            updateitemlist = self.getSupport(tilist, updateitemlist)
            updateitemlist, soarlist = self.filterSupport(minsupport, updateitemlist, soarlist)
            updateitemlist = self.buildNextItemList(updateitemlist) 
        for i in range(0, len(soarlist)):
            soarlist[i][0] = list(soarlist[i][0]) #turns set of transactions into list of transactions
        return soarlist