# Wit-projects
# A python-coding learning project. Mimics basic functions of git.

# Uses:
* Manage code to control changes and versions.
* Create backups for code versions, or any other files.
* Restore your project or system to any backup that was made.
* Create 'Branches' to allow others to edit your code or files on their own version.
* Merge  two versions of backups to a single working one.
* Can be used as a backup system to any folder or file.

# Requierments:
* A working python architecture.
* The modul graphviz installed. 

Start by initiating "python init" on command prompt.
The command creats the the ".wit" directory at current loacation.

# Commands:
* All commands must be applied from command prompt, from the directory which "init" command was initiated, or its subdirectories
* All commands must be initiated with "python" ahead of them.

# Concepts:
* Staging area: a location which all future backups will be initialized from.
* Commit folder: a backup version of your files, created from staging area.
* HEAD: a system pointer that points to the last relevant commit
* Branch: a tag label user name.
* Active branch: a system pointer that points to a single branch. the active branch advances with any new commit. 

# add [your files\folders]:
* Adds files or folder from under parent directory to a 'staging area'.
* Those files will be backed up at your next commit.

# commit [optional: message]:
* Creats a backup for all the added files, with the optional given message.
* Commits are saved under "images" folder, under ".wit" folder.
* Moves the HEAD pointer and active branch to the new commit folder.

# branch [name]:
* Creates an additional branch, that points to the last commit that was made.

# checkout [commit folder\branch name]:
* Restores the staging area, and previouslly added files at working file tree.
* Moves the 'Head' pointer to given commit folder.
* If branch name is given: activates branch.

# Status [optional: rm]:
* Displays current working file tree status, compared to staging area and to the last commit.
* If rm command is given: displays deleted file tree files, and allows to delete them from staging area.

# Merge [commit folder\branch name]:
* Merges the last Head pointing commit folder and given folder\branch to a new commit folder.
* Moves the HEAD pointer and active branch to the new commit folder. 

# Graph:
* Displays the commits chain downward from the HEAD pointing commit.
