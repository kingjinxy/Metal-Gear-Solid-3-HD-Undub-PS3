"""
Undubs audio across all files in .sdt files for MGS3 (Snake Eater HD Edition)

This is the core file which drives the actual total undubbing process.
This script will:
1) Navigate the folder structures
2) Copy Japanese audio over US audio (.sdt files)
3) Create a new identical folder structure with the new Japanese audio + General Subtitles

Written by Matthew Tran (giantlightbulb@gmail.com) 
"""
import os
import sys
import pathlib
import traceback
from smart_file_undub import smart_stitch

def copy_over_directory(japanese_folder, us_folder, output_folder):
    """
    Overwrites all US audio with Japaneses audio over a file structure. Completely rebuilds the file structure.
    Utilizes smart_file_undub to properly interleave audio tracks in the files.
    Should be flexible for all .sdt's in MGS3
    """
    """
    Force Absolute Paths
    """
    japanese_folder = pathlib.Path(japanese_folder).absolute().__str__()
    us_folder = pathlib.Path(us_folder).absolute().__str__()
    output_folder = pathlib.Path(output_folder).absolute().__str__()


    """
    Basic Setup
    """
    us_path = pathlib.Path(us_folder)
    us_folder_name = us_path.parts[-1]

    file_extension = ".sdt"
	
    """
    Find all paths for all files in the japanese folder
    """
    japanese_paths = []
    japanese_files = []
    
    for dir_path, dir_names, files in os.walk(japanese_folder):
        for file in files:
            japanese_paths.append(dir_path)
            japanese_files.append(file)

    """
    Iterate over all files and subfiles
    """
    n_files = 0
    n_failed_files = 0
    for dir_path, dir_names, files in os.walk(us_folder):
        """
        Setup the output directory paths
        """
        true_dir_path = pathlib.Path(dir_path).absolute()
        index = true_dir_path.parts.index(us_folder_name) # find the index in which the us_folder occurs
        sub_directories = "\\".join(true_dir_path.parts[index + 1:]) # copy all remaining subdirectory paths

        output_path = f"{output_folder}\\{sub_directories}"
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        
        print(f"\tCopying for {dir_path}")
        
        # iterate over files in the directory
        for file in files:
            n_files += 1
            file_path = pathlib.Path(file)
            file_name = file_path.name
            try:
                # make sure we're working with .sdt files
                if file_path.suffix == file_extension:
                    # copy the Japanese audio over the English audio and write to a new file in the output folder
                    index = japanese_files.index(file)
                    
                    if index == -1:
                        raise Exception(f"{dir_path}\\{file_path} not found in Japanese files")
                    
                    japanese_file = f"{japanese_paths[index]}\\{japanese_files[index]}"
					
                    us_file = f"{dir_path}\\{file}"
                    output_data = smart_stitch(japanese_file, us_file)

                    """
                    # dumb over copy, blindly acts based on a magic line
                    japanese_file = open(f"{japanese_folder}\\{sub_directories}\\{file}", "rb")
                    english_file = open(f"{dir_path}\\{file}", "rb")
                    japanese_data = japanese_file.read()
                    english_data = english_file.read()

                    output_data = copy_audio_bytes(japanese_data, english_data)

                    japanese_file.close()
                    english_file.close()
                    """

                    with open(f"{output_path}\\{file_name}", "wb") as output_file:
                        output_file.write(output_data)

                    
            except Exception as e:
                print(traceback.format_exc())
                print(f"Unable to Copy Data Over for {dir_path}\\{file}")
                n_failed_files += 1
    
    print(f"Proportion of Failed Files: {n_failed_files/n_files}")

if __name__ == "__main__":
    print("Usage:")
    print("python main.py us_folder japanese_folder output_folder_path")
    if len(sys.argv) == 4:
        us_folder = sys.argv[1]
        japanese_folder = sys.argv[2]
        output_folder = sys.argv[3]
    else:
        us_folder = "./us/"
        japanese_folder = "./japanese/"
        output_folder = "./output/"
    print()

    print("Copying Japanse Audio Over US Audio")
    print(f"{japanese_folder} and {us_folder} to {output_folder}")
    
    copy_over_directory(japanese_folder, us_folder, output_folder)