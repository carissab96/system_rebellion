from datetime import datetime
import os

def get_copyright_header(filename):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open('templates/copyright_header.txt', 'r') as f:
        template = f.read()
    
    return template.format(
        creation_date="2024-02-22 12:22:22",  # The sacred timestamp
        update_date=current_time,
        file_name=filename
    )

def update_file_header(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Remove old header if exists
    if '"""' in content:
        content = content.split('"""', 2)[-1]
    
    # Add new header
    new_content = get_copyright_header(os.path.basename(file_path)) + content
    
    with open(file_path, 'w') as f:
        f.write(new_content)