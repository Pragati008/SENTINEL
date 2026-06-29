import os

def clear_folder(folder_path):

    os.makedirs(
        folder_path,
        exist_ok=True
    )

    for file in os.listdir(folder_path):

        file_path = os.path.join(
            folder_path,
            file
        )

        try:
            os.remove(file_path)

        except Exception as e:

            print(
                f"Could not remove {file}: {e}"
            )