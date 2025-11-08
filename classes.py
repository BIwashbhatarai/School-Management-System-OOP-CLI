# classes.py
# Finalized version with fixes:
# - standardized exam schema ('subject' singular)
# - robust import/export for students/teachers/exams with ID deduplication
# - recalculation of last_* id counters after imports and load
# - improved attendance percentage denominator calculation
# - safer password defaults and defensive parsing
# - admin id generation improved to avoid duplicates
# - other defensive checks and small improvements

import json
import os
from datetime import datetime
from hashlib import sha256
import re
import csv
from colorama import Fore, Style, init
init(autoreset=True)

from tabulate import tabulate

TABLE_FMT = 'fancy_grid'

def print_section(title, color=Fore.CYAN):
    line = "-" * 60
    print("\n" + color + line + Style.RESET_ALL)
    print(color + title.center(60) + Style.RESET_ALL)
    print(color + line + Style.RESET_ALL)


def is_valid_email(email):
    pattern = r'^[\w\.-]+@([\w-]+\.)+[\w-]{2,}$'
    return bool(re.match(pattern , email))

def is_valid_phone(phone):
    return isinstance(phone, str) and phone.isdigit() and len(phone) == 10

def is_valid_class_section(cls: str) -> bool:
    if not isinstance(cls, str):
        return False
    pattern = r'^([0-9]{1,2}(-[A-Za-z])?|[A-Za-z]+)$'
    return bool(re.match(pattern, cls.strip()))

class Person:
    def __init__(self, name, contact_info, role='Person'):
        self.name = name
        self.role = role
        if contact_info is None:
            self.contact_info = {'Phone': '', 'Email': ''}
        else:
            self.contact_info = contact_info
    
    def update_contact(self, new_contact):
        if isinstance(new_contact, dict):
            self.contact_info = new_contact
        else:
            raise ValueError("Contact info must be a dictionary.")
        
    def __str__(self):
        contact_str = ", ".join(f"{k}: {v}" for k , v in self.contact_info.items())
        return f"{self.role}: {self.name}, Contact: {contact_str}"
    
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
        self.paid_amount = 0.0
        self.class_section = "N/A"
        # ensure non-empty hashed password; default '4321'
        self.password = sha256('4321'.encode()).hexdigest()

    def add_update_marks(self, subject ,  mark):
        if not isinstance(mark, (int,float)):
            raise ValueError("Mark must be a number!")
        self.marks[subject] = mark
        print(f"Marks updated for {self.name} - {subject}: {mark}")
    
    def calculate_grade(self):
        if not self.marks:
            return None
        avg = sum(self.marks.values()) / len(self.marks)
        
        if avg >= 90:
            return "A+"
        elif avg >= 80:
            return "A"
        elif avg >= 70:
            return "B+"
        elif avg >= 60:
            return "B"
        elif avg >= 50:
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
            'paid_amount': self.paid_amount,
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
    
    def change_password(self, manager=None):
        current = input("Enter current password: ").strip()
        if sha256(current.encode()).hexdigest() != self.password:
            print(Fore.RED + "❌ Current password incorrect!")
            return

        new_pass = input("Enter new password: ").strip()
        if len(new_pass) < 4:
            print(Fore.RED + "❌ Password too short, must be at least 4 characters.")
            return

        confirm = input("Confirm the password: ").strip()
        if new_pass != confirm:
            print(Fore.RED + "❌ Passwords do not match.")
            return

        self.password = sha256(new_pass.encode()).hexdigest()
        print(Fore.GREEN + "✅ Password Updated Successfully!")

        if manager:
            manager.data_changed = True
            manager.save_data()

        
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
        subjects = ", ".join(self.subject_assigned) if self.subject_assigned else "None"
        return f"{base_info}, Teachers_ID: {self.__teachers_id}, Subject_Assigned: {subjects}"
    
    def change_password(self, manager=None):
        current = input("Enter current password: ").strip()
        if sha256(current.encode()).hexdigest() != self.password:
            print(Fore.RED + "❌ Current password incorrect!")
            return

        new_pass = input("Enter new password: ").strip()
        if len(new_pass) < 4:
            print(Fore.RED + "❌ Password too short, must be at least 4 characters.")
            return

        confirm = input("Confirm the password: ").strip()
        if new_pass != confirm:
            print(Fore.RED + "❌ Passwords do not match.")
            return

        self.password = sha256(new_pass.encode()).hexdigest()
        print(Fore.GREEN + "✅ Password Updated Successfully!")

        if manager:
            manager.data_changed = True
            manager.save_data()

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
    
    def change_password(self, manager=None):
        current = input("Enter current password: ").strip()
        if sha256(current.encode()).hexdigest() != self.password:
            print(Fore.RED + "❌ Current password incorrect!")
            return

        new_pass = input("Enter new password: ").strip()
        if len(new_pass) < 4:
            print(Fore.RED + "❌ Password too short, must be at least 4 characters.")
            return

        confirm = input("Confirm the password: ").strip()
        if new_pass != confirm:
            print(Fore.RED + "❌ Passwords do not match.")
            return

        self.password = sha256(new_pass.encode()).hexdigest()
        print(Fore.GREEN + "✅ Password Updated Successfully!")

        if manager:
            manager.data_changed = True
            manager.save_data()
    
