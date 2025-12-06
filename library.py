import mysql.connector

# Establish database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="stark0007",
    database="library"
)
cursor = conn.cursor()

# CHANGE 1: Create tables if they don't exist
# WHY: Ensures the database schema is ready before operations
# WHAT: Creates two tables - one for libraries and one for books
cursor.execute("""
    CREATE TABLE IF NOT EXISTS library1 (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL UNIQUE
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INT AUTO_INCREMENT PRIMARY KEY,
        library_id INT,
        book_name VARCHAR(255) NOT NULL,
        FOREIGN KEY (library_id) REFERENCES library1(id) ON DELETE CASCADE
    )
""")
conn.commit()

class Library:
    # CHANGE 2: Modified __init__ to properly handle database operations
    # WHY: Original code had bugs (missing self.name, no commit, wrong parameter format)
    # WHAT: Now properly inserts library, retrieves its ID, and loads existing books
    def __init__(self, name):
        self.name = name
        self.library_id = None
        
        # Check if library already exists
        cursor.execute("SELECT id FROM library1 WHERE name = %s", (self.name,))
        result = cursor.fetchone()
        
        if result:
            # Library exists, load it
            self.library_id = result[0]
            print(f"Library '{self.name}' loaded from database.")
        else:
            # Create new library
            query = "INSERT INTO library1 (name) VALUES (%s)"
            cursor.execute(query, (self.name,))  # Fixed: Added comma to make it a tuple
            conn.commit()
            self.library_id = cursor.lastrowid  # Get the auto-generated ID
            print(f"Library '{self.name}' created successfully.")
        
        # Load books from database
        self.load_books()
    
    # CHANGE 3: New method to load books from database (READ operation)
    # WHY: To sync in-memory data with database on initialization
    # WHAT: Fetches all books for this library from the books table
    def load_books(self):
        """Load all books for this library from the database"""
        cursor.execute("SELECT book_name FROM books WHERE library_id = %s", (self.library_id,))
        self.books = [row[0] for row in cursor.fetchall()]
        self.number_of_books = len(self.books)
    
    # CHANGE 4: Enhanced info method to read from database
    # WHY: Original code had a bug (j wasn't incrementing properly)
    # WHAT: Displays library info with corrected enumeration
    def info(self):
        """Display library information (READ operation)"""
        self.load_books()
        
        print(f"\n{'='*50}")
        print(f"Library Name: {self.name}")
        print(f"{'='*50}")
        print("Books in library:")
        
        if not self.books:
            print("  No books available")
        else:
            for j, book in enumerate(self.books, 1): 
                print(f"  {j}. {book}")
        
        print(f"\nTotal number of books: {self.number_of_books}")
        print(f"{'='*50}\n")
    
    # CHANGE 5: Method remains similar but uses updated book count
    # WHY: To verify data integrity between stored count and actual books
    # WHAT: Compares number_of_books with actual book list length
    def allgood(self):
        """Check if the book count matches the actual number of books"""
        self.load_books()  # Refresh from database
        if self.number_of_books == len(self.books):
            print("✓ All good! Book count matches.")
        else:
            print("✗ Warning: Book count mismatch detected.")
    
    # CHANGE 6: Enhanced AddBooks method with database INSERT
    # WHY: Original code only stored in memory, changes were lost on restart
    # WHAT: Now inserts each book into the database and commits changes
    def AddBooks(self):
        """Add books to the library (CREATE operation)"""
        print("\nHow many books do you want to add?")
        try:
            adding_books = int(input("Enter number: "))
            
            if adding_books <= 0:
                print("Please enter a positive number.")
                return
            
            print(f"Enter {adding_books} book name(s):")
            for i in range(adding_books):
                book_name = input(f"Book {i+1}: ").strip()
                
                if not book_name:
                    print("Book name cannot be empty. Skipping.")
                    continue
                
                
                query = "INSERT INTO books (library_id, book_name) VALUES (%s, %s)"
                cursor.execute(query, (self.library_id, book_name))
                conn.commit()
                
                
                self.books.append(book_name)
                self.number_of_books += 1
            
            print(f"✓ Successfully added {adding_books} book(s).")
        
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    # CHANGE 7: New method for DELETE operation
    # WHY: Original code had no way to remove books
    # WHAT: Allows users to delete books by name or ID from database
    def DeleteBooks(self):
        """Delete books from the library (DELETE operation)"""
        self.load_books()
        
        if not self.books:
            print("No books to delete.")
            return
        
        print("\nCurrent books:")
        for j, book in enumerate(self.books, 1):
            print(f"  {j}. {book}")
        
        print("\nEnter the number of the book to delete (or 0 to cancel):")
        try:
            choice = int(input("Choice: "))
            
            if choice == 0:
                print("Delete operation cancelled.")
                return
            
            if 1 <= choice <= len(self.books):
                book_to_delete = self.books[choice - 1]
                
                # Delete from database
                query = "DELETE FROM books WHERE library_id = %s AND book_name = %s LIMIT 1"
                cursor.execute(query, (self.library_id, book_to_delete))
                conn.commit()
                
                print(f"✓ Book '{book_to_delete}' deleted successfully.")
                
                # Refresh from database
                self.load_books()
            else:
                print("Invalid choice.")
        
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    # CHANGE 8: New method for SEARCH operation
    # WHY: Users need to find specific books in large libraries
    # WHAT: Searches for books by partial name match in database
    def SearchBooks(self):
        """Search for books in the library (SEARCH operation)"""
        print("\nEnter search term:")
        search_term = input("Search: ").strip()
        
        if not search_term:
            print("Search term cannot be empty.")
            return
        
        
        query = """
            SELECT book_name FROM books 
            WHERE library_id = %s AND book_name LIKE %s
        """
        cursor.execute(query, (self.library_id, f"%{search_term}%"))
        results = cursor.fetchall()
        
        if results:
            print(f"\nFound {len(results)} book(s) matching '{search_term}':")
            for j, (book,) in enumerate(results, 1):
                print(f"  {j}. {book}")
        else:
            print(f"No books found matching '{search_term}'.")
    
    # CHANGE 9: New method for UPDATE operation
    # WHY: Users need to correct book names or update information
    # WHAT: Allows editing book names in the database
    def UpdateBook(self):
        """Update a book name (UPDATE operation)"""
        self.load_books()
        
        if not self.books:
            print("No books to update.")
            return
        
        print("\nCurrent books:")
        for j, book in enumerate(self.books, 1):
            print(f"  {j}. {book}")
        
        print("\nEnter the number of the book to update (or 0 to cancel):")
        try:
            choice = int(input("Choice: "))
            
            if choice == 0:
                print("Update operation cancelled.")
                return
            
            if 1 <= choice <= len(self.books):
                old_name = self.books[choice - 1]
                print(f"Current name: {old_name}")
                print("Enter new name:")
                new_name = input("New name: ").strip()
                
                if not new_name:
                    print("Book name cannot be empty.")
                    return
                
                # Update in database
                query = """
                    UPDATE books 
                    SET book_name = %s 
                    WHERE library_id = %s AND book_name = %s 
                    LIMIT 1
                """
                cursor.execute(query, (new_name, self.library_id, old_name))
                conn.commit()
                
                print(f"✓ Book updated from '{old_name}' to '{new_name}'.")
                
                # Refresh from database
                self.load_books()
            else:
                print("Invalid choice.")
        
        except ValueError:
            print("Invalid input. Please enter a number.")


