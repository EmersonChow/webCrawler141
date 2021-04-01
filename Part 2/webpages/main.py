from basic_query import basicQuery
from index_constructor import Index_Constructor

if __name__ == "__main__":

    done = False
    while (not done):
        firstInput = input("Create Index? (Y/N). Type (Done) to Exit")
        if firstInput == "Y": 
            x = Index_Constructor()
            x.insertIntoIndex()
            x.create_json()
            print(x.getNumDoc())
            print(x.getNumUnqiueWords())
        elif firstInput == "N":
            qDone = False
            while not qDone:
                myInput = input("Insert Query: ")
                numDocReturn = input("How many results? ")
                myQuery = basicQuery(myInput)
                myQuery.getResults(numDocReturn)
                exitting = input("Type (Done) to exit")
                if exitting == "Done":
                    qDone = True
        elif firstInput == "Done":
            done = True


