import os

def delete_old_files(directory, max_file_count):
    files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    if len(files) > max_file_count:
        files.sort(key=lambda x: os.path.getmtime(x))
        for file_to_delete in files[:len(files) - max_file_count]:
            os.remove(file_to_delete)
            print(f"Deleted file: {file_to_delete}")
