#NAME: FDD_PART_FUNCTIONS AND MODULES IMPLEMENTATION
#DATE CREATED: 15/11/2014

""" This is class implementation for cleaning Dr.Colby FDD dataset
and assigning numeric codes to all the letters in the file.
readCSV function reads the FDD data into a list 'r'
headingRow function removes the first row from the FDD input file
cleanCSV function removes rows with any blank spaces.
convertLettersToNumbers assigns numeric values to the letters . 
 
""" 
import csv
import re

class SVMInputData:
    def __init__(self, fileName):
        self.fileName = fileName
        self.rows = self.readCSV()
        self.cleanedData = self.cleanCSV()
    def readCSV(self):
        r = csv.reader(open(self.fileName)) 
        rows=[]
        for row in r:
            rows.append(row)
        #print rows
        #cleanedDataSet = self.clean_csv(self.rows)
        return rows # list 'rows' contains the data from Dr.Colby file 
    def headingRow(self):
        headingRow = zip(*[iter(self.rows[0])]*20)
        return headingRow 
        
    def cleanCSV(self):
        """looping through the nested list and deletes any rows with
           empty spaces.
        """
        n=0
        while n < len(self.rows):
            for row in self.rows:
                for x in row:
                    if x == "":
                        self.rows.pop(n)
                n +=1
        return self.rows
    
    def isUpper(self, x):
        try:
            x.upper()
        except ValueError:
            print "Special characters found"
    
    def convertLettersToNumbers(self):
        """This function converts all the letters in the CSV file to numeric codes.
           An empty list called mod_rows is created. 
           A dictionary is created with unique numbering for all the letters in the
           file. Using a regular expression, data with matched pattern is extracted.
           The letter is replaced with a corresponding value from the dictionary.
           Rows without a matched pattern is appended to the Modified Rows list.
        
        PRECONDITIONS: Clean_csv function returns a nested list, which is used as 
                       an input argument for this function.
                    
        POSTCONDITIONS: It returns a List with all the letters replaced with 
                        numeric values. If the data is a character it gets the
                        value from dictionary,else it appends directly to the 
                        list. 
        SIDEEFFECTS:     None
        ERRORCONDITIONS: None
        
        MODIFICATION HISTORY:
        >  November 15 , 2014
            Manojna
             Created initial version of function.
        > December 5 , 2014
            Manojna
           Modified to classes version
         """
        self.mod_rows = []
        
        dictionary = {'Y':2,'N':1,'M':2,'F':1,'W':1,'B':2,'A':3,'H':4,'C':{'col_G':1,'col_P':0},'P':0,'S':2,'PE':3,'M':2,'V':1,'L':1,'SL':3,'G':4,'SG':5,'SF':3,'DS':5,'D':4,'T':1,'N':1,'R':2,'MO':0,'MI':1}        
        pattern = re.compile('[A-Z]')
        #cleaned_data_set = self.readCSV( )
        for rows in self.cleanedData[1:]:
            for element in rows:
                match = re.match(pattern, element)
                if match is None:
                    #print match.group()
                    self.mod_rows.append(element)
                elif match is not None:
                    if match.group() == 'C' and len(rows) != 16:
                        col_GC = dictionary.get(element, 0)
                        #print col_GC
                        self.mod_rows.append(col_GC.get('col_G', 0))
                    elif match.group() == 'C' and len(rows) == 16:
                        col_PC = dictionary.get(element,0)
                        print col_PC
                        self.mod_rows.append(col_GC.get('col_P', 0))
                    else:
                        self.mod_rows.append(dictionary.get(element, 0))
        mod_rows = zip(*[iter(self.mod_rows)]*20)
        return mod_rows
                        
svm_data = SVMInputData("final_data.CSV")
dataWithoutHeader = svm_data.convertLettersToNumbers()
header = svm_data.headingRow()
#print dataWithoutHeader

#print header

#Writing the modified FDD data into a new output CSV file.

with open("FDD_DATA_SET_OUT.csv", "wb") as fp:
    w = csv.writer(fp)
    w.writerows(header)    
    w.writerows(dataWithoutHeader)