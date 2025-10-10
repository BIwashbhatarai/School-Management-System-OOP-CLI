from classes import Person, Student, Teacher, Admin

# Person
p1 = Person("Biwash Bhattarai", {'Phone': 9090909090, 'Email': 'biwashbhattarai252@gmail.com'})
print(p1)

# Student
s1 = Student("Ram Sharma", {'Phone': 9876543210, 'Email': 'ram@school.com'}, 101)
s1.marks['Math'] = 95
print(s1)

# Teacher
t1 = Teacher("Sita Koirala", {'Phone': 9123456780, 'Email': 'sita@school.com'}, 201, ['Math','Science'])
print(t1)

# Admin
a1 = Admin("Hari Sharma", {'Phone': 9112233445, 'Email':'hari@school.com'}, 301)
print(a1)
