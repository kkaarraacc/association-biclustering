import BiMax
import Apriori
import numpy as np

#####################
minsupport = .08    # CONTROLS FOR WINE RESULTS -- lower support will find more clusters  (default is .08) (test is .05)
minconfidence = .2  # CONTROLS FOR ATTRIBUTES RESULTS -- lower confidence will find more attributes within each cluster  (default is .2) (test is .1)
#####################
       
def getData(datatextfilename):
    winedata = list(np.genfromtxt(datatextfilename, dtype=object , delimiter='|'))
    for i in range(0, len(winedata)):
        for j in range(0, len(winedata[i])):
            if i == 0 or j == 0:
                winedata[i][j] = str(winedata[i][j])
            else:
                winedata[i][j] = int(winedata[i][j])
    return winedata
    
def getBiclusters(winedata):
    bimax =  BiMax.BiMax(winedata)
    bimax.findBiclusters()
    bimax.getDataFormattedBiclusters()
    return bimax
    
def getSupport(minsupport, processbiclusters, winedata):
    print('...', end='')
    tidata = processbiclusters
    apriori = Apriori.Apriori()
    itemlist = apriori.getSupportOnlyAssociationRules(minsupport, tidata)
    #formattedlist = apriori.getDataFormattedItemList(winedata, itemlist) #there's a problem with the formatted list(problem is that winedata does not carry the same format as the testdata format)
    formattedlist = []
    return apriori, itemlist, formattedlist

def stampClusterResults(stamp, processbiclusterlist):
    for i in range(0, len(processbiclusterlist)):
        processbiclusterlist[i].append(stamp)
    return processbiclusterlist
    
def appendStampedList(listbig, listsmall):
    for i in range(0, len(listsmall)):
        listbig.append(listsmall[i])
    return listbig
    
def getMaximalItemList(itemlist):
    max = 0
    newitemlist = []
    for i in range(0,len(itemlist)):
        if len(itemlist[i][0]) > max:
            max = len(itemlist[i][0])
    print('...', end='')
    for i in range(0,len(itemlist)):
        if len(itemlist[i][0]) == max:
            newitemlist.append(itemlist[i])
    print('...', end='')
    return newitemlist

def buildAssocationList(maximallist, stampedlist, minconfidence):
    setuplist = []
    organizedlist = []
    associationlist = []
    #build setuplist    
    for i in range(0, len(stampedlist)):
        for j in range(0, len(maximallist)):
            if set(maximallist[j][0]).issubset(set(stampedlist[i][0])):
                setuplist.append([list(set(maximallist[j][0]) & set(stampedlist[i][0])), stampedlist[i][1], stampedlist[i][2]])
    print('...', end='')
    #organize list
    for i in range(0, len(maximallist)):
        organizedlist.append([maximallist[i][0], set(), 0])    #[[wines], [attributes], [appearance count]]
        for j in range(0, len(setuplist)):
            if set(organizedlist[i][0]).issubset(set(setuplist[j][0])):
                organizedlist[i][1] |= set(organizedlist[i][1] ^ set(setuplist[j][1]))
                organizedlist[i][2] += 1    #appearance count increases by one everytime it appears in the list
    print('...', end='')
                #convert attribute sets to atrribute list of lists which contains each attribute and its count
    for i in range(0, len(organizedlist)):
        organizedlist[i][1] = list(organizedlist[i][1])
        for j in range(0, len(organizedlist[i][1])):
            organizedlist[i][1][j] = list([organizedlist[i][1][j], 0]) #[[w1, w2], [[a1, count], [a2, count]]]
    print('...', end='')
            #get attribute counts    <-----this is very inefficient but for now it's going to have to do
    for i in range(0, len(organizedlist)):
        for j in range(0, len(organizedlist[i][1])):
            for k in range(0, len(stampedlist)):
                if set([organizedlist[i][1][j][0]]).issubset(set(stampedlist[k][1])) and set(organizedlist[i][0]).issubset(set(stampedlist[k][0])):
                    organizedlist[i][1][j][1] += 1
    print('...', end='')
                    #filter by minsupport and build final association list
    for i in range(0, len(organizedlist)):
        associationlist.append([organizedlist[i][0], []])
        for j in range(0, len(organizedlist[i][1])):
            confidence = organizedlist[i][1][j][1] / organizedlist[i][2]
            if confidence  >= minconfidence:
                organizedlist[i][1][j][1] = confidence
                associationlist[i][1].append(organizedlist[i][1][j])  
    return associationlist