# CHANGE 10: Enhanced main program with better menu and error handling
# WHY: Original menu was limited and had no way to exit gracefully
# WHAT: Added more options (delete, search, update) and improved user experience

print("="*50)
print("LIBRARY MANAGEMENT SYSTEM")
print("="*50)
print("\nEnter the name of the library:")
library_name = input("Library name: ").strip()

if not library_name:
    print("Library name cannot be empty. Exiting.")
    cursor.close()
    conn.close()
    exit()

# Create or load library
lib = Library(library_name)

# Main menu loop
while True:
    print("\n" + "="*50)
    print("MAIN MENU")
    print("="*50)
    print("1. Display library information (READ)")
    print("2. Check data integrity")
    print("3. Add books (CREATE)")
    print("4. Delete books (DELETE)")
    print("5. Search books (SEARCH)")
    print("6. Update book name (UPDATE)")
    print("7. Exit")
    print("="*50)
    
    try:
        user_choice = int(input("Enter your choice: "))
        
        if user_choice == 1:
            lib.info()
        elif user_choice == 2:
            lib.allgood()
        elif user_choice == 3:
            lib.AddBooks()
        elif user_choice == 4:
            lib.DeleteBooks()
        elif user_choice == 5:
            lib.SearchBooks()
        elif user_choice == 6:
            lib.UpdateBook()
        elif user_choice == 7:
            print("\nThank you for using the Library Management System!")
            break
        else:
            print("Invalid choice. Please enter a number between 1-7.")
    
    except ValueError:
        print("Invalid input. Please enter a number.")
    except Exception as e:
        print(f"An error occurred: {e}")

# CHANGE 11: Proper cleanup of database connection
# WHY: Important to close database connections to prevent resource leaks
# WHAT: Closes cursor and connection when program exits
cursor.close()
conn.close()
print("Database connection closed. Goodbye!")
