import os

class StudentManager:
    def __init__(self, data_file='src/data/students.json'):
        self.data_file = data_file
        self.students = self.load_students()

    def load_students(self):
        import json
        try:
            with open(self.data_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return data.get("students", [])
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []

    def add_student(self, student_id, name, facial_data):
        new_student = {
            'id': student_id,
            'name': name,
            'facial_data': facial_data
        }
        self.students.append(new_student)
        self.save_students()

    def update_student(self, student_id, name=None, facial_data=None):
        for student in self.students:
            if student['id'] == student_id:
                if name is not None:
                    student['name'] = name
                if facial_data is not None:
                    student['facial_data'] = facial_data
                self.save_students()
                return True
        return False

    def save_students(self):
        # Tạo thư mục cha nếu chưa tồn tại
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w', encoding='utf-8') as file:
            import json
            json.dump({"students": self.students}, file, ensure_ascii=False, indent=2)

    def get_student(self, student_id):
        for student in self.students:
            if student['id'] == student_id:
                return student
        return None

    def get_all_students(self):
        return self.students