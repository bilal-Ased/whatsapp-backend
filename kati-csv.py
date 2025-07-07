
import csv
import json
import os
import re
from datetime import datetime

def convert_seconds_to_readable(seconds_str):
    """Convert seconds to 'X Days Y Hours Z Min' format"""
    try:
        total_seconds = int(seconds_str)
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{days} Days {hours} Hours {minutes} Min"
    except:
        return seconds_str  # Return original if conversion fails

def convert_unix_timestamp_to_readable(timestamp_str):
    """Convert Unix timestamp to human-readable date format"""
    try:
        timestamp = int(timestamp_str)
        # Convert to datetime object
        dt = datetime.fromtimestamp(timestamp)
        # Format as readable string
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp_str  # Return original if conversion fails

def fix_json_string(content):
    """Aggressively fix JSON string issues"""
    print("Fixing JSON string issues...")
    
    # Remove all control characters except valid JSON ones
    content = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', content)
    
    # Fix invalid escape sequences by escaping backslashes that aren't part of valid escapes
    # Valid JSON escapes: \", \\, \/, \b, \f, \n, \r, \t, \uXXXX
    def fix_escapes(match):
        escaped_char = match.group(1)
        if escaped_char in ['"', '\\', '/', 'b', 'f', 'n', 'r', 't']:
            return match.group(0)  # Keep valid escapes
        elif escaped_char == 'u':
            # Check if it's a valid unicode escape \uXXXX
            full_match = match.group(0)
            if len(full_match) >= 6 and all(c in '0123456789abcdefABCDEF' for c in full_match[2:6]):
                return full_match  # Keep valid unicode escapes
        # Invalid escape - escape the backslash
        return '\\\\' + escaped_char
    
    # Fix invalid escapes
    content = re.sub(r'\\(.)', fix_escapes, content)
    
    return content

def extract_objects_with_regex(content):
    """Extract objects using regex when JSON parsing fails completely"""
    print("Attempting regex-based object extraction...")
    
    objects = []
    # Look for complete object patterns
    object_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    
    matches = re.finditer(object_pattern, content, re.DOTALL)
    
    for match in matches:
        obj_str = match.group(0)
        try:
            # Try to parse this individual object
            obj_str_cleaned = fix_json_string(obj_str)
            obj = json.loads(obj_str_cleaned)
            objects.append(obj)
        except:
            continue
    
    return objects

def filter_record(obj, desired_fields):
    """Filter record to only include desired fields"""
    filtered_obj = {}
    for field in desired_fields:
        # Use get() to avoid KeyError if field doesn't exist
        filtered_obj[field] = obj.get(field, "")
    return filtered_obj

