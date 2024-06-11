# Extractor.py
This program takes the submission.zip from the downloads directory and uses it to create an eclipse project
# Requires
The default behavior requires;
* submissions.zip (download from carmen) is located in the Downloads directory.
* extractor.py is located in the softwaregradingtools directory
* https://cse22x1.engineering.osu.edu/common/OsuCseWsTemplate.zip is still a valid link

# Usage
* You can import the submissions folder into eclipse
  * It is advised that you close eclipse before running the program
  * Run program to create submissions directory
  * If not imported: import submissions directory into eclipse
  * Sometimes the eclipse config will get messed up (if it tries to write the config as the program is making a new config), just delete all the files and then rerun and import
* prompted input
  * Use default configs
  * Project number -> in default state will call ./CSE_References/Project{Project_number}/test/* to get test cases
* command line input
  1. defaults, (y or n)
  2. Project number [number]
  3. (optional) d -> if added will delete the submissions.zip in the Downloads folder after use
* Non-default state
  * defaults are stored in defaults.json
  * can be modified there or in the program
  * Submissions will be stored in sub_dir
  * test_location assumes that a directory exists $test_location/Project{project_number}/tests/* where test cases are located
# sample
default run: will be prompted
```
python extractor.py
```
Command line arguments less than 2 are ignored, so runs like prompted input
```
python extractor.py y
```
Calls default behavior and uses project 2
```
python extractor.py y 2
```
Deletes the submissions.zip after completion
```
python extractor.py y 2 d
```


