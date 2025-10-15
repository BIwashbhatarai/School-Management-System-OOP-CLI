import json
import os

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
        print(f"✅ {self.name} fee status updated to paid.")
    
    def to_dict(self):
        base = super().to_dict()
        base.update({
            "student_id": self.__student_id,
            "marks": self.marks,
            "fee_status": self.fee_status,
            "class_section": self.class_section
        })
        return base
    def get_student_id(self):
        return self.__student_id
    def set_student_id(self, new_id):
        self.__student_id = new_id
    def __str__(self):
        base_info = super().__str__()
        grade = self.calculate_grade()
        return f"{base_info}, Student ID: {self.__student_id}, Fee: {self.fee_status}, Marks: {self.marks}, Grade: {grade if grade else "N/A"}"

class Teacher(Person):
    def __init__(self, name , contact_info, teachers_id, subject_assigned = None):
        super().__init__( name, contact_info, role='Teacher')
        self.__teachers_id = teachers_id
        if subject_assigned is None:
            subject_assigned = []
        self.subject_assigned = subject_assigned
        self.role_description = "Teacher"
        
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
            'subjects': self.subject_assigned
        }
    def __str__(self):
        base_info = super().__str__()
        return f"{base_info}, Teachers_ID: {self.__teachers_id}, Subject_Assigned: {self.subject_assigned}"
    
class Admin(Person):
    def __init__(self, name , contact_info, admin_id):
        super().__init__( name, contact_info, role='Admin')
        self.__admin_id = admin_id
        self.permissions = ["Manage Students", "Manage Teachers", "Generate Reports"]
    def get_admin_id(self):
        return self.__admin_id
    def set_admin_id(self,new_id):
        self.__admin_id = new_id
    def __str__(self):
        base_info = super().__str__()
        return f"{base_info}, Admin ID: {self.__admin_id}, Permissions: {self.permissions} " 

