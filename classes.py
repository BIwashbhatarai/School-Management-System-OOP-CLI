import json
import os
from datetime import datetime
from hashlib import sha256
import re
from colorama import Fore, Style, init
init(autoreset=True)

from tabulate import tabulate


def print_section(title, color=Fore.CYAN):
    print("\n" + color + "-"*60)
    print(color + f"{title.center(60)}")
    print(color + "-"*60 + Style.RESET_ALL)


def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool (re.match(pattern,email))

def is_valid_phone(phone):
    return phone.isdigit() and len(phone)== 10

def is_valid_class_section(cls):
    return bool (re.match(r'^[A-Za-z0-9]+$', cls))

class Person:
    def __init__(self, name, contact_info, role='Person'):
        self.name = name
        self.role = role
        self.contact_info = contact_info
    
    def update_contact(self, new_contact):
        self.contact_info = new_contact
        
    def __str__(self):
        return f" {self.role}: {self.name}, Contact: {self.contact_info}"
    
    def to_dict(self):
        return {
            "name": self.name,
            "contact": self.contact_info,
            "role": self.role
        }
class Student(Person):
    def __init__(self, name , contact_info, student_id):
        super().__init__( name, contact_info, role='Student')
        self.__student_id = student_id
        self.marks = {}
        self.fee_status = 'Pending'
        self.class_section = "N/A"
        self.password = sha256('4321'.encode()).hexdigest()

    def add_update_marks(self, subject ,  mark):
        self.marks[subject] = mark
        print(f"Marks updated for {self.name} - {subject}: {mark}")
    
    def calculate_grade(self):
        if not self.marks:
            return None
        Avg = sum(self.marks.values()) / len(self.marks)
        
        if Avg >= 90:
            return "A+"
        elif Avg >= 80:
            return "A"
        elif Avg >= 70:
            return "B+"
        elif Avg >= 60:
            return "B"
        elif Avg >= 50:
            return "C"
        else:
            return "F"
    
    def pay_fee(self):
        self.fee_status = "Paid"
        print((Fore.GREEN)+ f"✅ {self.name} fee status updated to paid.")
    
    def to_dict(self):
        base = super().to_dict()
        base.update({
            "student_id": self.__student_id,
            "marks": self.marks,
            "fee_status": self.fee_status,
            "class_section": self.class_section,
            'password': self.password
        })
        return base
    def get_student_id(self):
        return self.__student_id
    def set_student_id(self, new_id):
        self.__student_id = new_id
    def __str__(self):
        base_info = super().__str__()
        grade = self.calculate_grade()
        return f"{base_info}, Student ID: {self.__student_id}, Fee: {self.fee_status}, Marks: {self.marks}, Grade: {grade if grade else 'N/A'}"
    
    def change_password(self):
        current = input("Enter current password: ")
        if sha256(current.encode()).hexdigest() != self.password:
            print(Fore.RED + "❌ Current password incorrect!")
            return 
        new_pass = input("Enter new password: ")
        confirm = input("Confirm the password: ")
        
        if new_pass != confirm:
            print( Fore.RED + "❌ New password do not match.")
            return
        self.password = sha256(new_pass.encode()).hexdigest()
        print(Fore.GREEN + "✅ Password Updated Successfully!")
class Teacher(Person):
    def __init__(self, name , contact_info, teachers_id, subject_assigned = None):
        super().__init__( name, contact_info, role='Teacher')
        self.__teachers_id = teachers_id
        if subject_assigned is None:
            subject_assigned = []
        self.subject_assigned = subject_assigned
        self.role_description = "Teacher"
        self.password = sha256('1234'.encode()).hexdigest()
        
    def get_teacher_id(self):
        return self.__teachers_id
    def set_teacher_id(self, new_id):
        self.__teachers_id = new_id
    
    def add_subject(self, subject_name):
        if subject_name not in self.subject_assigned:
            self.subject_assigned.append(subject_name)
            
    def remove_subject(self,subject_name):
        if subject_name in self.subject_assigned:
            self.subject_assigned.remove(subject_name)
    
    def to_dict(self):
        return {
            'name':self.name,
            'contact': self.contact_info,
            'role': self.role,
            'teacher_id': self.__teachers_id,
            'subjects': self.subject_assigned,
            'role-description': self.role_description,
            'password': self.password
        }
    def __str__(self):
        base_info = super().__str__()
        return f"{base_info}, Teachers_ID: {self.__teachers_id}, Subject_Assigned: {self.subject_assigned}"
    
    def change_password(self):
        current = input("Enter current password: ")
        if sha256(current.encode()).hexdigest() != self.password:
            print(Fore.RED + "❌ Current password incorrect!")
            return 
        new_pass = input("Enter new password: ")
        confirm = input("Confirm the password: ")
        
        if new_pass != confirm:
            print( Fore.RED + "❌ New password do not match.")
            return
        self.password = sha256(new_pass.encode()).hexdigest()
        print(Fore.GREEN + "✅ Password Updated Successfully!")
