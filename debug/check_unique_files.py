# find unique files in twin directory structures
import os
import sys
import pathlib
import numpy as np

def find_unique_files(first_folder, second_folder):
	first_folder = pathlib.Path(first_folder).absolute().__str__()
	first_folder_name = pathlib.Path(first_folder).parts[-1]
	
	second_folder = pathlib.Path(second_folder).absolute().__str__()
	second_folder_name = pathlib.Path(second_folder).parts[-1]
	
	unique_files = []
	anime_titties = 0
	
	for dir_path, dir_names, files in os.walk(first_folder):
		true_dir_path = pathlib.Path(dir_path).absolute()
		index = true_dir_path.parts.index(first_folder_name) # find the index in which the us_folder occurs
		sub_directories = "\\".join(true_dir_path.parts[index + 1:]) # copy all remaining subdirectory paths
		
		for file in files:
			file_path = f"{second_folder}\\{sub_directories}\\{file}"
			if not os.path.exists(file_path):
				unique_files.append(f"{first_folder}\\{sub_directories}\\{file}")
	
	return unique_files


if __name__ == "__main__":
	print("Usage:")
	print("python check_unique_files.py first_folder second_folder")
	
	if not len(sys.argv) == 3:
		print("Invalid Arugments provided. Check usage.")
	
	first_file_unique = find_unique_files(sys.argv[1], sys.argv[2])
	first_file_sizes = [os.path.getsize(file_path) for file_path in first_file_unique]
	print(first_file_unique)
	print(np.argsort(first_file_sizes))
	
	first_file_unique = np.array(first_file_unique)[np.argsort(first_file_sizes)]
	print(f"Files Exclusively found in the US Dub: {sys.argv[1]}")
	print(first_file_unique)
	print(f"Different Files: {len(first_file_unique)}")
	
	print()
	
	second_file_unique = find_unique_files(sys.argv[2], sys.argv[1])
	second_file_sizes = [os.path.getsize(file_path) for file_path in second_file_unique]
	print(f"Files Exclusively found in the Japanese Dub: {sys.argv[2]}")
	print(second_file_unique)
	print(f"Different Files: {len(second_file_unique)}")
	
    
