# Metal-Gear-Solid-3-HD-Undub-PS3
This project aims to "undub" Metal Gear Solid 3: HD Edition for PS3. Undubbing is the process of restoring the original language audio track to a movie or game. In this case, the English audio from Metal Gear Solid 3 HD (MGS3HD) is replaced with the Japanese audio from MGS3HD. The quality of each language's dub is debatable, but this project aims to give players the choice to play with Japanese audio and English/Spanish/French/Italian/German subtitles.

*What does this project do, technically speaking?*

MGS3HD stores almost all of its files in one large (~9GB) PSARC file, or PlayStation ARChive. The PSARC.exe application compresses MGS3HD's files with version 1.4 of the PSARC format, using zlib compression at level 9 and absolute path names.

Inside this PSARC are many thousands of files, but the ones used in this project are found in the `jp` folder in the Japanese version of MGS3HD (MGS3HDJPN). All the files modified have the extension `.sdx` or `.sdt`, which are assumed to be named Stream Data, given their contents.

The SDT/SDX files contain one or more of the following: `.m2v` video, `.vag`, `.msf`, or `.psq` audio, `.dmx`, `.bpx`, `.pbac`, and other unidentified files. More investigation is required, but it is believed that the DMX files are subtitles for SDTs containing radio calls, and the BPX files are animation data for said radio calls. In SDTs for in-game cutscenes (demos), it is assumed that unknown BIN files are images of text (opening credits, voice actor introductions). PBACs are almost certainly subtitles in these demos, as opening them with Notepad plainly shows text.

Undubbing the US version of the game is not as simple as replacing the entire PSARC, as the game will crash on boot. It is also not as simple as replacing the SDT files blindly, as the equivalent files in both versions are not necessarily in the same folders, and the audio portions are not necessarily in the same place in each file.

The audio needs to be extracted from the Japanese SDTs and stitched into the US SDTs, and in the case of the radio SDTs, the audio and subtitles need to be interleaved.

However, the SDX files can be copied straight from the Japanese version into the US version.

*Which files need to be dealt with?*

Inside the `jp` folder, the `demo` folder (cutscenes) contains other folders that contain SDTs. The SDTs on the top level of the `demo` folder are the same across both versions. The `movie` folder (FMVs) works much the same way, but all the SDTs contain video along with the audio. The `stage` folder contains many files related to 3D models, textures, and audio, but the Japanese SDX files just need to be copied to their equivalent folders in the US version. The `vox` folder contains equivalent files, but they are arranged in a different folder structure; the script accounts for this.

*What are some of the issues with the undub right now?*

The good news is that the demos and FMVs work pretty well. Subtitle timing is not perfect, but it is usually close. The bad news is that the radio calls quickly incur audio and video desync. Audio can get cut off, or can end well before the subtitles do. The lip sync in these calls is also wrong, and seems to represent the US version. It is predicted that the lip sync issue can be fixed by copying the Japanese BPX files into the US version's SDTs. More research has to be done to edit DMX/PBAC files and subtitle timing.

Testing has been done on both real PS3 hardware and RPCS3, but the entire game (100% of radio calls, demos, and FMVs) has not been tested; testing is ongoing. Softlocks *should* not happen, as radio calls can be manually advanced with the Circle button if need be.

*How is this installed?*

All of this is subject to change, as alternative applications need to be found for the PSARC creation and PS3 PKG creation, but this is the way used right now:

1. Acquire `.pkg` and `.rap` files for both MGS3HD US and JPN versions.
2. PKG SHA-1 file hashes: `42e0ba9efab78b32e81cf6a13f95fd7f4ba8220f` for the US version, `e39b0a4ceac0affbf771497ba51e68190522d8ce` for the Japanese version.
3. Download `main.py` and `smart_file_undub.py` from this repository, putting them in the same folder.
4. Download Total Commander [https://www.ghisler.com/] and install the PSARC plugin: [https://totalcmd.net/plugring/PSARC.html] An alternative will be found later, but you have a month to use Total Commander.
5. Install the US PKG and requisite RAP to your PS3 or RPCS3.
6. Install PS3 Tools and open PS3 Package GUI.
7. Open the US PKG and extract the `mgs3.psarc` file to somewhere easily accessible; do the same with the `mgs3_jp.psarc` in the JPN PKG.
8. Open PS3 Tools again and open PS3PSARC GUI.
9. Open the `mgs3.psarc` file and extract all of its files to a folder (e.g. `mgs3_us`); do the same with the `mgs3_jp.psarc`, extracing its files to a different folder (e.g. `mgs3_jpn`).
10. Run `main.py` in the command line with the syntax of `python main.py mgs3_us mgs3_jpn output_folder` over the folders described below. Copy all folders from the US version to the `output_folder` **EXCEPT** the `us` folder.
11. Inside the `output_folder`, create a `us` folder, and copy all the folders from `mgs3_us/us` **EXCEPT** `demo`, `movie`, and `vox`. Create empty folders for these exceptions.
12. Run the script on `mgs3_us/us/demo`, `mgs3_jpn/jp/demo`, and `output_folder/us/demo`. You should see the output folder structure match that of the US version. Copy the SDTs found in the root of the `mgs3_us/demo` to `output_folder/us/demo`.
13. Run the script again on `mgs3_us/us/movie`, `mgs3_jpn/jp/movie`, and `output_folder/us/movie`.
14. Run the script again on `mgs3_us/us/vox`, `mgs3_jpn/jp/vox`, and `output_folder/us/vox`.
15. The annoying part: in many (but not all) folders in the `stage` folder have `.sdx` files. Copy each SDX file in `mgs3_jpn/jp/stage/*` to `output_folder/us/stage/*`. Each file goes to its equivalent folder. This is tedious, and will be automated later.
16. Open Total Commander (TC) and navigate to the PSARC plugin; open it with TC to install it.
17. Navigate to the `output_folder` and mark all the folders inside it. (`fr`, `gr`, `it`, `slot`, etc.)
18. `File>Pack...` opens the "Pack files" dialogue.
19. Leave only `Recursively pack subdirectories` checked, then change the `Packer` to `psarc`, then click `Configure...`
20. Change `PSARC Version` to `1.4`, `Compression` to `ZLIB`, `Ratio` to `9`, and leave only `Absolute Path Names (starting with /)` checked, then click `OK`.
21. Make sure the archive output path is valid. Try changing the path to somewhere not in the root (e.g. `C:\`).
22. Click OK and wait, as the packing can take a while.
23. Rename the output to `mgs3.psarc` and replace the original file in the `NPUB30610/USRDIR/MGS3` installation folder for the US game. In RPCS3, this can easily be found by right-clicking the game in the Game List and choosing `Open Install Folder`.
24. If everything went right, the game should be able to get to the title screen without issue.
