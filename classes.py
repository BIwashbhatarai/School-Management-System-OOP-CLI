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
        
    def get_student_id(self):
        return self.__student_id
    def set_student_id(self, new_id):
        self.__student_id = new_id
    def __str__(self):
        base_info = super().__str__()
        return f"{base_info}, Student ID: {self.__student_id}, Fee: {self.fee_status}"

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
        self.last_id = 0
    
    def generate_id(self):
        self.last_id += 1
        return f"STU{self.last_id:03d}"
    
    def add_student(self):
        print("\n --- Add Students --- \n")
        name = input("Enter student name :")
        phone = input("Enter phone number :" )
        email = input("Enter email: ")
        class_section = input("Enter class section: ")
        
        Student_id = self.generate_id()
        
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