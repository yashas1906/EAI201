print("AI Assistant for Standard Grade Assignment")
student_id = int(input("Enter the student ID: "))
subject = input("Enter the subject: ")
marks = int(input("Enter the marks: "))
if marks > 85 or marks <= 100:
    grade = 'A+'
elif marks > 75 or marks <= 85:
    grade = 'A'
elif marks > 55 or marks <= 75:
    grade = 'B+' 
elif marks > 45 or marks <= 55:
    grade = 'B'
elif marks >= 35 or marks <= 45:
    grade = 'C'
elif marks >= 25 or marks <= 35:
    grade = 'C+'
elif marks >= 0 or marks <= 25:
    grade = 'W'
else:
    grade = 'Invalid marks'

print("Grade assigned based on marks:")
print("Student ID:", student_id)
print("Subject:", subject)
print("Marks:", marks)
print("Grade:", grade)
print("Thank you for using the AI Assistant")