def main():
    print("CSV Converter Starting...")
    
    # File path
    input_file = "/Users/bilalmughal/Documents/Dev/outbound-backend/response.txt"
    output_file = "/Users/bilalmughal/Documents/Dev/outbound-backend/converted_tickets.csv"
    
    # Define the specific fields you want in the CSV
    desired_fields = [
        "Created_date",
        "Ticket_number",
        "route",
        "email_subject",
        "responsible_employee",
        "age",
        "Category",
        "Disposition",
        "Sub-Disposition",
        "Customer_Name",
        "Customer_Email",
        "Ticket_Status"
    ]
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"ERROR: File does not exist: {input_file}")
        return
    
    print(f"Reading file: {input_file}")
    
    # Read the file
    try:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read().strip()
    except Exception as e:
        print(f"ERROR reading file: {e}")
        return
    
    if not content:
        print("ERROR: File is empty")
        return
    
    print(f"File content length: {len(content)} characters")
    
    # Try multiple parsing strategies
    data = []
    
    # Strategy 1: Direct JSON parsing
    try:
        print("Strategy 1: Direct JSON parsing...")
        data = json.loads(content)
        if isinstance(data, dict):
            data = [data]
        print(f"Success! Parsed {len(data)} objects")
    except Exception as e:
        print(f"Strategy 1 failed: {e}")
        
        # Strategy 2: Clean and parse
        try:
            print("Strategy 2: Cleaning and parsing...")
            cleaned_content = fix_json_string(content)
            data = json.loads(cleaned_content)
            if isinstance(data, dict):
                data = [data]
            print(f"Success! Parsed {len(data)} objects")
        except Exception as e2:
            print(f"Strategy 2 failed: {e2}")
            
            # Strategy 3: Regex extraction
            try:
                print("Strategy 3: Regex-based extraction...")
                data = extract_objects_with_regex(content)
                print(f"Extracted {len(data)} objects using regex")
            except Exception as e3:
                print(f"Strategy 3 failed: {e3}")
                
                # Strategy 4: Manual line-by-line with object reconstruction
                print("Strategy 4: Manual object reconstruction...")
                try:
                    objects = []
                    current_object = {}
                    in_object = False
                    brace_count = 0
                    
                    lines = content.split('\n')
                    current_obj_lines = []
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                            
                        # Count braces to track object boundaries
                        brace_count += line.count('{') - line.count('}')
                        current_obj_lines.append(line)
                        
                        # If we've closed all braces, we might have a complete object
                        if brace_count == 0 and current_obj_lines:
                            obj_str = ' '.join(current_obj_lines)
                            if obj_str.strip().startswith('{') and obj_str.strip().endswith('}'):
                                try:
                                    cleaned_obj = fix_json_string(obj_str)
                                    obj = json.loads(cleaned_obj)
                                    objects.append(obj)
                                except:
                                    pass
                            current_obj_lines = []
                    
                    data = objects
                    print(f"Manual reconstruction found {len(data)} objects")
                    
                except Exception as e4:
                    print(f"All strategies failed: {e4}")
                    return
    
    if not data:
        print("ERROR: Could not extract any valid objects from the file")
        return
    
    print(f"Successfully extracted {len(data)} objects")
    
    # Write CSV with filtered fields
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=desired_fields)
            writer.writeheader()
            
            converted_count = 0
            date_converted_count = 0
            
            for i, obj in enumerate(data):
                if not isinstance(obj, dict):
                    continue
                
                # Filter to only desired fields
                filtered_obj = filter_record(obj, desired_fields)
                
                # Convert Created_date from Unix timestamp to readable format
                if 'Created_date' in filtered_obj and filtered_obj['Created_date']:
                    original_date = filtered_obj['Created_date']
                    filtered_obj['Created_date'] = convert_unix_timestamp_to_readable(filtered_obj['Created_date'])
                    if date_converted_count < 3:  # Show first 3 conversions
                        print(f"Date conversion {date_converted_count+1}: {original_date} → {filtered_obj['Created_date']}")
                        date_converted_count += 1
                
                # Convert age field
                if 'age' in filtered_obj and filtered_obj['age']:
                    original_age = filtered_obj['age']
                    filtered_obj['age'] = convert_seconds_to_readable(filtered_obj['age'])
                    if converted_count < 3:  # Show first 3 conversions
                        print(f"Age conversion {converted_count+1}: {original_age} → {filtered_obj['age']}")
                        converted_count += 1
                
                # Convert lists to strings and handle any remaining issues
                for key, value in filtered_obj.items():
                    if isinstance(value, list):
                        filtered_obj[key] = ', '.join(str(v) for v in value)
                    elif isinstance(value, str):
                        # Clean any remaining problematic characters
                        filtered_obj[key] = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', str(value))
                
                writer.writerow(filtered_obj)
        
        print(f"SUCCESS: CSV file created at {output_file}")
        print(f"File size: {os.path.getsize(output_file)} bytes")
        print(f"Fields included: {', '.join(desired_fields)}")
        
    except Exception as e:
        print(f"ERROR writing CSV: {e}")

if __name__ == "__main__":
    main()