# Reliable Student Records Import & Validation Tool

import json
import os

class StudentRecordError(Exception):
    pass

def validate_student_record(record):

    if not isinstance(record, dict):
        raise StudentRecordError("Record must be a dictionary.")

    required_fields = ['student_id', 'name', 'department', 'marks']

    for field in required_fields:
        if field not in record:
            raise StudentRecordError(f"Missing required field: {field}")

    for field in ['student_id', 'name', 'department']:
        if not isinstance(record[field], str) or not record[field].strip():
            raise StudentRecordError(f"Field '{field}' must be a non-empty string.")

    marks = record['marks']

    if not isinstance(marks, list):
        raise StudentRecordError("Marks must be a list.")

    if len(marks) != 3:
        raise StudentRecordError("Marks must contain exactly 3 values.")

    for mark in marks:

        if isinstance(mark, bool):
            raise StudentRecordError("Boolean marks are not allowed.")

        if not isinstance(mark, (int, float)):
            raise StudentRecordError("Marks must be numeric.")

        if not 0 <= mark <= 100:
            raise StudentRecordError("Marks must be between 0 and 100.")

    return True



def main():

    input_file = "students_input.json"
    output_file = "students_valid.json"
    error_file = "import_errors.txt"

    accepted_records = []
    rejected_records = []

    
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            records = json.load(file)

    except FileNotFoundError:
        print("Error: Input file not found.")
        return

    except PermissionError:
        print("Error: Permission denied.")
        return

    except json.JSONDecodeError as e:
        print(f"Invalid JSON format: {e}")
        return

    except OSError as e:
        print(f"File error: {e}")
        return

    
    if not isinstance(records, list):
        print("Error: Input JSON must contain a list of student records.")
        return

    
    try:
        with open(output_file, 'r') as file:
            existing_records = json.load(file)

        if not isinstance(existing_records, list):
            print("Error: Existing output JSON must contain a list.")
            return

    except FileNotFoundError:
        existing_records = []

    except (json.JSONDecodeError, OSError) as e:
        print(f"Cannot safely read existing output: {e}")
        return

    
    existing_ids = set()

    for student in existing_records:
        if not isinstance(student, dict) or not isinstance(student.get('student_id'), str):
            print("Error: Existing output contains an invalid record.")
            return

        existing_ids.add(student['student_id'])

    
    for index, record in enumerate(records, start=1):

        try:
            validate_student_record(record)

            student_id = record['student_id']

            if student_id in existing_ids:
                raise StudentRecordError(
                    f"Duplicate student ID: {student_id}"
                )

            existing_ids.add(student_id)
            accepted_records.append(record)

            print(f"Accepted: {student_id} - {record['name']}")

        except StudentRecordError as e:

            message = f"Rejected record {index}: {e}"

            print(message)
            rejected_records.append(message)

    
    all_valid_records = existing_records + accepted_records

    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(all_valid_records, file, indent=4)

        
        with open(error_file, 'w', encoding='utf-8') as file:
            for error in rejected_records:
                file.write(error + "\n")

    except OSError as e:
        print(f"Output file error: {e}")
        return

    
    print("\n========== IMPORT SUMMARY ==========")
    print(f"Accepted records: {len(accepted_records)}")
    print(f"Rejected records: {len(rejected_records)}")
    print(f"Valid output: {output_file}")
    print(f"Error log: {error_file}")
    print("Import completed successfully.")


if __name__ == "__main__":
    main()