def getAssociationBiclusters(associationlist, stampedlist):
    yearsets = []
    setuplist = []
    associationbiclusters = []
    #formatlist <--- [[wines], [attributes]]
    for i in range(0, len(associationlist)):
        setuplist.append([associationlist[i][0], []])
        for j in range(0, len(associationlist[i][1])):
            setuplist[i][1].append(associationlist[i][1][j][0])
    print('...', end='')
            #find which years are associated with the attributes
    for i in range(0, len(setuplist)):     #this is also a bad implementation, could generate a year setlist earlier
        yearsets.append([setuplist[i][0], set()])
        for j in range (0, len(setuplist[i][1])):
            for k in range (0, len(stampedlist)):
                if set([setuplist[i][1][j]]).issubset(set(stampedlist[k][1])) and set(setuplist[i][0]).issubset(set(stampedlist[k][0])):
                    yearsets[i][1] |= set([stampedlist[k][2]])
    print('...', end='')
                    #make associationblicslusters
    for i in range(0, len(yearsets)):
        yearsets[i][1] = list(yearsets[i][1])
    print('...', end='')
    for i in range(0, len(yearsets)):
        associationbiclusters.append([yearsets[i][0], []])
        for j in range(0, len(yearsets[i][1])):
            associationbiclusters[i][1].append([yearsets[i][1][j], set()])
        for j in range(0, len(associationbiclusters[i][1])):
            for k in range(0, len(setuplist[i][1])):
                for l in range(0, len(stampedlist)):
                    if set([setuplist[i][1][k]]).issubset(set(stampedlist[l][1])) and set([associationbiclusters[i][1][j][0]]).issubset(set([stampedlist[l][2]])):
                        associationbiclusters[i][1][j][1] |= set([setuplist[i][1][k]])      
    print('...', end='')
    return associationbiclusters
    #find which attributes are active during those years
    
#format text files
winedata2010 = getData('wine2010.txt')
winedata2009 = getData('wine2009.txt')
winedata2008 = getData('wine2008.txt')
winedata2007 = getData('wine2007.txt')
winedata2006 = getData('wine2006.txt')

#get bliclusters
print('2010:')
bimax2010 = getBiclusters(winedata2010)
print('')
print('2009:')
bimax2009 = getBiclusters(winedata2009)
print('')
print('2008:')
bimax2008 = getBiclusters(winedata2008)
print('')
print('2007:')
bimax2007 = getBiclusters(winedata2007)
print('')
print('2006:')
bimax2006 = getBiclusters(winedata2006)

#stamp cluster lists with the years
stamped2010 = stampClusterResults('2010', bimax2010.processbiclusters)
stamped2009 = stampClusterResults('2009', bimax2009.processbiclusters)
stamped2008 = stampClusterResults('2008', bimax2008.processbiclusters)
stamped2007 = stampClusterResults('2007', bimax2007.processbiclusters)
stamped2006 = stampClusterResults('2006', bimax2006.processbiclusters)

#combine all stamped lists into one
stampedlist = []
stampedlist = appendStampedList(stampedlist, stamped2010)
stampedlist = appendStampedList(stampedlist, stamped2009)
stampedlist = appendStampedList(stampedlist, stamped2008)
stampedlist = appendStampedList(stampedlist, stamped2007)
stampedlist = appendStampedList(stampedlist, stamped2006)
print('\n' + 'Time stamps applied and lists combined')
print('Full list size: ' + str(len(stampedlist)))