class SchoolManager:
    def __init__(self, data_file = 'school_data.json'):
        self.students = []
        self.teachers = []
        self.last_student_id = 0  
        self.last_teacher_id = 0
        self.last_admin_id = 0
        self.last_exam_id = 0
        self.data_file = data_file
        self.attendance = {}
        self.admins = []
        self.exams = []
        self.fee_structure = {}
        self.fee_transactions = []
        self.data_changed = False
        self.load_data()
        self.load_attendance()
        # ensure internal counters are accurate after load
        self._update_last_ids()
        
    # ID generators with uniqueness ensured by incrementing and checking existing sets
    def generate_student_id(self):
        """
        Generate a unique student id by incrementing last_student_id.
        Ensures uniqueness against existing students.
        """
        existing_ids = {stu.get_student_id() for stu in self.students}
        # keep incrementing until unique found
        while True:
            self.last_student_id += 1
            candidate = f"STU{self.last_student_id:03d}"
            if candidate not in existing_ids:
                return candidate

    def generate_teacher_id(self):
        existing_ids = {t.get_teacher_id() for t in self.teachers}
        while True:
            self.last_teacher_id += 1
            candidate = f"TCH{self.last_teacher_id:03d}"
            if candidate not in existing_ids:
                return candidate

    def generate_admin_id(self):
        existing_ids = {a.get('admin_id') for a in self.admins if a.get('admin_id')}
        while True:
            self.last_admin_id += 1
            candidate = f"ADM{self.last_admin_id:03d}"
            if candidate not in existing_ids:
                return candidate

    def generate_exam_id(self):
        existing_ids = {ex.get('exam_id') for ex in self.exams if ex.get('exam_id')}
        while True:
            self.last_exam_id += 1
            candidate = f"EX{self.last_exam_id:03d}"
            if candidate not in existing_ids:
                return candidate
    
    def _extract_numeric_suffix(self, identifier):
        if not identifier:
            return 0
        m = re.search(r'(\d+)$', str(identifier))
        if m:
            try:
                return int(m.group(1))
            except Exception:
                return 0
        return 0

    def _update_last_ids(self):
        # students
        max_s = 0
        for s in self.students:
            sid = s.get_student_id()
            max_s = max(max_s, self._extract_numeric_suffix(sid))
        self.last_student_id = max(self.last_student_id, max_s)

        # teachers
        max_t = 0
        for t in self.teachers:
            tid = t.get_teacher_id()
            max_t = max(max_t, self._extract_numeric_suffix(tid))
        self.last_teacher_id = max(self.last_teacher_id, max_t)

        # admins (admin_id keys in admins list)
        max_a = 0
        for a in self.admins:
            aid = a.get('admin_id') or a.get('admin-id')
            max_a = max(max_a, self._extract_numeric_suffix(aid))
        self.last_admin_id = max(self.last_admin_id, max_a)

        # exams
        max_e = 0
        for ex in self.exams:
            eid = ex.get('exam_id')
            max_e = max(max_e, self._extract_numeric_suffix(eid))
        self.last_exam_id = max(self.last_exam_id, max_e)
    
    def backup_data(self, max_backup = 5):
        if os.path.exists(self.data_file) and os.path.getsize(self.data_file) > 0:
                try:
                    with open(self.data_file, 'r') as f:
                        data = f.read().strip()
                    backup_file = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"   
                    with open(backup_file,'w') as f:
                        f.write(data)
                    print(Fore.GREEN + f" 🗃️  Backup created: {backup_file}")
                    
                    backups = sorted([f for f in os.listdir('.') if f.startswith('backup_')])
                    while len(backups) > max_backup:
                        os.remove(backups.pop(0))
                except Exception as e:
                    print(Fore.YELLOW + f"⚠️ Backup skipped: {e}")
                
    def save_data(self):
        data = {
            'last_student_id': self.last_student_id,
            'last_teacher_id': self.last_teacher_id,
            'last_admin_id': self.last_admin_id,
            'last_exam_id': self.last_exam_id,
            'students': [stu.to_dict() for stu in self.students],
            'teachers': [t.to_dict() for t in self.teachers],
            'admins' : self.admins,
            'exams': self.exams,
            'fee_structure': self.fee_structure,
            'fee_transactions': self.fee_transactions
        }
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=4)
            print(Fore.GREEN + " 🗃️ Data saved successfully!")
            self.data_changed = False
        except Exception as e:
            print( Fore.RED + f"❌ Error saving data: {e}")
        
            
    def load_data(self):
        
        default_admin = {
            'name': 'Default-Admin',
            'username': 'admin',
            'password': sha256('1234'.encode()).hexdigest(),
            'role': 'superadmin',
            'admin_id': 'ADM001'
            
        }
        if not os.path.exists(self.data_file) or os.path.getsize(self.data_file) == 0:
            self.last_student_id = 0
            self.last_teacher_id = 0
            self.students = []
            self.teachers = []
            self.attendance = {}
            self.admins = [default_admin]
            self.exams = []
            print(Fore.YELLOW + f"⚠️ No existing datafile found. starting fresh!")
            self.save_data()
            return 
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
        except Exception as e:
            # If file is corrupted or unreadable, start fresh but keep default admin
            self.last_student_id = 0
            self.last_teacher_id = 0
            self.students = []
            self.teachers = []
            self.attendance = {}
            self.admins = [default_admin]
            self.exams = []
            print(Fore.RED + f"❌ Error loading data: {e}. Starting with fresh state.")
            return
    
        self.last_student_id = data.get('last_student_id', 0) or 0
        self.last_teacher_id = data.get('last_teacher_id', 0) or 0
        self.last_admin_id = data.get('last_admin_id', 0) or 0
        self.last_exam_id = data.get('last_exam_id', 0) or 0
        
        self.exams = data.get('exams', []) or []
        self.admins = data.get('admins', []) or [default_admin]
        self.fee_structure = data.get('fee_structure', {}) or {}
        self.fee_transactions = data.get('fee_transactions', []) or []
        
        self.students = []
        for s in data.get('students', []) or []:
            student_id = s.get('student_id') or self.generate_student_id()
            contact = s.get('contact', {'Phone': '', 'Email': ''})
            stu = Student(s.get('name', f'Student {student_id}'), contact, student_id)
            stu.marks = s.get('marks', {}) or {}
            # fixed float conversion bug
            try:
                stu.paid_amount = float(s.get('paid_amount', 0.0) or 0.0)
            except (TypeError, ValueError):
                stu.paid_amount = 0.0
            stu.fee_status = s.get('fee_status', stu.fee_status) or stu.fee_status
            stu.class_section = s.get('class_section', 'N/A') or 'N/A'
            stu.password = s.get('password') or sha256('4321'.encode()).hexdigest()
            self.students.append(stu)

        self.teachers = []
        for t_data in data.get('teachers', []) or []:
            teacher_id = t_data.get('teacher_id') or self.generate_teacher_id()
            contact = t_data.get('contact', {'Phone': '', 'Email': ''})
            teacher = Teacher(t_data.get('name', f'Teacher {teacher_id}'), contact, teacher_id, t_data.get('subjects', []))
            teacher.role_description = t_data.get('role-description', 'Teacher') or 'Teacher'
            teacher.password = t_data.get('password') or sha256('1234'.encode()).hexdigest()
            self.teachers.append(teacher)
        
        # normalize admins to use 'admin_id' key
        raw_admins = data.get('admins', [default_admin]) or [default_admin]
        normalized_admin = []
        
        for idx , a in enumerate(raw_admins, start=1):
            normalized_admin.append({
                'name': a.get('name', f'Admin{idx}'),
                'username': a.get('username', f'admin{idx}'),
                'password': a.get('password') or sha256('1234'.encode()).hexdigest(),
                'role': a.get('role', 'admin'),
                'admin_id': a.get('admin_id') or a.get('admin-id') or f'ADM{idx:03d}'
            })
        self.admins = normalized_admin
        
        # Ensure exams have minimum canonical fields (subject singular, max_marks, allow_bonus, results, exam_id)
        loaded_exams = []
        for ex in self.exams:
            # ex may already be the dict stored; ensure canonical shape
            exam_id = ex.get('exam_id') or ex.get('examId') or None
            if not exam_id:
                exam_id = self.generate_exam_id()
            subject = ex.get('subject')
            # if only 'subjects' provided (list or comma-str), choose first
            if not subject and 'subjects' in ex:
                subjects_field = ex.get('subjects') or []
                if isinstance(subjects_field, list) and subjects_field:
                    subject = subjects_field[0]
                elif isinstance(subjects_field, str) and subjects_field.strip():
                    # take first comma-separated
                    subject = subjects_field.split(',')[0].strip()
            # fallback to empty string
            subject = subject or ''
            max_marks = ex.get('max_marks', ex.get('maxMark', 100) )
            try:
                max_marks = float(max_marks or 100)
            except (TypeError, ValueError):
                max_marks = 100.0
            allow_bonus = bool(ex.get('allow_bonus') or ex.get('allowBonus') or False)
            results = ex.get('results') or {}
            exam_name = ex.get('exam_name') or ex.get('examName') or ex.get('name') or ''
            date = ex.get('date') or ''
            loaded_exams.append({
                'exam_id': exam_id,
                'exam_name': exam_name,
                'class': ex.get('class',''),
                'subject': subject,
                'date': date,
                'max_marks': max_marks,
                'allow_bonus': allow_bonus,
                'results': results
            })
        self.exams = loaded_exams
        
        # Finalize counters
        self._update_last_ids()
        print(Fore.GREEN + "🗃️ Data loaded successfully (admins included.)")
        
    def add_student(self):
        print_section("Add Student", Fore.CYAN)
        name = input("Enter student name: ")
        while True:
            phone = input("Enter phone number: ")
            if is_valid_phone(phone):
                break
            print(Fore.RED + "❌ Invalid Phone, must be 10 digits, e.g.9878567167")
            
        while True:
            email = input("Enter email: ")
            if is_valid_email(email):
                break
            print(Fore.RED + "❌ Invalid email format, must be like user@gmail.com")
            
        while True:
            class_section = input("Enter class section (e.g., 10-A): ")
            if is_valid_class_section(class_section):
                break
            print(Fore.RED +"❌ Invalid class-section! Format: 10-A, 12-B.")
        
        student_id = self.generate_student_id()
        
        contact_info = {'Phone': phone, 'Email': email}
        
        new_student = Student(name, contact_info, student_id)
        new_student.class_section = class_section
        self.students.append(new_student)
        self.data_changed = True
        print(Fore.GREEN + f"✅ Student {name} ({student_id}) added successfully.\n ")
        
    def list_students(self):
        print_section("All Students",Fore.GREEN)
        if not self.students:
            print(Fore.RED + "❌ No students found.\n")
            return

        table = []
            
        for stu in self.students:
            grade = stu.calculate_grade() or 'N/A'
            marks_display = Fore.RED + "N/A" + Style.RESET_ALL if not stu.marks else Fore.GREEN + str(stu.marks) + Style.RESET_ALL
            fee_color = Fore.RED if str(stu.fee_status).lower() == 'pending' else Fore.GREEN
            grade_color = Fore.RED if grade in ('F', 'N/A') else Fore.GREEN
            
            table.append([
                stu.get_student_id(),
                stu.name,
                stu.class_section,
                stu.contact_info.get('Phone', 'N/A'),
                fee_color + stu.fee_status + Style.RESET_ALL,
                marks_display,
                grade_color + grade + Style.RESET_ALL
            ])
        headers = ['ID', 'Name', 'Class_Section', 'Phone', 'Fee', 'Marks', 'Grade' ]
        print(tabulate(table, headers, tablefmt=TABLE_FMT, stralign='center'))
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
        
        new_name = input(f"Current Name: {stu.name}\nEnter new name (Press enter to keep current): ")
        if new_name.strip():
            stu.name = new_name
            
        while True:    
            current_phone = stu.contact_info.get('Phone', 'N/A')
            new_phone = input(f"Current Phone: {current_phone}\n Enter new phone (press enter to keep current): ")
            if not new_phone.strip():
                break
            if is_valid_phone(new_phone):
                stu.contact_info['Phone'] = new_phone
                break
            print(Fore.RED + f"❌ Invalid Phone, must be 10 digits, e.g, 9846288338")
            
        while True:
            current_class = getattr(stu, 'class_section',"N/A")
            new_class = input(f"Current Class/Section: {current_class}\nEnter new Class Section (press enter to keep current): ")
            if not new_class.strip():
                break
            if is_valid_class_section(new_class):
                stu.class_section = new_class
            else:
                print(Fore.RED + "❌ Invalid class-section format.")
                continue
            break
        self.data_changed = True
        print(Fore.GREEN+ f"✅ Student {stu.get_student_id()} updated successfully!\n")

    def delete_student(self):
        print_section("Delete Student",Fore.GREEN)
        student_id = input("Enter Student ID to delete: ")
        stu = self.find_student_by_id(student_id)
        
        if not stu:
            print(Fore.RED + f"❌ Student {student_id} not found.\n")
            return
        
        confirm = input(f"Are you sure want to delete {stu.name} ({stu.get_student_id()})? (y/n) ").strip().lower()
        if confirm in ['y', 'yes']:
            try:
                self.students.remove(stu)
                print(Fore.GREEN + f"Student {student_id} deleted successfully\n")
            except ValueError:
                print(Fore.RED + "❌ Error: Student not in list.")
        else:
            print(Fore.RED + "❌ Deletion cancelled\n")
        self.data_changed = True
    
    def add_teachers(self):
        print_section("Add Teacher",Fore.GREEN)
        name = input("Enter teacher name: ")
        while True:
            phone = input("Enter phone number: ")
            if is_valid_phone(phone):
                break
            print(Fore.RED + "❌ Invalid Phone, must be 10 digits.")
        while True:
            email = input("Enter email: ")
            if is_valid_email(email):
                break
            print(Fore.RED + "❌ Invalid email format.")
            
        role = input("Enter role (Teacher/Librarian/Accountant/etc) ") or "Teacher"
        teacher_id =  self.generate_teacher_id()
        contact_info = {'Phone': phone, 'Email': email}
        
        subjects = []
        add_subjects = input("Do you want to assign subject now? (y/n): ")
        if add_subjects.lower() in ['y', 'yes']:
            while True:
                sub = input("Enter subject name or press enter to finish: ").strip()
                if not sub:
                    break
                subjects.append(sub)
                
        new_teacher = Teacher(name , contact_info, teacher_id, subjects)  
        new_teacher.role_description = role   
        self.teachers.append(new_teacher)
        self.data_changed = True
        print(Fore.GREEN + f"✅ Teacher {name} ({teacher_id}) added successfully.\n")
        
    
    def list_teachers(self):
        print_section("All Teachers",Fore.GREEN)
        if not self.teachers:
            print( Fore.RED + "❌ No teachers found.\n")
            return
        
       
        table = []
        
        for t in self.teachers:
            table.append([t.get_teacher_id(), t.name, t.role_description, t.contact_info.get('Phone', 'N/A'), ', '.join(t.subject_assigned) if t.subject_assigned else "N/A" ])
        headers = ['ID','Name','Role','Phone','Subjects']
        print(tabulate(table, headers, tablefmt=TABLE_FMT, stralign='center'))
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
            print(Fore.RED + f"❌ Teacher {teacher_id} not found")
            return
        
        new_name = input(f"Current name: {t.name}\nEnter new name(Press enter to keep current.\n)").strip()
        if new_name:
            t.name = new_name
        
        new_phone = input(f"Current phone: {t.contact_info.get('Phone','N/A')}\nEnter new Phone (Press enter to keep current,)")
        if new_phone.strip() and is_valid_phone(new_phone):
            t.contact_info['Phone'] = new_phone
            
        new_email = input(f"Current email: {t.contact_info.get('Email','N/A')}\nEnter new Email (Press enter to keep current,)")
        if new_email.strip() and is_valid_email(new_email):
            t.contact_info['Email'] = new_email
            
        new_role = input(f"Current role: {t.role_description}\nEnter new role (Press enter to keep current.)")
        if new_role.strip():
            t.role_description = new_role
        
        print_section("Update Subject",Fore.GREEN)
        while True:
            choice = input("Do you want to (A)dd or (R)emove or (U)pdate or (F)inish?: ").strip().lower()
            if not choice:
                continue
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
                        print( (Fore.GREEN )+(f"✅ Subject {old_subject} updated to {new_sub}"))
                else:
                    print((Fore.RED )+ f"❌ Subject {old_subject} not found in teacher's assigned subjects.")
        self.data_changed = True
        print(Fore.GREEN + f"✅ Teacher {t.get_teacher_id()} updated successfully!\n")

         
    
    def delete_teacher(self):
        print_section("Delete Teacher",Fore.GREEN)
        teacher_id = input("Enter teacher id to delete: ")
        t =  self.find_teacher_id(teacher_id)
        if not t:
            print(Fore.RED + f"❌ Teacher {teacher_id} not found.\n")
            return
        
        confirm = input(f"Are you sure want to delete {t.name} ({t.get_teacher_id()})? (y/n): ").strip().lower()
        if confirm in ['yes','y']:
            self.teachers.remove(t)
            print(Fore.GREEN + f"✅ Teacher {t.get_teacher_id()} deleted Successfully!\n")
        else:
            print(Fore.RED + "❌ Deletion cancelled.\n")
        self.data_changed = True
        
    
    def manage_student_marks(self):
        print_section("Manage Student Marks",Fore.GREEN)
        student_id = input("Enter student ID: ").strip()
        stu = self.find_student_by_id(student_id)
        
        if not stu:
            print(f"❌ Student {student_id} not found.")
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
            print(Fore.GREEN + f"✅ Marks entry completed for {stu.name}")
        self.data_changed = True
    
    def manage_fee(self):
        # Note: Phase 1 keeps existing manage_fee behavior (mark paid)
        # Detailed payment collection (amounts, transactions) will be implemented in Phase 3.
        print_section("Manage Student Fee",Fore.GREEN)
        student_id = input("Enter student ID: ").strip()
        stu = self.find_student_by_id(student_id)
        
        if not stu:
            print(Fore.RED + f"❌ student {student_id} not found")
            return 
        
        print(f"Current Fee Status: {stu.fee_status}")
        confirm = input("Mark fee as paid (y/n): ")
        
        if  confirm.lower() in ['yes','y']:
            stu.pay_fee()
        else:
            print(Fore.RED + "❌ Fee update cancelled.")
        self.data_changed = True
        
    def view_student_report(self, student):
        grade = student.calculate_grade() or 'N/A'
        fee_color = Fore.GREEN if student.fee_status.lower() == "paid" else Fore.RED
        grade_color = Fore.RED if grade == 'F' else Fore.GREEN

        print_section("My Report", Fore.GREEN)
        print(f"Student ID: {student.get_student_id()}")
        print(f"Name: {student.name}")
        print(f"Class: {student.class_section}")
        print(f"Fee Status: {fee_color}{student.fee_status}{Style.RESET_ALL}")
        print("Marks:")
        if student.marks:
            for subj, mark in student.marks.items():
                print(f"  {subj}: {mark}")
        else:
            print("  N/A")
        print(f"Grade: {grade_color}{grade}{Style.RESET_ALL}")

            
    def student_report(self):
        print_section("Student Report", Fore.GREEN)
        if not self.students:
            print(Fore.RED + "❌ No student found.")
            return

        table = []
        for stu in self.students:
            grade = stu.calculate_grade() or "N/A"
            fee_color = Fore.GREEN if stu.fee_status.lower() == "paid" else Fore.RED
            grade_color = Fore.RED if grade in ('F', 'N/A') else Fore.GREEN
            marks_str = ', '.join(f"{sub}: {mark}" for sub, mark in stu.marks.items()) or "N/A"

            table.append([
                stu.get_student_id(),
                stu.name,
                stu.class_section,
                fee_color + stu.fee_status + Style.RESET_ALL,
                marks_str,
                grade_color + grade + Style.RESET_ALL
            ])

        headers = ['ID', 'Name', 'Class', 'Fee', 'Marks', 'Grade']
        print(tabulate(table, headers=headers, tablefmt=TABLE_FMT, stralign='center'))
        print()

    
    def report_by_class(self):
        print_section("📘 CLASS-WISE STUDENT REPORT 📘", Fore.CYAN)

        if not self.students:
            print(Fore.RED + "❌ No students found.\n")
            return 

        class_name = input("Enter class/section to view (e.g. 10-A): ").strip().lower()

        filtered_students = [stu for stu in self.students if stu.class_section.strip().lower() == class_name]

        if not filtered_students:
            print(Fore.RED + f"❌ No students found in class {class_name.upper()}.\n")
            return

        table = []
        for stu in filtered_students:
            grade = stu.calculate_grade() or 'N/A'
            fee_color = Fore.GREEN if stu.fee_status.lower() == "paid" else Fore.RED
            grade_color = Fore.RED if grade == 'F' else Fore.GREEN

            table.append([
                stu.get_student_id(),
                stu.name,
                stu.class_section,
                fee_color + stu.fee_status + Style.RESET_ALL,
                grade_color + grade + Style.RESET_ALL
            ])
        
        print("\n" + tabulate(table, headers=['ID', 'Name', 'Class', 'Fee', 'Grade'], tablefmt=TABLE_FMT, stralign='center'))

    def report_by_fee(self):
        print_section('💰 FEE-WISE STUDENT REPORT 💰', Fore.CYAN)

        if not self.students:
            print(Fore.RED + "❌ No students found.\n")
            return 

        paid_students = [stu for stu in self.students if stu.fee_status.lower() == 'paid']
        pending_students = [stu for stu in self.students if stu.fee_status.lower() == 'pending']

        if paid_students:
            print(Fore.GREEN + '\n✅ Paid Students:')
            table = []
            for stu in paid_students:
                fee_color = Fore.GREEN
                table.append([
                    stu.get_student_id(),
                    stu.name,
                    stu.class_section,
                    fee_color + stu.fee_status + Style.RESET_ALL
                ])
            print("\n" + tabulate(table, headers=['ID','Name','Class','Fee'], tablefmt=TABLE_FMT, stralign='center'))
        else:
            print(Fore.RED + "\n❌ No students have paid their fees yet.")   

        if pending_students:
            print(Fore.RED + '\n❌ Pending Students:')
            table = []
            for stu in pending_students:
                fee_color = Fore.RED
                table.append([
                    stu.get_student_id(),
                    stu.name,
                    stu.class_section,
                    fee_color + stu.fee_status + Style.RESET_ALL
                ])
            print("\n" + tabulate(table, headers=['ID','Name','Class','Fee'], tablefmt=TABLE_FMT, stralign='center'))
        else:
            print(Fore.GREEN + "\n✅ All students have paid their fees.")  

    def report_top_students(self, Top_n=5):
        print_section("🏆 TOP STUDENTS REPORT 🏆", Fore.CYAN)
        
        if not self.students:
            print(Fore.RED + "❌ No students found.\n")
            return

        student_with_avg = []
        for stu in self.students:
            if stu.marks:
                avg_marks = sum(stu.marks.values()) / len(stu.marks)
                student_with_avg.append((stu, avg_marks))

        if not student_with_avg:
            print(Fore.RED + "❌ No marks found for any student.\n")
            return  

        student_with_avg.sort(key=lambda x: x[1], reverse=True)
        top_students = student_with_avg[:Top_n]

        table = []
        for stu, avg in top_students:
            grade = stu.calculate_grade() or 'N/A'
            grade_color = Fore.RED if grade == 'F' else Fore.GREEN

            table.append([
                stu.get_student_id(),
                stu.name,
                stu.class_section,
                round(avg, 2),
                grade_color + grade + Style.RESET_ALL
            ])

        print('\n' + tabulate(table, headers=['ID', 'Name', 'Class', 'Avg_Marks', 'Grade'], tablefmt=TABLE_FMT, stralign='center'))

    def search_students(self):
        print_section('🔍 Search Students', Fore.CYAN)
        
        if not self.students:
            print(Fore.RED + '❌ No students found.\n')
            return 
        
        keywords = input("Enter keywords to search (Name, ID, Class, Phone etc.): ").strip().lower()
        if not keywords:
            print(Fore.RED + "❌ No keywords entered.\n")
            return
        
        results = []
        for stu in self.students:
            if (
                keywords in (stu.name or '').lower()
                or keywords in (stu.get_student_id() or '').lower()
                or keywords in getattr(stu, 'class_section', 'N/A').lower()
                or keywords in (stu.contact_info.get('Phone','') or '').lower()
                or keywords in (stu.contact_info.get('Email','') or '').lower()
                or keywords in str(stu.fee_status).lower()
            ):
                results.append(stu)

        if not results:
            print(Fore.RED + "❌ No matching student found.\n")   
            return 

        table = []
        for rstu in results:
            grade = rstu.calculate_grade() or 'N/A'
            table.append([
                rstu.get_student_id(),
                rstu.name,
                rstu.class_section,
                rstu.contact_info.get('Phone',''),
                rstu.fee_status,
                rstu.marks or 'N/A',
                grade
            ])
        headers = ['ID', 'Name', 'Class', 'Phone', 'Fee_status', 'Marks', 'Grade']
        print(tabulate(table, headers, tablefmt=TABLE_FMT, stralign='center'))
            
            
    
    def search_teachers(self):
        print_section('🔍 Search Teachers', Fore.CYAN)
        
        if not self.teachers:
            print(Fore.RED + '❌ No teachers found.\n')
            return 
        
        keywords = input("Enter keywords to search (Name, ID, Phone, subjects etc.): ").strip().lower()
        if not keywords:
            print(Fore.RED + "❌ No keywords entered.\n")
            return
        
        results = []
        for t in self.teachers:
            if(
                keywords in (t.name or '').lower()
                or keywords in (t.get_teacher_id() or '').lower()
                or keywords in (t.contact_info.get('Phone','') or '').lower()
                or keywords in (t.contact_info.get('Email', '') or '').lower()
                or keywords in (t.role_description or '').lower()
                or any(keywords in sub.lower() for sub in t.subject_assigned)
            ):
                results.append(t)
        if not results:
            print(Fore.RED + "❌ No matching teachers found.\n")   
            return 
        table = []
        for t in results:
                subjects = ', '.join(t.subject_assigned) if t.subject_assigned else "N/A"
                table.append([
                    t.get_teacher_id(),
                    t.name,
                    t.role_description,
                    t.contact_info.get('Phone',''),
                    subjects
                ])
        headers = ['ID', 'Name', 'Role', 'Phone', 'Subjects']
        print(tabulate(table, headers, tablefmt=TABLE_FMT, stralign='center'))
            
    def mark_attendance(self):
        print_section("📑 MARK ATTENDANCE 📑", Fore.CYAN)
        
        if not self.students:
            print(Fore.RED + "❌ No Students Found." + Style.RESET_ALL)
            return 

        date_str = input("Enter date (YYYY-MM-DD) or press enter for today: ").strip()
        
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
        else:
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                print(Fore.RED + "❌ Invalid date format! Using today instead." + Style.RESET_ALL)
                date_str = datetime.now().strftime("%Y-%m-%d")

        if date_str not in self.attendance:
            self.attendance[date_str] = {}
            
        for stu in self.students:
            status = input(f'{stu.get_student_id()} - {stu.name} (P/A) ').strip().upper()
            while status not in ['P', 'A']:
                print(Fore.RED + "❌ Invalid input! Enter 'P' for Present and 'A' for Absent." + Style.RESET_ALL)
                status = input(f'{stu.get_student_id()} - {stu.name} (P/A) ').strip().upper()        
                
            self.attendance[date_str][stu.get_student_id()] = 'Present' if status == 'P' else 'Absent'
        
        print(Fore.GREEN + f"✅ Attendance marked for {date_str}!" + Style.RESET_ALL)
        self.save_attendance()

        #---- AUTOMATIC LOW ATTENDANCE ALERT -----#
        print(Fore.CYAN + "\n ⚠️ Checking for students with low attendance... " + Style.RESET_ALL)
        self.low_attendance_report()
        self.data_changed = True
        
    def save_attendance(self, filename='attendance.json'):
        try:
            with open(filename, 'w') as f:
                json.dump(self.attendance, f, indent=4)
            print(Fore.GREEN + f"🗃️ Attendance saved successfully to {filename}!" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"❌ Error saving attendance: {e}" + Style.RESET_ALL)

    def load_attendance(self, filename='attendance.json'):
        if not os.path.exists(filename) or os.path.getsize(filename) == 0:
            print(Fore.YELLOW + "⚠️ No existing attendance file found. Starting fresh!" + Style.RESET_ALL)
            self.attendance = {}
            return
        try:
            with open(filename, 'r') as f:
                self.attendance = json.load(f)
            if not isinstance(self.attendance, dict):
                self.attendance = {}
            print(Fore.GREEN + f"🗃️ Attendance loaded successfully from {filename}!" + Style.RESET_ALL)
        except Exception as e:
            self.attendance = {}
            print(Fore.RED + f"❌ Error loading attendance: {e}" + Style.RESET_ALL)
            
    def view_attendance(self):
        print_section("📅 VIEW ATTENDANCE", Fore.CYAN)
        if not self.attendance:
            print(Fore.RED + "❌ No attendance record found.\n" + Style.RESET_ALL)
            return 
        
        print("1. View by Date")
        print("2. View by Student ID")
        
        choice = input("Enter your choice (1/2): ").strip()
        
        if choice == '1':
            date_str = input("Enter date (YYYY-MM-DD): ").strip()
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                print(Fore.RED + "❌ Invalid date format.\n" + Style.RESET_ALL)
                return
            
            if date_str not in self.attendance:
                print(Fore.RED + f"❌ No attendance found for {date_str}\n" + Style.RESET_ALL)
                return 
            
            table = []
            for sid, status in self.attendance[date_str].items():
                stu = self.find_student_by_id(sid)
                name = stu.name if stu else 'Unknown'
                table.append([sid, name, status])
            print("\n" + tabulate(table, headers=['ID', 'Name', 'Status'], tablefmt=TABLE_FMT, stralign='center'))
        
        elif choice == '2':
            sid = input("Enter student ID: ").strip()
            table = []
            for date, records in self.attendance.items():
                if sid in records:
                    table.append([date, records[sid]])
            
            if not table:
                print(Fore.RED + f"❌ No attendance found for {sid}.\n" + Style.RESET_ALL)
                return
            
            print("\n" + tabulate(table, headers=['Date', 'Status'], tablefmt=TABLE_FMT, stralign='center'))
        
        else:
            print(Fore.RED + "❌ Invalid choice.\n" + Style.RESET_ALL)
            
    def school_attendance_percentage(self):
        print_section("📅 STUDENT ATTENDANCE PERCENTAGE ", Fore.CYAN)
        
        if not self.students:
            print(Fore.RED + "❌ No student found.\n")
            return 
        table = []
        for stu in self.students:
            total_days = 0
            present_days = 0
            
            for _, records in self.attendance.items():
                if stu.get_student_id() in records:
                    total_days += 1
                    if records.get(stu.get_student_id()) == 'Present':
                        present_days += 1
            if total_days > 0:
                percentage = (present_days / total_days) * 100
                color = Fore.GREEN if percentage >= 75 else Fore.RED
                table.append([stu.get_student_id(), stu.name, f"{color}{percentage:.2f}%{Style.RESET_ALL}", present_days, total_days])
            else:
                table.append([stu.get_student_id(), stu.name, Fore.YELLOW + "N/A" + Style.RESET_ALL, 0, 0])
            
        headers = ['ID', 'Name', 'Attendance %', 'Days Present', 'Total Days']
        print('\n'+tabulate(table,headers,tablefmt=TABLE_FMT, stralign='center'))
    def calculate_attendance_percentage(self, student_id):
        # Count only the days where the student has a recorded status
        total_days = sum(1 for day in self.attendance.values() if student_id in day)
        if total_days == 0:
            return 0.0
        present_count = sum(1 for day in self.attendance.values() if day.get(student_id) == 'Present')
        return (present_count / total_days) * 100
    
    def low_attendance_report(self,threshold = 75):
        print_section("⚠️ LOW ATTENDANCE REPORT ", Fore.CYAN)
        
        if not self.students:
            print(Fore.RED + "❌ No student found.\n")
            return 
        table = []
        
        for stu in self.students:
            percent = self.calculate_attendance_percentage(stu.get_student_id())
            # include students with percentage less than threshold (0% included)
            if percent < threshold:
                table.append([
                    stu.get_student_id(),
                    stu.name,
                    stu.class_section,
                    f"{percent:.2f}"
                ])
        if not table:
            print(Fore.GREEN + f"✅ All students have attendance above {threshold}%.\n")
            return     
        headers = ['ID', 'Name', 'Class', 'Percentage']
        print("\n"+ tabulate(table, headers, tablefmt=TABLE_FMT, stralign='center'))
            
    def add_admin(self,name,username,password,role='admin'):
        if not username or not password:
            print(Fore.RED + "❌ username and Password are required.")
            return False
        
        if any(a['username'] == username for a in self.admins):
            print(Fore.RED + f"Admin with username {username} already exists.")
            return False
        
        new_id = self.generate_admin_id()
        hashed = sha256(password.encode()).hexdigest()
        self.admins.append({'name': name, 'username': username, 'password': hashed, 'role': role, 'admin_id': new_id})
        self.data_changed = True
        self.save_data()
        print(Fore.GREEN + f"Admin {username} added successfully with the role {role}.")
        return True

    def list_admins(self):
        if not getattr(self, 'admins', None):
            print(Fore.YELLOW + "No admins configured." + Style.RESET_ALL)
            return
        
        headers = ['Admin_ID', 'Name', 'Username', 'Role']
        table = []
        
        for a in self.admins:
            admin_id = a.get('admin_id')  # normalized key
            name = a.get('name')
            username = a.get('username')
            role = a.get('role')
            table.append([admin_id, name, username, role])
        
        print_section("Admins", Fore.CYAN)
        print(tabulate(table, headers, tablefmt=TABLE_FMT, stralign='center'))
        print()
        
    def delete_admin(self, username):
        admin = next((a for a in self.admins if a['username'] == username), None)
        if not admin:
            print(Fore.RED + f"❌ No admin found with the username {username}." + Style.RESET_ALL)
            return
        
        if admin.get('role') == 'superadmin':
            superadmins = [s for s in self.admins if s.get('role') == 'superadmin']
            if len(superadmins) == 1:
                print(Fore.RED + "❌ Cannot delete the last superadmin." + Style.RESET_ALL)
                return
        
        confirm = input(Fore.YELLOW + f"Delete admin '{username}' (role: {admin.get('role')})? Type 'yes' to confirm: " + Style.RESET_ALL).lower()
        if confirm != 'yes':
            print(Fore.RED + "❌ Deletion Cancelled." + Style.RESET_ALL)
            return
        
        self.admins.remove(admin)
        self.data_changed = True
        self.save_data()
        print(Fore.GREEN + f"✅ Admin {username} deleted successfully." + Style.RESET_ALL)

    
    def change_admin_role(self, username_to_change, new_role):
            valid_roles = ['admin', 'superadmin']
            
            if new_role not in valid_roles:
                print(Fore.RED + f"❌ Invalid role '{new_role}'. Valid roles: {', '.join(valid_roles)}." + Style.RESET_ALL)
                return False

            admin = next((a for a in self.admins if a['username'] == username_to_change), None)
            if not admin:
                print(Fore.RED + f"❌ No admin found with the username {username_to_change}." + Style.RESET_ALL)
                return False

            old_role = admin.get('role', 'admin')
            
            if old_role == new_role:
                print(Fore.YELLOW + f"⚠️ Admin {username_to_change} already has the role '{new_role}'." + Style.RESET_ALL)
                return False

            # Prevent changing the last superadmin to admin
            if old_role == 'superadmin' and new_role != 'superadmin':
                superadmins = [a for a in self.admins if a.get('role') == 'superadmin']
                if len(superadmins) == 1:
                    print(Fore.RED + "❌ Cannot change role of the last superadmin." + Style.RESET_ALL)
                    return False

            admin['role'] = new_role
            self.data_changed = True
            self.save_data()
            print(Fore.GREEN + f"✅ Admin {username_to_change} role changed: {old_role} -> {new_role}" + Style.RESET_ALL)
            return True

    def get_valid_choice(self, prompt, choices):
        choices_str = list(map(str, choices))
        while True:
            choice = input(prompt).strip()
            if choice in choices_str:
                return choice
            else:
                print(f"❌ Invalid input! Please enter one of {choices_str}.")
    
    def get_dash_board_alerts(self):
        alerts = []

        # Low attendance: calculate with existing method
        low_attendance_students = []
        for student in self.students:
            pct = self.calculate_attendance_percentage(student.get_student_id())
            if pct < 75:
                low_attendance_students.append(student)
        if low_attendance_students:
            alerts.append(Fore.RED + f"⚠️ {len(low_attendance_students)} students have low attendance (<75%)")
        
        # Pending fees: consider fee_structure when available, else fall back to fee_status
        pending_fees_students = []
        for student in self.students:
            cls = student.class_section
            class_fee = self.fee_structure.get(cls)
            try:
                paid = float(student.paid_amount or 0.0)
            except (TypeError, ValueError):
                paid = 0.0
            if class_fee is not None:
                try:
                    class_fee_val = float(class_fee or 0.0)
                except (TypeError, ValueError):
                    class_fee_val = 0.0
                if paid < class_fee_val:
                    pending_fees_students.append(student)
            else:
                # If no class fee defined, rely on fee_status
                if str(student.fee_status).lower() != 'paid':
                    pending_fees_students.append(student)

        if pending_fees_students:
            alerts.append(Fore.RED + f"⚠️ {len(pending_fees_students)} students have pending fees")
        
        return alerts
    
    def show_dashboard_alerts(self):
        alerts = self.get_dash_board_alerts()
        print_section("📢 DASHBOARD ALERTS", Fore.RED)
        
        if not alerts:
            print(Fore.GREEN + "✅ No alerts. All students are fine!" + Style.RESET_ALL)
            return

        table = []
        for idx, alert in enumerate(alerts, start=1):
            table.append([idx, alert])
        
        print(tabulate(table, headers=['No.', 'Alert'], tablefmt=TABLE_FMT, stralign='center'))
        print()

    
    def create_exam(self):
        print_section("Create New Exam", Fore.CYAN)
        
        exam_id = input("Enter Exam ID (e.g, EX001) or press Enter to auto-generate: ").strip()
        class_name = input("Enter Class Name e.g, (10-A): ").strip()
        subject = input("Enter Subject Name e.g, (Math): ").strip()
        exam_name = input("Enter Exam Name e.g, (First Term): ").strip()
        date = input("Enter Exam Date (YYYY-MM-DD): ").strip()
        
        max_marks_input = input("Enter Maximum Marks (default 100): ").strip()
        try:
            max_marks = float(max_marks_input) if max_marks_input else 100.0
        except ValueError:
            print(Fore.RED + "❌ Invalid marks. Setting max_marks to 100 by default.")
            max_marks = 100.0
        allow_bonus = input("Allow bonus marks for this exam (y/n): ").strip().lower() in ('yes', 'y')
        
        if not exam_id:
            exam_id = self.generate_exam_id()
            
        exam = {
            'exam_id': exam_id,
            'exam_name': exam_name,
            'class': class_name,
            'subject': subject,
            'date': date,
            'max_marks': max_marks,
            'allow_bonus': allow_bonus,
            'results': {} 
        }
        self.exams.append(exam)
        self.data_changed = True
        self._update_last_ids()
        self.save_data()
        print(Fore.GREEN + f"✅ Exam '{exam_name}' for {class_name} - {subject} created successfully!" + Style.RESET_ALL)
    
    def list_exams(self):
        print_section("ALL EXAMS", Fore.CYAN)
        
        if not self.exams:
            print(Fore.RED + "❌ No exams found.\n")
            return 
        
        table = []
        for idx , exam in enumerate(self.exams, start=1):
            table.append([
                idx,
                exam.get('exam_id',''),
                exam.get('class',''),
                exam.get('subject',''),
                exam.get('exam_name',''),
                exam.get('date',''),
                exam.get('max_marks','')
            ])
        
        header = ['#', 'Exam Id', 'Class', 'Subject', 'Exam Name', 'Date', 'Max_Marks']
        print(tabulate(table, header, tablefmt=TABLE_FMT, stralign='center'))
        print()
    
    def enter_marks(self):
        print_section("ENTER EXAM MARKS", Fore.CYAN)

        if not self.exams:
            print(Fore.RED + "❌ No exams found. Please create an exam first.\n")
            return

        # Show exams briefly
        for idx, exam in enumerate(self.exams, start=1):
            print(f"{idx}. {exam.get('exam_name','')} - {exam.get('class','')} - {exam.get('subject','')}")
        exam_index = input("Select exam number to enter marks for: ").strip()

        if not exam_index.isdigit() or int(exam_index) < 1 or int(exam_index) > len(self.exams):
            print(Fore.RED + "❌ Invalid exam selection.\n")
            return

        exam = self.exams[int(exam_index) - 1]
        exam_class = exam.get('class', '').strip().lower()
        max_marks = float(exam.get('max_marks', 100) or 100)
        allow_bonus = bool(exam.get('allow_bonus', False))

        if 'results' not in exam or not isinstance(exam.get('results'), dict):
            exam['results'] = {}

        students_in_class = [s for s in self.students if s.class_section.strip().lower() == exam_class]
        if not students_in_class:
            print(Fore.RED + f"❌ No students found in class {exam.get('class')} ")
            return

        print(f"\nEntering marks for {exam.get('exam_name')} ({exam.get('subject')})\n")
        for stu in students_in_class:
            sid = stu.get_student_id()
            print(f"Student: {stu.name} ({sid})")
            while True:
                raw = input(f"Enter marks out of {max_marks} (press Enter to skip): ").strip()

                # Skip to next student
                if raw == "":
                    print(Fore.CYAN + "⏩ Skipped this student.\n")
                    break

                try:
                    marks = float(raw)
                    if marks < 0 or marks > max_marks:
                        print(Fore.RED + f"❌ Marks must be between 0 and {max_marks}")
                        continue
                except ValueError:
                    print(Fore.RED + "❌ Please enter a valid number.")
                    continue

                bonus = 0.0
                if allow_bonus:
                    bonus_in = input("Enter bonus marks (press Enter to skip): ").strip()
                    if bonus_in:
                        try:
                            bonus = float(bonus_in)
                            if bonus < 0:
                                print(Fore.RED + "❌ Bonus cannot be negative. Using 0.")
                                bonus = 0.0
                        except ValueError:
                            print(Fore.RED + "❌ Invalid bonus input. Using 0.")
                            bonus = 0.0

                exam['results'][sid] = {'marks': marks, 'bonus': bonus}
                print(Fore.GREEN + f"✅ Marks saved for {stu.name}: {marks} (+{bonus})\n")
                break  

        self._update_last_ids()
        self.save_data()
        print(Fore.GREEN + "✅ All marks entry complete and saved.\n")

    def calculate_student_percentage(self, student_id):
        total_max = 0.0
        total_obtained = 0.0
        details = []

        for ex in self.exams:
            results = ex.get('results', {}) or {}
            if student_id not in results:
                continue

            res = results.get(student_id, {})
            try:
                marks = float(res.get('marks', 0) or 0)
            except (ValueError, TypeError):
                marks = 0.0
            try:
                bonus = float(res.get('bonus', 0) or 0)
            except (ValueError, TypeError):
                bonus = 0.0
            try:
                max_marks = float(ex.get('max_marks', 0) or 0)
            except (ValueError, TypeError):
                max_marks = 0.0

            obtained = marks + bonus
            pct = (obtained / max_marks * 100) if max_marks > 0 else 0.0

            details.append({
                'exam_id': ex.get('exam_id', ''),
                'exam_name': ex.get('exam_name', ''),
                'subject': ex.get('subject', ''),
                'marks': marks,
                'bonus': bonus,
                'max_marks': max_marks,
                'percentage': round(pct, 2)
            })

            total_obtained += obtained
            total_max += max_marks

        if total_max == 0:
            return 0.0, details

        avg_pct = round((total_obtained / total_max) * 100, 2)
        return avg_pct, details

        
        
    def student_exam_report(self, student_id):
        student = self.find_student_by_id(student_id)
        if not student:
            print(Fore.RED + f"❌ Student {student_id} not found.\n")
            return

        avg_percent, details = self.calculate_student_percentage(student_id)

        print_section(f"Exam Report for {student.name} ({student.get_student_id()})", Fore.CYAN)

        if not details:
            print(Fore.YELLOW + "ℹ️ No exam results found for this student.\n")
            print(Fore.CYAN + f"Overall Percentage: {avg_percent:.2f}%\n")
            return

        table = []
        for d in details:
            table.append([
                d['exam_id'],
                d['exam_name'],
                d['subject'],
                d['marks'],
                d['bonus'],
                d['max_marks'],
                f"{d['percentage']:.2f}%"
            ])

        headers = ['Exam_ID', 'Exam_Name', 'Subject', 'Marks', 'Bonus', 'Max_Marks', 'Exam %']
        print(tabulate(table, headers, tablefmt=TABLE_FMT, stralign='center'))
        print()

        print(Fore.CYAN + f"📊 Overall Percentage (weighted): {avg_percent:.2f}%")

        # Map overall percentage to grade
        if avg_percent >= 90:
            grade = 'A+'
        elif avg_percent >= 80:
            grade = 'A'
        elif avg_percent >= 70:
            grade = 'B+'
        elif avg_percent >= 60:
            grade = 'B'
        elif avg_percent >= 50:
            grade = 'C'
        else:
            grade = 'F'

        print(Fore.GREEN + f"Grade: {grade}\n")
        
    def quick_dashboard_stats(self):
        print_section("📊 DASHBOARD SUMMARY", Fore.MAGENTA)
        total_days = len(self.attendance)
        total_students = len(self.students)
        # Use actual recorded cells as denominator to avoid inaccuracies when some entries are missing
        total_possible = sum(len(records) for records in self.attendance.values()) if self.attendance else 0

        # Count actual present entries across all recorded days
        total_present = sum(
            1
            for records in self.attendance.values()
            for status in records.values()
            if status == 'Present'
        )

        attendance_percent = (total_present / total_possible * 100 ) if total_possible else 0
        
        
        print(Fore.CYAN + f"📅 Attendance days recorded: {total_days}")
        print(Fore.GREEN + f"Attendance Percentage: {attendance_percent:.2f}")
        
        
        pending_count = sum( 1 for stu in self.students if str(stu.fee_status).lower() == 'pending')
        print(Fore.YELLOW + f"🫰 Students with pending fees: {pending_count}")
        
        today = datetime.today().date()
        upcoming = []
        for exam in self.exams:
            exam_date_str = exam.get('date', '')
            try:
                exam_date = datetime.strptime(exam_date_str, '%Y-%m-%d').date()
                delta_days = (exam_date - today).days
                if 0 <= delta_days <= 7:
                    upcoming.append(exam)
            except Exception:
                continue
        
        if upcoming:
            print(Fore.BLUE + f"📚 Upcoming exams (next 7 days): {len(upcoming)}")
            for ex in upcoming:
                print(f"  - {ex.get('exam_name','untitled')} on {ex.get('date')}")
        else:
            print(Fore.BLUE + "📚 No upcoming exams in the next 7 days.")
            
    
    def export_students_csv(self, filename = 'student_export.csv'):
        unique_subject = set()
        for stu in self.students:
            unique_subject.update(stu.marks.keys())
        subject_list = sorted(unique_subject)
        
        headers = ['Student ID', 'Name', 'Class', 'Phone', 'Email', 'Fee_status', 'Paid Amount'] + subject_list + ['Grade']

        
        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                
                for stu in self.students:
                    row = {
                            'Student ID': stu.get_student_id(),
                            'Name': stu.name,
                            'Class': stu.class_section,
                            'Phone': stu.contact_info.get('Phone', ''),
                            'Email': stu.contact_info.get('Email', ''),
                            'Fee_status': stu.fee_status,
                            'Paid Amount': stu.paid_amount,
                            'Grade': stu.calculate_grade() or 'N/A'
                    }
                    
                    for subject in subject_list:
                        row[subject] = stu.marks.get(subject, '')
                    writer.writerow(row)
            print(Fore.GREEN + f'✅ Exported {len(self.students)} students to {filename} ')
        except Exception as e:
            print(Fore.RED + f"❌ Export Failed {e}")
    
    def import_students_csv(self, filename='students_export.csv'):
        try:
            with open(filename, 'r') as f:
                Reader = csv.DictReader(f)
                required = ['Name']
                # flexible regarding Student ID: if provided use it, otherwise generate
                imported = 0
                skipped = 0
                for row in Reader:
                    if not row:
                        continue
                    student_id = (row.get('Student ID') or '').strip()
                    name = (row.get('Name') or '').strip()
                    if not name:
                        skipped += 1
                        continue
                    class_section = (row.get('Class') or 'N/A').strip()
                    phone = (row.get('Phone') or '').strip()
                    email = (row.get('Email') or '').strip()
                    fee_status = (row.get('Fee_status') or 'Pending').strip()
                    try:
                        paid_amount = float(row.get('Paid Amount') or 0.0)
                    except Exception:
                        paid_amount = 0.0

                    if student_id:
                        # if a student with same id exists, skip to avoid duplicates
                        if self.find_student_by_id(student_id):
                            skipped += 1
                            continue
                    else:
                        student_id = self.generate_student_id()

                    contact_info = {'Phone': phone, 'Email': email}   
                    stu = Student(name , contact_info, student_id)
                    stu.class_section = class_section
                    stu.fee_status = fee_status
                    stu.paid_amount = paid_amount
                    
                    marks = {}
                    for key in row:
                        if key not in ['Student ID', 'Name', 'Class', 'Phone', 'Email', 'Fee_status', 'Paid Amount', 'Grade']:
                            val = row.get(key)
                            if val is None or val == '':
                                continue
                            try:
                                marks[key] = float(val)
                            except Exception:
                                # skip non-numeric mark fields
                                continue
                    stu.marks = marks
                    self.students.append(stu)
                    imported += 1
            # refresh counters and mark dirty
            self.data_changed = True
            self._update_last_ids()
            print(Fore.GREEN + f"✅ Imported {imported} students from {filename} (skipped {skipped} rows).")
        except FileNotFoundError:
            print(Fore.RED + f"❌ Import failed: File not found ({filename})")
        except Exception as e:
            print(Fore.RED + f"❌ Import failed: {e}")
            
            
    def export_teachers_csv(self, filename = 'teachers_export.csv'):
        # Use keys that match the rows (Role_Description vs Role Description)
        headers = ['Teacher ID', 'Name', 'Role_Description', 'Phone', 'Email', 'Subjects']
        
        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                
                for t in self.teachers:
                    row = {
                            'Teacher ID': t.get_teacher_id(),
                            'Name': t.name,
                            'Role_Description': t.role_description,
                            'Phone': t.contact_info.get('Phone', ''),
                            'Email': t.contact_info.get('Email', ''),
                            'Subjects': ", ".join(t.subject_assigned) if t.subject_assigned else 'N/A'
                    }
                    writer.writerow(row)
            print(Fore.GREEN + f'✅ Exported {len(self.teachers)} teachers to {filename} ')
        except Exception as e:
            print(Fore.RED + f"❌ Export Failed {e}")
            
    def import_teachers_csv(self, filename='teachers_import.csv'):
        try:
            with open(filename, 'r') as f:
                Reader = csv.DictReader(f)
                imported = 0
                skipped = 0
                for row in Reader:
                    if not row:
                        continue
                    teacher_id = (row.get('Teacher ID') or '').strip()
                    name = (row.get('Name') or '').strip()
                    if not name:
                        skipped += 1
                        continue
                    role_desc = row.get('Role_Description') or row.get('Role Description') or ''
                    phone = (row.get('Phone') or '').strip()
                    email = (row.get('Email') or '').strip()
                    subjects = row.get('Subjects') or ''

                    if teacher_id:
                        if self.find_teacher_id(teacher_id):
                            skipped += 1
                            continue
                    else:
                        teacher_id = self.generate_teacher_id()

                    contact_info = {'Phone': phone, 'Email': email}   
                    subjects_list = [s.strip() for s in subjects.split(',')] if subjects else []
                    
                    teacher = Teacher(name , contact_info, teacher_id, subjects_list )
                    teacher.role_description = role_desc or 'Teacher'
                    self.teachers.append(teacher)
                    imported += 1
                self.data_changed = True
                self._update_last_ids()
                print(Fore.GREEN + f"✅ Imported {imported} teachers from {filename} (skipped {skipped} rows).")
        except FileNotFoundError:
            print(Fore.RED + f"❌ Import failed: File not found ({filename})")
        except Exception as e:
                print(Fore.RED + f"❌ Import failed: {e}")
    
    
    def export_attendance_csv(self, filename='attendance_export.csv'):
        headers = ['Date', 'Student ID', 'Name', 'Status']

        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()

                for date, records in self.attendance.items():
                    for student_id, status in records.items():
                        student = self.find_student_by_id(student_id)
                        name = student.name if student else 'Unknown'
                        row = {
                            'Date': date,
                            'Student ID': student_id,
                            'Name': name,
                            'Status': status
                        }
                        writer.writerow(row)

            print(Fore.GREEN + f"✅ Exported attendance records to {filename}")
        except Exception as e:
            print(Fore.RED + f"❌ Export failed: {e}")
            
    def import_attendance_csv(self, filename='attendance_import.csv'):
        try:
            with open(filename, 'r') as f:
                reader = csv.DictReader(f)
                imported = 0
                for row in reader:
                    if not row:
                        continue
                    date = (row.get('Date') or '').strip()
                    student_id = (row.get('Student ID') or '').strip()
                    status = (row.get('Status') or '').strip()

                    if not date or not student_id or not status:
                        continue

                    # normalize status
                    status_norm = 'Present' if status.lower().startswith('p') else 'Absent'
                    if date not in self.attendance:
                        self.attendance[date] = {}
                    self.attendance[date][student_id] = status_norm
                    imported += 1
            self.data_changed = True
            print(Fore.GREEN + f"✅ Imported {imported} attendance records from {filename}")
        except FileNotFoundError:
            print(Fore.RED + f"❌ Import failed: File not found ({filename})")
        except Exception as e:
            print(Fore.RED + f"❌ Import failed: {e}")

    def export_exams_csv(self, filename='exams_export.csv'):
        headers = ['Exam ID', 'Exam Name', 'Class', 'Subject', 'Date', 'Max Marks', 'Allow Bonus']

        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()

                for exam in self.exams:
                    row = {
                        'Exam ID': exam.get('exam_id', 'N/A'),
                        'Exam Name': exam.get('exam_name', 'N/A'),
                        'Class': exam.get('class', 'N/A'),
                        'Subject': exam.get('subject', 'N/A'),
                        'Date': exam.get('date', 'N/A'),
                        'Max Marks': exam.get('max_marks', 100),
                        'Allow Bonus': exam.get('allow_bonus', False)
                    }
                    writer.writerow(row)

            print(Fore.GREEN + f"✅ Exported {len(self.exams)} exams to {filename}")
        except Exception as e:
            print(Fore.RED + f"❌ Export failed: {e}")
    
    
    def import_exams_csv(self, filename='exams_import.csv'):
        try:
            with open(filename, 'r') as f:
                reader = csv.DictReader(f)
                imported = 0
                for row in reader:
                    if not row:
                        continue
                    exam_id = (row.get('Exam ID') or '').strip()
                    exam_name = (row.get('Exam Name') or '').strip()
                    class_name = (row.get('Class') or '').strip()
                    subject_raw = (row.get('Subject') or '').strip()
                    date = (row.get('Date') or '').strip()
                    max_marks_raw = row.get('Max Marks') or row.get('Max Marks', 100)
                    allow_bonus_raw = (row.get('Allow Bonus') or 'n').strip().lower()

                    if not exam_id:
                        exam_id = self.generate_exam_id()
                    try:
                        max_marks = float(max_marks_raw or 100)
                    except Exception:
                        max_marks = 100.0
                    allow_bonus = allow_bonus_raw in ('y', 'yes', 'true', '1')

                    # if subject contains commas, take first as canonical subject, but store original if needed
                    subject = subject_raw.split(',')[0].strip() if subject_raw else ''

                    exam = {
                        'exam_id': exam_id,
                        'exam_name': exam_name or '',
                        'class': class_name or '',
                        'subject': subject,
                        'date': date,
                        'max_marks': max_marks,
                        'allow_bonus': allow_bonus,
                        'results': {}
                    }
                    self.exams.append(exam)
                    imported += 1
                self.data_changed = True
                self._update_last_ids()
                print(Fore.GREEN + f"✅ Imported {imported} exams from {filename}")
        except FileNotFoundError:
            print(Fore.RED + f"❌ Import failed: File not found ({filename})")
        except Exception as e:
            print(Fore.RED + f"❌ Import failed: {e}")
    
    def export_fee_transactions_csv(self, filename='fee_transactions_export.csv'):
        headers = ['Student ID', 'Name', 'Amount', 'Date', 'Method']

        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()

                for txn in self.fee_transactions:
                    student = self.find_student_by_id(txn.get('student_id'))
                    name = student.name if student else 'Unknown'
                    row = {
                        'Student ID': txn.get('student_id', 'N/A'),
                        'Name': name,
                        'Amount': txn.get('amount', 0.0),
                        'Date': txn.get('date', 'N/A'),
                        'Method': txn.get('method', 'N/A')
                    }
                    writer.writerow(row)

            print(Fore.GREEN + f"✅ Exported {len(self.fee_transactions)} fee transactions to {filename}")
        except Exception as e:
            print(Fore.RED + f"❌ Export failed: {e}")
    
    def import_fee_transactions_csv(self, filename='fee_transactions_import.csv'):
        try:
            with open(filename, 'r') as f:
                reader = csv.DictReader(f)
                imported = 0
                for row in reader:
                    if not row:
                        continue
                    student_id = (row.get('Student ID') or '').strip()
                    try:
                        amount = float(row.get('Amount') or 0.0)
                    except Exception:
                        amount = 0.0
                    date = (row.get('Date') or 'N/A').strip()
                    method = (row.get('Method') or 'N/A').strip()

                    txn = {
                        'student_id': student_id,
                        'amount': amount,
                        'date': date,
                        'method': method
                    }
                    self.fee_transactions.append(txn)
                    imported += 1
                self.data_changed = True
                print(Fore.GREEN + f"✅ Imported {imported} fee transactions from {filename}")
        except FileNotFoundError:
            print(Fore.RED + f"❌ Import failed: File not found ({filename})")
        except Exception as e:
            print(Fore.RED + f"❌ Import failed: {e}")