class library:
    def __init__(self,name):
                self.name = name

    books = ["CProgramming","Python","Java","DataScience","MachineLearning"]
    number_of_books = 5

    def info(self):
        print(f"name of library:{self.name}")
        print(f"books = ")
        for i in self.books:
            j =1
            print(f"{j}:{i}")
            j+1
        print(f"number of books = {self.number_of_books}")

    def allgood(self):
        if(self.number_of_books == len(self.books)):
            print("all good!!")
        else: 
            print("big problem")
    
    def AddBooks(self):
        print("how many books do you wanna add ??")
        Addingbooks = int(input())
        self.number_of_books = Addingbooks+self.number_of_books
        for i in range (Addingbooks):
            input_ = input()
            self.books.append(input_)

print("0. enter the name of the library")
name = input()
name = library(name)

while(1):


    print("1.To print information of books")
    print("2.To Check if All Books are there in library")
    print("3.To Add more books to the library")
    print("4.To exit out of REPL")

    usrneed = int(input())

    if(usrneed == 1):
        name.info()
    elif(usrneed == 2):
        name.allgood()
    elif(usrneed == 3):
        name.AddBooks()
    elif(usrneed == 4):
        break
    else:
         print("Invalid output")