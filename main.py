from classes import SchoolManager

def main():
    manager = SchoolManager()
    
    while True:
        print("\n School Management System. \n")
        print("\n1. Add Student")
        print("2. List Student")
        print("3. Update Student")
        print("4. Delete Student")
        print("5. Exit")
        
        choice = input("Enter your choice (1-5): ")
        
        if choice == '1':
            manager.add_student()
        elif choice == '2':
            manager.list_students()
        elif choice == '3':
            manager.update_student()
        elif choice == '4':
            manager.delete_student()
        elif choice == '5':
            print("Exiting Bye-Bye👋")
            break
        else:
            print("Invalid choice, Please choose a number between 1-5")
            
if __name__ == "__main__":
    main()