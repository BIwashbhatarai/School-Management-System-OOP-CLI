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