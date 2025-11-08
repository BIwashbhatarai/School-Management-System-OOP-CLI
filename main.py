# main.py
# Fixed and hardened main CLI for SchoolManager
# - Non-recursive login loop
# - Graceful handling of KeyboardInterrupt/EOF during prompts
# - Consistent saves after data changes
# - Slight input validation hardening

from classes import SchoolManager
import sys
from hashlib import sha256
from colorama import Fore, Style, init
from getpass import getpass

init(autoreset=True)

# Initialize manager
manager = SchoolManager()
print(Fore.GREEN + " 🗂️ School Data Loaded Successfully!" + Style.RESET_ALL)

# Show initial alerts once
manager.show_dashboard_alerts()


# ------------------------ Helpers ------------------------
def hash_password(pwd):
    return sha256(pwd.encode()).hexdigest()


# ------------------------ Menus & Actions ------------------------
def admin_change_password(logged_admin):
    """
    Change password for the logged-in admin (logged_admin is a dict stored in manager.admins)
    """
    try:
        current = getpass("Enter current password: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n" + Fore.YELLOW + "Cancelled.")
        return

    if sha256(current.encode()).hexdigest() != logged_admin.get('password'):
        print(Fore.RED + "❌ Current password incorrect!")
        return

    try:
        new_pass = getpass("Enter new password: ").strip()
        if len(new_pass) < 4:
            print(Fore.RED + "❌ Password too short, must be at least 4 characters.")
            return
        confirm = getpass("Confirm the password: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n" + Fore.YELLOW + "Cancelled.")
        return

    if new_pass != confirm:
        print(Fore.RED + "❌ Passwords do not match.")
        return

    logged_admin['password'] = sha256(new_pass.encode()).hexdigest()
    manager.data_changed = True
    manager.save_data()
    print(Fore.GREEN + "✅ Password Updated Successfully!")