class Admin(Person):
    def __init__(self, name , contact_info, admin_id, username='admin', password='1234'):
        super().__init__( name, contact_info, role='Admin')
        self.username = username
        self.password = sha256(password.encode()).hexdigest()
        self.__admin_id = admin_id
        self.permissions = ["Manage Students", "Manage Teachers", "Generate Reports"]
    
    def authenticate(self, username, password):
        return self.username == username and self.password == sha256(password.encode()).hexdigest()
    
    def get_admin_id(self):
        return self.__admin_id
    
    def set_admin_id(self,new_id):
        self.__admin_id = new_id
        
    def __str__(self):
        base_info = super().__str__()
        return f"{base_info}, Admin ID: {self.__admin_id}, Permissions: {self.permissions} " 
    
    def change_password(self):
        current = input("Enter current password: ")
        if sha256(current.encode()).hexdigest() != self.password:
            print( Fore.RED + "❌ Current Password incorrect")
            return
        new_pass = input("Enter new password: ")
        confirm = input("Confirm new password: ")
        
        if new_pass != confirm:
            print( Fore.RED +'❌ Password do not match!')
            return
        self.password = sha256(new_pass.encode()).hexdigest() 
        print(Fore.GREEN +"✅ Password updated successfully!")
    
class SchoolManager:
    def __init__(self, data_file = 'school_data.json'):
        self.students = []
        self.teachers = []
        self.last_student_id = 0  
        self.last_teacher_id = 0
        self.data_file = data_file
    
    def generate_student_id(self):
        self.last_student_id += 1
        return f"STU{self.last_student_id:03d}"
    
    def generate_teacher_id(self):
        self.last_teacher_id += 1
        return f"TCH{self.last_teacher_id:03d}"
    def backup_data(self):
        if os.path.exists(self.data_file):
            backup_file = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"   
            with open(self.data_file, 'r') as f:
                data = f.read()
            with open(backup_file,'w') as f:
                f.write(data)
    def save_data(self):
        data = {
            'last_student_id': self.last_student_id,
            'last_teacher_id': self.last_teacher_id,
            'students': [stu.to_dict() for stu in self.students],
            'teachers': [t.to_dict() for t in self.teachers]
        }
        
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=4)
        print(Fore.GREEN+ "🗃️ Data saved successfully!")
            
    def load_data(self):
        if not os.path.exists(self.data_file) or os.path.getsize(self.data_file) == 0:
            print("No existing datafile found. Starting fresh!")
            return 
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            self.last_student_id = data.get('last_student_id', 0)
            self.last_teacher_id = data.get('last_teacher_id', 0)
            
            self.students = []
            for s in data.get('students', []):
                student_id = s.get('student_id') or self.generate_student_id()
                stu = Student(s['name'], s['contact'], student_id)
                stu.marks = s.get('marks', {})
                stu.fee_status = s.get('fee_status', 'Pending')
                stu.class_section = s.get('class_section', 'N/A')
                stu.password = s.get('password', sha256('4321'.encode()).hexdigest())
                self.students.append(stu)

            self.teachers = []
            for t_data in data.get('teachers', []):
                teacher_id = t_data.get('teacher_id') or self.generate_teacher_id()
                teacher = Teacher(t_data['name'], t_data['contact'], teacher_id, t_data.get('subjects', []))
                teacher.role_description = t_data.get('role-description ', 'Teacher')
                teacher.password = t_data.get('password',sha256('1234'.encode()).hexdigest())
                self.teachers.append(teacher)
            print(Fore.GREEN +" 🗃️ Data loaded successfully!\n")
        except FileNotFoundError:
                print(Fore.RED +'❌ No existing data found, starting fresh!')   
                        
    def add_student(self):
        print_section("Add Student",Fore.GREEN)
        name = input("Enter student name :")
        while True:
            phone = input("Enter phone number: " )
            if is_valid_phone(phone):
                break
            print(Fore.RED + "❌ Invalid Phone, must be 10 digits, e.g.9878567167")
            
        while True:
            email = input("Enter email: ")
            if is_valid_email(email):
                break
            print(Fore.RED + "❌ Invalid email format, must be like user@gmail.com")
            
        while True:
            class_section = input("Enter class section (e.g., 10-A)")
            if is_valid_class_section(class_section):
                break
            print(Fore.RED  + "❌ Invalid class-section! Format: 10-A, 12-B.")
        
        Student_id = self.generate_student_id()
        
        contact_info = {'Phone': phone, 'Email': email}
        
        new_student = Student(name, contact_info, Student_id)
        new_student.class_section = class_section
        self.students.append(new_student)
        print(Fore.GREEN + f"✅ Student {name} ({Student_id}) added successfully.\n ")
        
    def list_students(self):
        print_section("All Students",Fore.GREEN)
        if not self.students:
            print(Fore.RED + "❌ No students found.\n")
            return

        table = []
        
        for stu in self.students:
            grade = stu.calculate_grade() or 'N/A'
            fee_color = Fore.RED if stu.fee_status == 'Pending' else Fore.GREEN
            grade_color = Fore.RED if grade == 'F' else Fore.GREEN
            table.append([stu.get_student_id(), stu.name, stu.class_section, stu.contact_info['Phone'], fee_color + stu.fee_status + Style.RESET_ALL, stu.marks, grade_color + grade + Style.RESET_ALL])
        headers = ['ID', 'Name', 'Class_Section', 'Phone', 'Fee', 'Marks', 'Grade' ]
        print(tabulate(table, headers, tablefmt= 'fancy-grid', stralign='center'))
        print()

    def find_student_by_id(self, student_id):
        for stu in self.students:
            if stu.get_student_id() == student_id:
                return stu
        return None

    def update_student(self):
        print_section("Update Student",Fore.GREEN)
        student_id = input("Enter Student ID to update: ")
        stu = self.find_student_by_id(student_id)
        
        if not stu:
            print( (Fore.RED )+ f"❌ Student {student_id} not found.\n")
            return
        
        new_name = input(f"Current Name: {stu.name}\n Enter new name (Press enter to keep current): ")
        if new_name.strip():
            stu.name = new_name
            
        new_phone = input(f"Current Phone: {stu.contact_info['Phone']}\n Enter new phone (press enter to keep current): ")
        if new_phone.strip() and is_valid_phone(new_phone):
            stu.contact_info['Phone'] = new_phone
        
        new_class = input(f"Current Class/Section: {getattr(stu, 'class_section', 'N/A')}\nEnter new Class Section (press enter to keep current): ")

        if new_class.strip() and is_valid_class_section(new_class):
            stu.class_section = new_class
        print( (Fore.GREEN)+ f"✅ Student {stu.get_student_id()} updated successfully!\n")

    def delete_student(self):
        print_section("Delete Student",Fore.GREEN)
        student_id = input("Enter Student ID to delete: ")
        stu = self.find_student_by_id(student_id)
        
        if not stu:
            print( (Fore.RED ) + f"❌ Student {student_id} not found.\n")
            return
        
        confirm = input(f"Are you sure want to delete {stu.name} ({stu.get_student_id()})? (y/n)")
        if confirm.lower() == 'y':
            self.students.remove(stu)
            print( (Fore.GREEN )+f"Student {student_id} deleted successfully\n")
        else:
            print(Fore.RED +"❌ Deletion cancelled\n")
    
    def add_teachers(self):
        print_section("Add Teacher",Fore.GREEN)
        name = input("Enter teacher name :")
        while True:
            phone = input("Enter phone number :" )
            if is_valid_phone(phone):
                break
            print(Fore.RED +"❌ Invalid Phone, must be 10 digits.")
        while True:
            email = input("Enter email: ")
            
            if is_valid_email(email):
                break
            print(Fore.RED + "❌ Invalid email format.")
            
        role = input("Enter role (Teacher/Liberian/Accountant/etc)")
        
        teacher_id =  self.generate_teacher_id()
        contact_info = {'Phone': phone, 'Email': email}
        
        subjects = []
        add_subjects = input("Do you want to assign subject now? (y/n): ")
        if add_subjects.lower() =='y':
            while True:
                sub = input("Enter subject name or (press enter to finish): ")
                if sub.strip() == '':
                    break
                subjects.append(sub)
        
        new_teacher = Teacher( name , contact_info, teacher_id, subjects)  
        new_teacher.role_description = role   
        self.teachers.append(new_teacher)
        
    
    def list_teachers(self):
        print_section("All Teachers",Fore.GREEN)
        if not self.teachers:
            print( Fore.RED + "❌ No teachers found.\n")
            return
        
       
        table = []
        
        for t in self.teachers:
            table.append([t.get_teacher_id(), t.name, t.role_description, t.contact_info['Phone'], ''.join(t.subject_assigned)])
        headers = ['ID', 'Name', 'Class_Section', 'Phone', 'Fee', 'Marks', 'Grade' ]
        print(tabulate(table, headers, tablefmt= 'fancy-grid', stralign='center'))
        print()
    
    def find_teacher_id(self, teacher_id):
        for t in self.teachers:
            if t.get_teacher_id() == teacher_id:
                return t
        return None
    
    def update_teachers(self):
        print_section("Update Teacher",Fore.GREEN)
        teacher_id = input("Enter teacher id to update: ")
        t = self.find_teacher_id(teacher_id)
        
        if not t:
            print( (Fore.RED )+f"❌ Teacher {teacher_id} not found")
            return
        
        new_name = input(f"Current name: {t.name}\nEnter new name(Press enter to keep current.\n)")
        if new_name.strip():
            t.name = new_name
        
        new_phone = input(f"Current phone: {t.contact_info['Phone']}\nEnter new Phone (Press enter to keep current,)")
        if new_phone.strip() and is_valid_phone(new_phone):
            t.contact_info['Phone'] = new_phone
            
        new_email = input(f"Current email: {t.contact_info['Email']}\nEnter new Email (Press enter to keep current,)")
        if new_email.strip() and is_valid_email(new_email):
            t.contact_info['Email'] = new_email
            
        new_role = input(f"Current role: {t.role_description}\nEnter new role (Press enter to keep current.)")
        if new_role.strip():
            t.role_description = new_role
        
        print_section("Update Subject",Fore.GREEN)
        while True:
            choice = input("Do you want to (A)dd or (R)emove or (U)pdate or (F)inish?: ")
            choice = choice.lower()
            if choice == 'f':
                break
            elif choice == 'a':
                sub = input("Enter subject to add: ").strip()
                if sub:
                    t.add_subject(sub)
            elif choice == 'r':
                sub = input("Enter subject to remove: ").strip()
                if sub:
                    t.remove_subject(sub)
            elif choice == 'u':
                old_subject = input("Enter old subject to update: ").strip()
                if old_subject in t.subject_assigned:
                    new_sub = input(f"Enter new name for subject: {old_subject}: ").strip()
                    if new_sub:
                        index = t.subject_assigned.index(old_subject)
                        t.subject_assigned[index] = new_sub
                        print( (Fore.RED )+(f"✅ Subject {old_subject} updated to {new_sub}"))
                else:
                    print((Fore.RED )+ f"❌ Subject {old_subject} not found in teacher's assigned subjects.")
        print(Fore.GREEN + f"✅ Teacher {t.get_teacher_id()} updated successfully!\n")

         
    
    def delete_teacher(self):
        print_section("Delete Teacher",Fore.GREEN)
        teacher_id = input("Enter teacher id to delete: ")
        t =  self.find_teacher_id(teacher_id)
        if not t:
            print( (Fore.RED )+f"❌ Teacher {teacher_id} not found.\n")
            return
        
        confirm = input(f"Are you sure want to delete {t.name} {t.get_teacher_id()}? (y/n): ")
        if confirm.lower() == 'y':
            self.teachers.remove(t)
            print((Fore.GREEN ) + f"✅ Teacher {t.get_teacher_id()} deleted Successfully!\n")
        else:
            print(Fore.RED + "❌ Deletion cancelled.\n")
        
    
    def manage_student_marks(self):
        print_section("Manage Student Marks",Fore.GREEN)
        student_id = input("Enter student ID: ")
        stu = self.find_student_by_id(student_id)
        
        if not stu:
            print(f"Student {student_id} not found")
            return
        while True:
            subject = input("Enter subject name or(Press enter to finish): ").strip()
            if not subject:
                break
            try:
                marks = float(input(f"Enter marks for {subject}: "))
                if marks < 0 or marks > 100:
                    print(Fore.RED +"❌ Marks must be between 0-100.")
                    continue
            except ValueError:
                print(Fore.RED +"❌ Invalid input. Enter a number")
                continue
            stu.add_update_marks(subject ,  marks)
    
    def manage_fee(self):
        print_section("Manage Student Fee",Fore.GREEN)
        student_id = input("Enter student ID: ")
        stu = self.find_student_by_id(student_id)
        
        if not stu:
            print(f" student {student_id} not found")
            return 
        
        print(f"Current fee status: {stu.fee_status}")
        confirm = input("Mark fee as paid (y/n): ")
        
        if  confirm.lower() == 'y':
            stu.pay_fee()
        else:
            print(Fore.RED + "❌ Fee update cancelled.")
    
    def view_student_report(self, student):
        grade = student.calculate_grade() or 'N/A'
        
        print_section("My Report",Fore.GREEN)
        print(f"Student ID: {student.get_student_id()}")
        print(f"Name: {student.name}")
        print(f"Class: {student.class_section}")
        print(f"Fee Status: {student.fee_status}")
        print(f"Student Marks: {student.marks}")
        print(f"Grade: {grade}")
        
    def student_report(self):
        print_section("Student Report",Fore.GREEN)
        if not self.students:
            print(Fore.RED + "❌ No student found.")
            return
        
        for stu in self.students:
            grade = stu.calculate_grade() or "N/A"
            print(f"{stu.get_student_id()} | {stu.name} | Class: {stu.class_section} | Fee: {stu.fee_status} | Marks: {stu.marks} | Grade: {grade} ")
            