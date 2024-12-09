
def open_file(file_name):
    try:
        with open(file_name) as f:
            text = f.read().splitlines()
        return text, None
    except PermissionError:
        return None, f"Permission denied to open the file: {file_name}"
    except Exception:
        return [''], None


def save_file(file_name, text):
    try:
        with open(file_name, 'w') as f:
            for line in text:
                f.write(line + '\n')
        return True, None
    except PermissionError:
        return False, f'Permission denied to save file: {file_name}'
    except Exception:
        return False, f'Unexpected Error: while saving file: {file_name}'
