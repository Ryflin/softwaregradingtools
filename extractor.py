import os
from pathlib import Path
import shutil
import sys
from zipfile import ZipFile
import json
import xml.etree.ElementTree as ET
import requests

# Maybe put this in json if the url is prone to change
cse_template_url = 'https://cse22x1.engineering.osu.edu/common/OsuCseWsTemplate.zip'

# this creates all the paths that are used later, and avoids hardcoding by creating defaults.json that feeds the info map. 
def startup_tasks():
  print("This program extracts files from the zip file, then moves them to a submissions folder in the current directory.")
  print("The directory being run from is the same directory as the root of the zip (the directory that contains CSE_2231_References)")
  print("Source: the location of the submisions.zip file, Default is the Downloads folder.")
  # if the sys args are not correct ask for console input
  sys_args_correct = True
  info = {}
  proj_number = 0
  # So that continue can be used to 
  while(True):
    if len(sys.argv) >= 3 and sys_args_correct:
      defaults = sys.argv[1]
      proj_number = sys.argv[2]
    else:
      defaults = input("defaults? [y/n]: ").lower()
      proj_number = input("project number? [num]: ")
    if not proj_number.isdigit():
      print("Please input a digit for project number")
      continue
    if defaults == 'y':
      # defaults so that the default behavior can be stored and altered not just hardcoded
      if not Path.exists(Path.cwd() / "defaults.json"):
        # the hard coded json
        info['template_dir'] = str(Path.cwd() / "workspace" / "ProjectTemplate")
        info['sub_dir'] = str(Path.cwd() / "submissions")
        # if on the lab computers the path needs to be written regardless
        print(Path.cwd())
        # Checks if submissions.zip is in the directory
        #if os.name == "nt" and Path.cwd().__str__().find("User") != -1:
        download_folder = Path.home() / "Downloads" / "submissions.zip"
        while not Path.exists(download_folder):
          download_folder = Path(input("Can't find the directory that submissions.zip was downloaded into, please provide: ")) / "submissions.zip"
        info['src'] = str(download_folder)
        # the others are hardcoded because they are within the zip that will be distributed
        info['test_location'] = str(Path.cwd() / "CSE_2231_References")
        with open("defaults.json", "w") as f:
          json.dump(info, f)
      else:
        # if defaults.json exists use that instead
        with open("defaults.json", "r") as f:
          info = json.load(f)
        # if the default config is incorrect get user input and rewrite
        if not Path.exists(Path(info["src"]) / "submissions.zip"):
          download_folder = input("Unable to locate downloads directory, please provide: ")
          info["src"] = Path(download_folder) / "submissions.zip"
          with open("defaults.json", "w") as f:
            json.dump(info, f)
    #only other option for valid input
    elif defaults == 'n':
      print("Rewriting defaults.")
      # delete info and try again
      info['project_number'] = input("Enter the project number: ")
      info['sub_dir'] = Path(input("Enter the destination directory: "))
      info['src'] = input("Enter the source (downloaded zip) directory: ")
      info['test_location'] = Path(input("Enter the test location: "))
      if input("Save defaults? [y/n]: ").lower() == 'y':
        with open("defaults.json", "w") as f:
          json.dump(info, f)
    else:
      print("Invalid input. Please enter 'y' or 'n'")
      sys_args_correct = False
      continue
    break
  info['test_number'] = proj_number
  return info

# Copies the .project (changing the name) .classpath and .checkstyle from the template directory
# therefore make sure that the template project is to your liking then run the script
def make_eclipse_config_from_template(template_path: Path, path: Path, project_name: str):
  # xml parsing library to change the project name
  project_template = ET.parse(template_path / ".project")
  project_template.getroot().find("name").text = project_name
  project_template.write(path / ".project")
  shutil.copyfile(template_path / ".classpath", path / ".classpath")
  shutil.copyfile(template_path / ".checkstyle", path / ".checkstyle")

# Does what says on tin. Copies test from info["test_location"] to the individual project test directories
def copy_tests_into_project(path: Path, test_location: Path):
  for file in os.listdir(test_location):
    shutil.copyfile(test_location / file, path / file)


# Does the beef of the program with the information already provided
def process_labs(info):
  # uses as submissions folder
  proj_dir = Path(info["sub_dir"])
  if not Path.exists(proj_dir):
    os.mkdir(proj_dir)
  # takes the zip in info["src"] and extracts it to the submissons folder
  ZipFile(info['src']).extractall(proj_dir)
  # begins extracting all the zips inside the submissions.zip
  for file in os.listdir(proj_dir):
    if not Path.is_dir(proj_dir / file):
      if file.endswith(".zip"):
        group_name = '_'.join(file.split("_")[0:2])
        group_dir = proj_dir / group_name
        # deletes the group project folder so that it can be rewritten
        if Path.exists(group_dir):
          shutil.rmtree(group_dir)
        ZipFile(proj_dir / file).extractall(group_dir)
        temp_assignment_name = os.listdir(group_dir)
        # if there are multiple files in the directory ask the user which one to use
        if len(temp_assignment_name) > 1:
          i = 0
          print("Found 2 potential projects")
          for name in temp_assignment_name:
            print(f"{i}: >", name)
            i += 1
          # Yes I am using different paradigms for checking user input
          while True:
            try:
              assignment_name = temp_assignment_name[int(input("Which contains the project? [int] "))]
              break
            except:
              print("Something went wrong, input could not be parsed into an integer")
              continue
          for name in temp_assignment_name:
            # print(name)
            if name != assignment_name:
              shutil.rmtree(group_dir / name)
          temp_assignment_name = assignment_name
        # if there is only one dir, use that dir
        else:
          assignment_name = temp_assignment_name[0]
        # was easier than trying to move it to a parent and doesn't really change functionality
        shutil.move(group_dir / assignment_name, group_dir / "temp")
        test_project_number = info['test_number']
        make_eclipse_config_from_template(Path(info['template_dir']), group_dir / "temp", group_name)
        copy_tests_into_project(group_dir / "temp" / "test", Path(info['test_location']) / f"Project{test_project_number}" / "test" )
        os.remove(proj_dir / file)
      elif not os.path.isdir(proj_dir / file): 
        os.remove(proj_dir / file)
  


def download_and_unzip_template(path: Path):
  if not Path.exists(path.parent):
    zip_name = Path(path.parent.name + '.zip')
    response = requests.get(cse_template_url)
    with open(zip_name, "wb") as f:
      f.write(response.content)
    # print(path)
    ZipFile(zip_name).extractall(Path.cwd())
    os.remove(Path.cwd() / zip_name)

# It is kind of default behavior to click on something once it is downloaded, which will likely run the script.
# However, since the script should not be run from the Downloads folder, this is a stopper
if not Path(__file__).parent.name == "Downloads":
  os.chdir(Path(__file__).parent)
  info = startup_tasks()
  download_and_unzip_template(Path(info['template_dir']))  
  process_labs(info)

  if not (len(sys.argv) == 4 and sys.argv[3] == 'n'):
    os.remove(info['src'])
else:
  print("Don't run from root directory")
  # in case the user cannot see the terminal output
  open("message_from_extractor.txt", "w").write("This script should be used from the softwaregradingtools directory, and you will need to provide console input")