class SchoolManager:
    def __init__(self):
        self.students = []
        self.last_student_id = 0
        self.teachers = []
        self.last_teacher_id = 0
        self.data_file = 'school_data.json'
    
    def generate_student_id(self):
        self.last_student_id += 1
        return f"STU{self.last_student_id:03d}"
    
    def generate_teacher_id(self):
        self.last_teacher_id += 1
        return f"TCH{self.last_teacher_id:03d}"
        
        
    def add_student(self):
        print("\n --- Add Students --- \n")
        name = input("Enter student name :")
        phone = input("Enter phone number :" )
        email = input("Enter email: ")
        class_section = input("Enter class section: ")
        
        Student_id = self.generate_student_id()
        
        contact_info = {'Phone': phone, 'Email': email}
        
        new_student = Student(name, contact_info, Student_id)
        new_student.class_section = class_section
        self.students.append(new_student)
        print(f"✅ Student {name} ({Student_id}) added successfully.\n ")
    
    def list_students(self):
        print("\n--- All Students ---\n")
        if not self.students:
            print("No students found.\n")
            return

        # Header
        print(f"{'ID':<8} {'Name':<20} {'Class':<10} {'Phone':<15} {'Fee':<10} {'Marks':<10}")
        print('-' * 75)

        # Data
        for stu in self.students:
            print(f"{stu.get_student_id():<8} {stu.name:<20} {getattr(stu, 'class_section', 'N/A'):<10}"
                f"{stu.contact_info['Phone']:<15} {stu.fee_status:<10} {stu.marks}")
        print()

    def find_student_by_id(self, student_id):
        for stu in self.students:
            if stu.get_student_id() == student_id:
                return stu
        return None

    def update_student(self):
        print("\n--- Update Student ---")
        student_id = input("Enter Student ID to update: ")
        stu = self.find_student_by_id(student_id)
        
        if not stu:
            print(f"❌ Student {student_id} not found.\n")
            return
        
        new_name = input(f"Current Name: {stu.name}\n Enter new name (Press enter to keep current): ")
        if new_name.strip():
            stu.name = new_name
            
        new_phone = input(f"Current Phone: {stu.contact_info['Phone']}\n Enter new phone (press enter to keep current): ")
        if new_phone.strip():
            stu.contact_info['Phone'] = new_phone
        
        new_class = input(f"Current Class/Section: {getattr(stu, 'class_section', 'N/A')}\nEnter new Class Section (press enter to keep current): ")

        if new_class.strip():
            stu.class_section = new_class
        print(f"✅ Student {stu.get_student_id()} updated successfully!\n")

    def delete_student(self):
        print("\n--- Delete Student ---")
        student_id = input("Enter Student ID to delete: ")
        stu = self.find_student_by_id(student_id)
        
        if not stu:
            print(f"❌ Student {student_id} not found.\n")
            return
        
        confirm = input(f"Are you sure want to delete {stu.name} ({stu.get_student_id()})? (y/n)")
        if confirm.lower() == 'y':
            self.students.remove(stu)
            print(f"Student {student_id} deleted successfully\n")
        else:
            print(f"❌ Deletion cancelled\n")
    
    def add_teachers(self):
        print("\n--- Add Teacher ----\n")
        name = input("Enter teacher name :")
        phone = input("Enter phone number :" )
        email = input("Enter email: ")
        
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
        print("\n--- All Teachers ---\n")
        if not self.teachers:
            print("No teachers found.\n")
            return
        
        #header 
        print(f"{'ID':<8} {'Name':<20} {'Role':<15} {'Phone':<15} {'Subjects':<30}")
        print('-' *90)
        
        for t in self.teachers:
            print(f"{t.get_teacher_id():<8} {t.name:<20} {t.contact_info['Phone']:<15} {','.join(t.subject_assigned):<30}")
        print()
    
    def find_teacher_id(self, teacher_id):
        for t in self.teachers:
            if t.get_teacher_id() == teacher_id:
                return t
        return None
    
    def update_teachers(self):
        print("\n---Update Teacher ---\n")
        teacher_id = input("Enter teacher id to update: ")
        t = self.find_teacher_id(teacher_id)
        
        if not t:
            print(f"❌ Teacher {teacher_id} not found")
            return
        
        new_name = input(f"Current name: {t.name}\nEnter new name(Press enter to keep current.\n)")
        if new_name.strip():
            t.name = new_name
        
        new_phone = input(f"Current phone: {t.contact_info['Phone']}\nEnter new Phone (Press enter to keep current,)")
        if new_phone.strip():
            t.contact_info['Phone'] = new_phone
            
        new_email = input(f"Current email: {t.contact_info['Email']}\nEnter new Email (Press enter to keep current,)")
        if new_email.strip():
            t.contact_info['Email'] = new_email
            
        new_role = input(f"Current role: {t.role_description}\nEnter new role (Press enter to keep current.)")
        if new_role.strip():
            t.role_description = new_role
        
        print("\n--- Update Subjects ---")
        while True:
            choice = input("Do you want to (A)dd or (R)emove or (F)inish?: ")
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
        print(f"✅ Teacher {t.get_teacher_id()} updated successfully!\n. ")        
    
    def delete_teacher(self):
        print("\n--- Delete Teacher ---\n")
        teacher_id = input("Enter teacher id to delete: ")
        t =  self.find_teacher_id(teacher_id)
        if not t:
            print(f"❌ Teacher {teacher_id} not found.\n")
            return
        
        confirm = input(f"Are you sure want to delete {t.name} {t.get_teacher_id()}? (y/n): ")
        if confirm.lower() == 'y':
            self.teachers.remove(t)
            print(f"✅ Teacher {t.get_teacher_id()} deleted Successfully!\n")
        else:
            print("❌ Deletion cancelled.\n")
        
    def save_data(self):
        data = {
            'last_student_id': self.last_student_id,
            'last_teacher_id': self.last_teacher_id,
            'students': [stu.to_dict() for stu in self.students],
            'teachers': [t.to_dict() for t in self.teachers]
        }
        
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=4)
        print("🗃️  Data saved successfully!")
        
    def load_data(self):
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            self.last_student_id = data.get('last_student_id', 0)
            self.last_teacher_id = data.get('last_teacher_id', 0)
            
            self.students = []
            for s in data.get('students', []):
                stu = Student(s['name'], s['contact'], s['student_id'])
                stu.marks = s.get('marks', {})
                stu.fee_status = s.get('fee_status', 'Pending')
                stu.class_section = s.get('class_section', 'N/A')
                self.students.append(stu)
            
            self.teachers = []
            for t_data in data.get('teachers', []):
                teacher = Teacher(t_data['name'], t_data['contact'], t_data['teacher_id'], t_data.get('subjects', []))
                teacher.role_description = t_data.get('role', 'Teacher')
                self.teachers.append(teacher)
            print("🗃️ Data loaded successfully!\n")
        except FileNotFoundError:
            print('No existing data found, starting freshh!')
    
    def manage_student_marks(self):
        print("\n---Manage Student marks---\n")
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
                    print("❌ Marks must be between 0-100.")
                    continue
            except ValueError:
                print("❌ Invalid input. Enter a number")
                continue
            stu.add_update_marks(subject ,  marks)
    
    def manage_fee(self):
        print("\n---Manage Student Fee---\n")
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
            print("❌ Fee update cancelled.")
            
    def student_report(self):
        print("\n---Student Report---\n")
        if not self.students:
            print("No student found.")
            return
        
        for stu in self.students:
            grade = stu.calculate_grade() or "N/A"
            print(f"{stu.get_student_id()} | {stu.name} | Class: {stu.class_section} | Fee: {stu.fee_status} | Marks: {stu.marks} | Grade: {grade} ")
            