print('\n' + 'Applying support with a minimum of ' + str(minsupport) + '...', end='')

apriorilist, itemlist, formattedlist = getSupport(minsupport, stampedlist, winedata2010)
maximalitemlist = getMaximalItemList(itemlist)
print('\n' + 'Found ' + str(len(itemlist)) + ' items')
print('of which, ' + str(len(maximalitemlist)) + ' are maximal with a size of ' + str(len(maximalitemlist[0][0])))

print('\n' + 'Finding Association Biclusters with a minimum support of ' + str(minsupport) + ' and a minimum confidence of ' + str(minconfidence) + '...', end = '')

associationlist = buildAssocationList(maximalitemlist, stampedlist, minconfidence)
associationbiclusters = getAssociationBiclusters(associationlist, stampedlist)

#================hacky stuff starts here

def getStampedYearList(stampedlist, year):
    stampedyearlist = []
    for i in range(len(stampedlist)):
        if stampedlist[i][2] == year:
            stampedyearlist.append(stampedlist[i])
    return stampedyearlist
    


#divide stamped list into years
stampedlist2006 = getStampedYearList(stampedlist, '2006')
stampedlist2007 = getStampedYearList(stampedlist, '2007')
stampedlist2008 = getStampedYearList(stampedlist, '2008')
stampedlist2009 = getStampedYearList(stampedlist, '2009')
stampedlist2010 = getStampedYearList(stampedlist, '2010')

associationlist2006 = buildAssocationList(maximalitemlist, stampedlist2006, minconfidence)
associationlist2007 = buildAssocationList(maximalitemlist, stampedlist2007, minconfidence)
associationlist2008 = buildAssocationList(maximalitemlist, stampedlist2008, minconfidence)
associationlist2009 = buildAssocationList(maximalitemlist, stampedlist2009, minconfidence)
associationlist2010 = buildAssocationList(maximalitemlist, stampedlist2010, minconfidence)

associationlist = [associationlist2006, associationlist2007, associationlist2008,associationlist2009,associationlist2010]
print('...')

#=========organizing final association list for spreadsheet

winesets = []

for i in range(len(associationlist[0])):
    winesets.append(set())

for i in range(len(associationlist)):
    for j in range(len(associationlist[i])):
        for k in range(len(associationlist[i][j][1])):
            winesets[j].add(associationlist[i][j][1][k][0])  #creates sets of attributes for each ordered wineset

for i in range(len(winesets)):   #convert set to list
    winesets[i] = list(winesets[i])
    
# get wine names
winenames = []

for i in range(len(associationlist[0])):
    winenames.append([])
    for j in range(len(associationlist[0][i][0])):
        location = associationlist[0][i][0][j]
        winenames[i].append(winedata2010[location][0])
        
# get attribute names
attributenames = []

for i in range(len(winesets)):
    attributenames.append([])
    for j in range(len(winesets[i])):
        attributenames[i].append(winedata2010[0][winesets[i][j]])
        
# yearlist
yearlist = ['2006', '2007', '2008', '2009', '2010']
        
# build file

filename = 'test.txt'

file = open(filename,'w') 

for i in range(len(winenames)):
    # write wine names
    for j in range(len(winenames[i])):
        file.write(winenames[i][j] + '\n')
    # write attribute names
    file.write('\n\n\t')
    for j in range(len(attributenames[i])):
        file.write(attributenames[i][j] + '\t')
    file.write('\n\n')
    # write year
    for j in range(len(associationlist)):
        file.write(yearlist[j] + '\t')
        # match attributes
        for k in range(len(winesets[i])):
            for l in range(len(associationlist[j][i][1])): # for each attribute found in that year
                if not set([winesets[i][k]]).isdisjoint(set(associationlist[j][i][1][l])):
                    file.write('X')
            file.write('\t')
        file.write('\n')
    file.write('\n\n\n')
file.close() 

print('\n' + 'Done! Results created as file "' + filename + '"')