def admin_menu(logged_admin):
    while True:
        try:
            manager.show_dashboard_alerts()

            print("\n--- School Management System (Admin) ---\n")
            print("1. Add Student")
            print("2. List Students")
            print("3. Update Student")
            print("4. Delete Student")
            print("5. Search Students")
            print("6. Add Teacher")
            print("7. List Teachers")
            print("8. Update Teacher")
            print("9. Delete Teacher")
            print("10. Search Teachers")
            print("11. Manage Student Fee")
            print("12. Student Reports")
            print("13. Change Password")
            print("14. Mark Attendance")
            print("15. School Attendance Percentage")
            print("16. View Attendance")
            print("17. Low Attendance Report")
            print("18. Report Top Students")
            print("19. Report by Fee")
            print("20. Report by Class")
            print("21. Add Admin")
            print("22. List Admin")
            print("23. Delete Admin")
            print("24. Change Admin Role")
            print("25. Create Exam")
            print("26. List Exam")
            print("27. Dashboard Summary")
            print("28. Export Students to CSV")
            print("29. Import Students from CSV")
            print("30. Export Teachers to CSV")
            print("31. Import Teachers from CSV")
            print("32. Export Attendance to CSV")
            print("33. Import Attendance from CSV")
            print("34. Log Out")

            choice_str = manager.get_valid_choice('Enter your choice: ', list(range(1, 35)))
            try:
                choice = int(choice_str)
            except ValueError:
                print(Fore.RED + "❌ Invalid input. Please enter a number.")
                continue

            # Student related
            if choice == 1:
                manager.add_student()
                manager.save_data()
            elif choice == 2:
                manager.list_students()
            elif choice == 3:
                manager.update_student()
                manager.save_data()
            elif choice == 4:
                manager.delete_student()
                manager.save_data()
            elif choice == 5:
                manager.search_students()

            # Teacher related
            elif choice == 6:
                manager.add_teachers()
                manager.save_data()
            elif choice == 7:
                manager.list_teachers()
            elif choice == 8:
                manager.update_teachers()
                manager.save_data()
            elif choice == 9:
                manager.delete_teacher()
                manager.save_data()
            elif choice == 10:
                manager.search_teachers()

            # Fees, reports, attendance
            elif choice == 11:
                manager.manage_fee()
                manager.save_data()
            elif choice == 12:
                manager.student_report()
            elif choice == 13:
                admin_change_password(logged_admin)
            elif choice == 14:
                manager.mark_attendance()
                manager.save_data()
            elif choice == 15:
                manager.school_attendance_percentage()
            elif choice == 16:
                manager.view_attendance()
            elif choice == 17:
                threshold = input("Enter attendance threshold (default 75%): ").strip()
                try:
                    threshold = float(threshold) if threshold else 75.0
                except ValueError:
                    threshold = 75.0
                manager.low_attendance_report(threshold)
            elif choice == 18:
                manager.report_top_students()
            elif choice == 19:
                manager.report_by_fee()
            elif choice == 20:
                manager.report_by_class()

            # Admin management
            elif choice == 21:
                name = input("Name of new admin: ").strip()
                username = input("Username: ").strip()
                if not name or not username:
                    print(Fore.RED + "❌ Name and username are required.")
                    continue
                while True:
                    try:
                        password = getpass("Password: ").strip()
                        confirm_password = getpass("Confirm Password: ").strip()
                    except (KeyboardInterrupt, EOFError):
                        print("\n" + Fore.YELLOW + "Cancelled.")
                        password = None
                        break
                    if password == confirm_password:
                        break
                    print(Fore.RED + "❌ Passwords do not match. Please try again." + Style.RESET_ALL)
                if not password:
                    continue
                role = input("Role (admin/superadmin) [admin]: ").strip() or 'admin'
                manager.add_admin(name, username, password, role)
                # add_admin saves data internally
            elif choice == 22:
                manager.list_admins()
            elif choice == 23:
                username = input("Enter username of admin to delete: ").strip()
                if username:
                    manager.delete_admin(username)
                    # delete_admin already saves, but call save to be extra safe
                    manager.save_data()
            elif choice == 24:
                username = input("Enter username of admin to change role: ").strip()
                new_role = input("Enter new role (admin/superadmin): ").strip()
                if username and new_role:
                    manager.change_admin_role(username, new_role)
                    manager.save_data()

            # Exams
            elif choice == 25:
                manager.create_exam()
                manager.save_data()
            elif choice == 26:
                manager.list_exams()

            # Dashboard & exports/imports
            elif choice == 27:
                manager.quick_dashboard_stats()
            elif choice == 28:
                manager.export_students_csv()
            elif choice == 29:
                manager.import_students_csv()
                manager.save_data()
            elif choice == 30:
                manager.export_teachers_csv()
            elif choice == 31:
                manager.import_teachers_csv()
                manager.save_data()
            elif choice == 32:
                manager.export_attendance_csv()
            elif choice == 33:
                manager.import_attendance_csv()
                manager.save_data()
            elif choice == 34:
                print("Logging out...")
                break
            else:
                print(Fore.RED + "❌ Invalid choice, please select a valid option (1–34)." + Style.RESET_ALL)
        except KeyboardInterrupt:
            print("\n" + Fore.YELLOW + "Interrupted. Returning to main menu." + Style.RESET_ALL)
            break


def teacher_menu(teacher):
    while True:
        try:
            print(f"\n--- Teacher Portal ({teacher.name}) ---\n")
            print("1. View Students")
            print("2. Add/Update Student Marks")
            print("3. Change Password")
            print("4. Log Out")

            choice_str = manager.get_valid_choice('Enter your choice: ', [1, 2, 3, 4])
            try:
                choice = int(choice_str)
            except ValueError:
                print(Fore.RED + "❌ Invalid input. Please enter a number.")
                continue

            if choice == 1:
                manager.list_students()
            elif choice == 2:
                manager.manage_student_marks()
                manager.save_data()
            elif choice == 3:
                teacher.change_password(manager)
            elif choice == 4:
                print("Logging out...")
                break
            else:
                print(Fore.RED + '❌ Invalid choice' + Style.RESET_ALL)
        except KeyboardInterrupt:
            print("\n" + Fore.YELLOW + "Interrupted. Returning to main menu." + Style.RESET_ALL)
            break


