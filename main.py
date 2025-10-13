from classes import SchoolManager

def main():
    manager = SchoolManager()
    manager.load_data()
    
    while True:
        print("\n--- School Management System ---\n")
        print("1. Add Student")
        print("2. List Students")
        print("3. Update Student")
        print("4. Delete Student")
        print("5. Add Teacher")
        print("6. List Teachers")
        print("7. Update Teacher")
        print("8. Delete Teacher")
        print("9. Exit")

        choice = input("Enter your choice (1-9): ")
        
        if choice == '1':
            manager.add_student()
            manager.save_data()
        elif choice == '2':
            manager.list_students()
        elif choice == '3':
            manager.update_student()
            manager.save_data()
        elif choice == '4':
            manager.delete_student()
            manager.save_data()
        elif choice == '5':
            manager.add_teachers()
            manager.save_data()
        elif choice == '6':
            manager.list_teachers()
        elif choice == '7':
            manager.update_teachers()
            manager.save_data()
        elif choice == '8':
            manager.delete_teacher()
            manager.save_data()
        elif choice == '9':
            print("Exiting. Bye-Bye 👋")
            break
        else:
            print("Invalid choice, Please choose a number between 1-9")

if __name__ == "__main__":
    main()
