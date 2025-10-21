from classes import SchoolManager, Admin
import sys
from hashlib import sha256

manager = SchoolManager()
manager.load_data()

admin = Admin(
    name="Super Admin", 
    contact_info={"Phone": "0000000000", "Email": "admin@example.com"}, 
    admin_id="ADM001"
)
def admin_menu():
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
        print("9. Manage Student Fee")
        print("10. Student Reports")
        print("11. Change Password")
        print("12. Log Out")

        choice = input("Enter your choice (1-12): ")
        
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
            manager.manage_fee()
        elif choice == '10':
            manager.student_report()
        elif choice == '11':
            admin.change_password()
            manager.save_data()
        elif choice == '12':
            print("Logging out...")
            break
        else:
            print("Invalid choice, Try again!")

def teacher_menu(teacher):
    while True:
        print(f"\n---Teacher Portal ({teacher.name})---\n")   
        print("1. View Students.")
        print("2. Add/Update Student Marks")
        print("3. Change Password")
        print("4. Log Out.")
        
        choice = input("Enter your choice (1-4): ")
        
        if choice =='1':
            manager.list_students()
        elif choice == '2':
            manager.manage_student_marks()
            manager.save_data()
        elif choice =='3':
            teacher.change_password()
            manager.save_data()
        elif choice =='4':
            break
        else:
            print('Invalid choice')
            

def Student_menu(student):
    while True:
        print(f"\n---Student Portal ({student.name})---\n")   
        print("1. View My Report.")
        print("2. Change Password.")
        print("3. Log Out.")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice =='1':
            manager.view_student_report(student)
        elif choice == '2':
            student.change_password()
            manager.save_data()
        elif choice =='3':
            print("Logging out...")
            break
        else:
            print('Invalid choice')
def Login():
    print("\n---Login Portal---\n1. Admin\n2. Teacher\n3. Student")
    choice = input("Enter your choice (1-3): ")
    
    if choice == '1':
        username = input("Enter username: ")
        password = input("Enter password: ")
        if admin.authenticate(username,password):
            print("✅ Login Successful! Welcome, Admin.")
            admin_menu()
        else:
            print("❌ Invalid Credentials!")
            sys.exit()
    elif choice == '2':
        tid = input("Teacher Id: ")
        password = input("Password: ")
        
        teacher = next((t for t in manager.teachers if t.get_teacher_id() == tid), None)
        if teacher and sha256(password.encode()).hexdigest() == teacher.password:
            teacher_menu(teacher)
        else:
            print("Invalid Credentials.")
    elif choice == '3':
        sid = input("Student ID: ")
        password = input("Password: ")
        
        student = next((s for s in manager.students if s.get_student_id() == sid), None)
        
        if student and sha256(password.encode()).hexdigest() == student.password:
            Student_menu(student)
        else:
            print("Invalid Credentials.")
    else:
        print("Invalid choice. Exiting...")
        sys.exit()

if __name__ == '__main__':
    while True:
        print("\n--- SCHOOL MANAGEMENT SYSTEM ---\n")
        print("1. Login")
        print("2. Exit")
        
        main_choice = input("Enter Choice: ")
        
        if main_choice == '1':
            Login()
        elif main_choice == 2:
            print("Exiting program. Goodbye!")
            manager.backup_data()
            manager.save_data()
            break
        else:
            print("❌ Invalid choice, Try again.")