def student_menu(student):
    while True:
        try:
            print(f"\n--- Student Portal ({student.name}) ---\n")
            print("1. View My Report")
            print("2. Change Password")
            print("3. Log Out")

            choice = input("Enter your choice (1-3): ").strip()
            if choice == '1':
                manager.view_student_report(student)
            elif choice == '2':
                student.change_password(manager)
            elif choice == '3':
                print("Logging out...")
                break
            else:
                print(Fore.RED + '❌ Invalid choice' + Style.RESET_ALL)
        except KeyboardInterrupt:
            print("\n" + Fore.YELLOW + "Interrupted. Returning to main menu." + Style.RESET_ALL)
            break


# ------------------------ Login ------------------------
def Login():
    """
    Non-recursive login loop. Returns after the user logs out (back to main menu).
    """
    try:
        while True:
            print("\n--- Login Portal ---\n1. Admin\n2. Teacher\n3. Student\n4. Back to Main")
            choice_str = manager.get_valid_choice('Enter your choice: ', [1, 2, 3, 4])
            try:
                choice = int(choice_str)
            except ValueError:
                print(Fore.RED + "❌ Invalid input. Please enter a number.")
                continue

            if choice == 1:
                username = input("Enter username: ").strip()
                try:
                    password = getpass("Enter password: ")
                except (KeyboardInterrupt, EOFError):
                    print("\n" + Fore.YELLOW + "Cancelled.")
                    continue
                admin_entry = next((a for a in manager.admins if a.get('username') == username), None)
                if admin_entry and sha256(password.encode()).hexdigest() == admin_entry.get('password'):
                    print("✅ Login Successful! Welcome, Admin.")
                    admin_menu(admin_entry)
                else:
                    print("❌ Invalid Credentials! Try again.")

            elif choice == 2:
                tid = input("Teacher ID: ").strip()
                try:
                    password = getpass("Enter password: ")
                except (KeyboardInterrupt, EOFError):
                    print("\n" + Fore.YELLOW + "Cancelled.")
                    continue
                teacher = next((t for t in manager.teachers if t.get_teacher_id() == tid), None)
                if teacher and hash_password(password) == teacher.password:
                    teacher_menu(teacher)
                else:
                    print("❌ Invalid Credentials! Try again.")

            elif choice == 3:
                sid = input("Student ID: ").strip()
                try:
                    password = getpass("Enter password: ")
                except (KeyboardInterrupt, EOFError):
                    print("\n" + Fore.YELLOW + "Cancelled.")
                    continue
                student = next((s for s in manager.students if s.get_student_id() == sid), None)
                if student and hash_password(password) == student.password:
                    student_menu(student)
                else:
                    print("❌ Invalid Credentials! Try again.")

            elif choice == 4:
                # Back to main menu
                break
            else:
                print("❌ Invalid choice. Returning to login menu.")
    except KeyboardInterrupt:
        print("\n" + Fore.YELLOW + "Interrupted. Returning to main menu." + Style.RESET_ALL)
        return


# ------------------------ Main Loop ------------------------
if __name__ == '__main__':
    try:
        while True:
            print("\n--- SCHOOL MANAGEMENT SYSTEM ---\n")
            print("1. Login")
            print("2. Exit")

            choice_str = manager.get_valid_choice('Enter your choice: ', [1, 2])
            try:
                choice = int(choice_str)
            except ValueError:
                print(Fore.RED + "❌ Invalid input. Please enter 1 or 2." + Style.RESET_ALL)
                continue

            if choice == 1:
                Login()
            elif choice == 2:
                print("Exiting program. Goodbye!")
                if manager.data_changed:
                    try:
                        manager.backup_data()
                    except Exception:
                        pass
                    manager.save_data()
                break
            else:
                print(Fore.RED + "❌ Invalid choice. Please enter 1 or 2." + Style.RESET_ALL)

    except KeyboardInterrupt:
        print("\n" + Fore.YELLOW + "Keyboard interrupt received. Saving data (if changed) and exiting..." + Style.RESET_ALL)
        try:
            if manager.data_changed:
                try:
                    manager.backup_data()
                except Exception:
                    pass
                manager.save_data()
        except Exception as e:
            print(Fore.RED + f"❌ Error while saving on exit: {e}")
        sys.exit(0)