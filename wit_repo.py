# Upload 177
from datetime import datetime
from distutils.dir_util import copy_tree, create_tree
import filecmp
import os
import random
import shutil
import sys

import graphviz


def init():
    current_location = os.path.join(os.getcwd(), ".wit")
    try:
        for directory in ("", "images", "staging_area"):
            os.mkdir(os.path.join(current_location, directory))
    except FileExistsError:
        print(" Directory '.wit' already exist!")
        return
    with open(os.sep.join([current_location, "activated.txt"]), 'w') as f:
        f.write("master")
    print("'.wit' Directory was created!")


class Compare:
    def __init__(self, source, backup, wit=True):
        self.source = source
        self.backup = backup
        self.source_list = self._get_files(self.source, wit)
        self.backup_list = self._get_files(self.backup, wit)
        self.intersected_files = self.get_intersected_files()

    def _get_files(self, path, wit=False):
        result = set()
        for i in os.walk(path):
            base = i[0].replace(path, '')
            for file in i[2]:
                if wit:
                    result.add(os.path.join(base, file))
                else:
                    if ".wit" not in base:
                        result.add(os.path.join(base, file))
        return result

    def get_missing_files(self):
        differ = self.source_list - self.backup_list
        result = []
        for file in differ:
            final = f"{os.sep}".join([self.source, file])
            result.append(final)
        return result

    def is_file_different(self):
        result = []
        for source in self.source_list:
            full_source = ''.join([self.source, os.sep, source])
            for backup in self.backup_list:
                full_backup = ''.join([self.backup, os.sep, backup])
                if source == backup:
                    if not filecmp.cmp(full_source, full_backup):
                        result.append(full_source)
        return result

    def get_intersected_files(self):
        return list(self.source_list & self.backup_list)


class Wit:
    def __init__(self, location=False):
        if not location:
            self.path = os.getcwd()
        else:
            self.path = self._is_abs_path(location)
        self.wit_exist = False
        self.staging_area = None
        self.images = None
        self.is_file = None
        self.references = None
        self.wit_location = self._find_wit_location()

    def _is_abs_path(self, location):
        if not os.path.isabs(location):
            return os.path.realpath(location)
        return location

    def _is_wit_exist(self, location):
        return os.path.exists(os.path.join(location, ".wit"))

    def _find_wit_location(self):
        root_dir = self.path.split(os.path.sep)[0] + os.path.sep
        wit_location = self.path
        while wit_location != root_dir and not self._is_wit_exist(wit_location):
            wit_location = os.path.dirname(wit_location)
        if not self._is_wit_exist(wit_location):
            print("'.wit' folder was not found!")
            return
        self.wit_exist = True
        self.is_file = os.path.isfile(self.path)
        self.staging_area = os.path.join(
            wit_location, ".wit", "staging_area")
        self.images = os.path.join(
            wit_location, ".wit", "images")
        self.references = os.path.join(wit_location, ".wit", "references.txt")
        return wit_location

    def add(self):
        if not self.wit_exist:
            return
        if self.is_file:
            path = os.path.split(self.path)[0]
        else:
            path = self.path
        relative_path = os.path.relpath(path, self.wit_location)
        des = os.path.join(self.staging_area, relative_path)
        if not self.is_file:
            if os.path.exists(des):
                shutil.rmtree(des)
            copy_tree(path, des)
        else:
            create_tree(des, path)
            shutil.copy2(self.path, des)
        print("File(s) added successfully")


class Commit(Wit):
    def __init__(self):
        super().__init__()
        if not self.wit_exist:
            return
        self.active_branch = None
        self.activated_file = os.sep.join(
            [self.wit_location, ".wit", "activated.txt"])
        self.branches_list_for_references = ""
        self.branches_list = {}
        self.new_commit_folder = None

    def _get_references_content(self):
        self.branches_list_for_references = ""
        for branch, folder in self.branches_list.items():
            self.branches_list_for_references += f"{branch}={folder}\n"

    def _get_branches_list(self):
        with open(self.references, 'r') as f:
            branches = f.readlines()
        for branch in branches:
            branch = branch.strip().split("=")
            self.branches_list[branch[0]] = branch[1]
        self.branches_list['HEAD'] = self.new_commit_folder
        if self.active_branch in self.branches_list:
            if self.branches_list[self.active_branch] == self._get__HEAD_from_references_file():
                self.branches_list[self.active_branch] = self.new_commit_folder
        self._get_references_content()

    def _commit_image_details(self):
        options = '1234567890abcdef'
        image_name = "".join(random.choices(options, k=40))
        os.mkdir(os.path.join(self.images, image_name))
        return image_name

    def _get__HEAD_from_references_file(self, commit_folder=False):
        if commit_folder:
            commit_file = f"{os.path.join(self.images, commit_folder)}.txt"
            with open(commit_file, "r") as f:
                parent = f.readline()
            return parent
        else:
            with open(self.references, "r") as f:
                parent = f.readline()
        return parent.strip().split("=")[1]

    def _write_to_file(self, path, mode, content, *args):
        with open(path, mode) as file:
            file.write(content)
        return

    def check_differences(self):
        backup_dolder = os.path.join(
            self.images, self._get__HEAD_from_references_file())
        compare = Compare(self.staging_area, backup_dolder)
        if len(compare.is_file_different()) == 0 and len(compare.get_missing_files()) == 0:
            return False
        return True

    def get_active_user(self):
        with open(self.activated_file, 'r') as f:
            self.active_branch = f.read()
        return

    def create_txt_file_for_commit(self, message, merge, commit=True):
        if commit:
            previous_commit = self._get__HEAD_from_references_file()
        else:
            previous_commit = "None"
        if not merge:
            commit_file_content = f'parent={previous_commit}\nnow={datetime.now().strftime("%a %b %d %H:%M:%S %Y ")}\nmessage={message}'
        else:
            commit_file_content = f'parent={previous_commit}, {merge}\nnow={datetime.now().strftime("%a %b %d %H:%M:%S %Y ")}\nmessage={message}'
        file_name = os.path.join(self.images, f"{self.new_commit_folder}.txt")
        self._write_to_file(file_name, "w", commit_file_content)

    def commit(self, message, merge=False):
        previous_commit = True
        if not self.wit_exist:
            print("'.wit' folder was not found!")
            return
        if os.path.exists(self.references):
            if not merge:
                if not self.check_differences():
                    print(
                        "Since last commit, no changes had been made\ncommit was cancelled!")
                    return
        else:
            previous_commit = False
        self.new_commit_folder = self._commit_image_details()
        copy_tree(self.staging_area, os.path.join(
            self.images, self.new_commit_folder))
        print(
            f"Commit action successfull!\ncomitted to folder: {self.new_commit_folder}")
        if not os.path.exists(self.references):
            self._write_to_file(
                self.references, 'w', f"HEAD={self.new_commit_folder}\nmaster={self.new_commit_folder}")
        self.get_active_user()
        self.create_txt_file_for_commit(message, merge, commit=previous_commit)
        self.branches_list = self._get_branches_list()
        self._write_to_file(self.references, 'w',
                            self.branches_list_for_references)

    def branch(self, name):
        if not self.wit_exist:
            return
        self.get_active_user()
        self._get_branches_list()
        branch_details = f'{name}={self._get__HEAD_from_references_file()}\n'
        if name in self.branches_list:
            print(f"{name} branch was already added!")
            return
        else:
            self._write_to_file(self.references, 'a', branch_details)
            print(f"{name} branch was added!")
        return


class Status(Commit):
    def __init__(self):
        super().__init__()
        if not self.wit_exist:
            return
        self.commit_id = self._get__HEAD_from_references_file()
        compare_staging_to_images = Compare(
            self.staging_area, os.path.join(self.images, self.commit_id))
        self.changes_to_be_committed = compare_staging_to_images.get_missing_files()
        self.changes_to_be_committed.extend(
            compare_staging_to_images.is_file_different())
        compare_source_to_staging = Compare(
            self.wit_location, self.staging_area, wit=False)
        self.changes_not_staged_for_commit = compare_source_to_staging.is_file_different()
        self.untracked_files = compare_source_to_staging.get_missing_files()

    def __str__(self):
        new_files = "\n ".join(self.changes_to_be_committed)
        message = f'Current commit id:\n {self.commit_id}\n'
        message += f"\nChanges to be committed:\n {new_files}\n"
        changed_files = "\n ".join(self.changes_not_staged_for_commit)
        message += f"\nChanges not staged for commit\n {changed_files}\n"
        untracked_files = "\n ".join(self.untracked_files)
        message += f"\nUntracked files\n {untracked_files}"
        return message

    def wit_rm(self):
        compare_staging_to_source = Compare(
            self.staging_area, self.wit_location)
        self.wit_rm_files = compare_staging_to_source.get_missing_files()
        if len(self.wit_rm_files) == 0:
            print("No files to be deleted!")
            return
        rm_files = "\n ".join(self.wit_rm_files)
        print(
            f"\nFiles in 'staging_area' folder that could not be found at source loacation:\n {rm_files}\n")
        rm = input("Do you want to delete them? (y\\n)").lower()
        if rm == "y":
            for file in self.wit_rm_files:
                os.remove(file)
            print("FileS deleted!")
            return
        print("Action cancelled!")
        return


class CheckOut(Status):
    def __init__(self, arg):
        super().__init__()
        if not self.wit_exist:
            return
        self._get_branches_list()
        self.image_id = self._get_commit_id(arg)
        self.commit_folder = f"{os.sep}".join([self.images, self.image_id])
        self.files = self._get_intersec()

    def _get_commit_id(self, arg):
        if arg in self.branches_list:
            self._write_to_file(self.activated_file, 'w', arg)
            print(f"{arg} branch is now active!")
            arg = self.branches_list[arg]
        else:
            self._write_to_file(self.activated_file, 'w', "")
            print("No branch is currently active!")
        self.branches_list['HEAD'] = arg
        self._get_references_content()
        return arg

    def _get_intersec(self):
        compare = Compare(self.commit_folder, self.wit_location)
        return compare.get_intersected_files()

    def _is_checkout_legal(self):
        if not self.wit_exist:
            return False
        elif len(self.changes_not_staged_for_commit) != 0 or len(self.changes_to_be_committed) != 0:
            print("Please apply 'commit'.\n Action was canccelled!")
            print(self)
            return False
        elif not os.path.exists(self.commit_folder):
            print("Folder number is in correct!")
            return False
        return True

    def copy_files(self):
        if not self.wit_exist or not self._is_checkout_legal():
            return
        for file in self.files:
            shutil.copy2(f"{os.sep}".join([self.commit_folder, file]), os.path.dirname(
                f"{os.sep}".join([self.wit_location, file])))
        print(f"Files from folder {self.image_id} copied seccessfully")
        self._write_to_file(self.references, "w",
                            self.branches_list_for_references)
        # updating staging_area
        shutil.rmtree(self.staging_area, ignore_errors=True)
        copy_tree(self.commit_folder, self.staging_area)


class Graph(Status):
    def __init__(self):
        super().__init__()
        if not self.wit_exist:
            return
        self.file = self._get__HEAD_from_references_file()

    def get_content(self, file):
        content = self._get__HEAD_from_references_file(commit_folder=file)
        if ", " in content:
            content = content.strip().split(", ")
            content[0] = content[0].split("=")[1]
        else:
            content = [content.strip().split("=")[1]]
            if content[0] == "None":
                content[0] = None
            content.append(None)
        return content

    def readFilesList(self, current_file, current_file_son, tupleList):
        current_file_name = current_file
        current_file_son_name = self.get_content(current_file)
        tupleList.append((current_file_name, current_file_son_name))
        current_file_parent1 = current_file_son_name[0]
        current_file_parent2 = current_file_son_name[1]
        if current_file_parent1 is None:
            return tupleList
        else:
            parent1_list = self.readFilesList(
                current_file_parent1, current_file, [])
            parent2_list = []
            if current_file_parent2 is not None:
                parent2_list = self.readFilesList(
                    current_file_parent2, current_file, [])
            tupleList.extend(parent1_list)
            tupleList.extend(parent2_list)
            return tupleList

    def graph(self):
        g = graphviz.Digraph('G', filename='wit_graph.gv')
        g.node_attr['style'] = 'filled'
        g.node_attr['color'] = 'lightblue'
        g.attr(rankdir='RL', size='10')
        for start in self.readFilesList(self.file, None, []):
            for end in start[1]:
                if end is not None:
                    g.edge(start[0][:6], end[:6])
        g.view()


class Merge(CheckOut):
    def __init__(self, arg):
        super().__init__(arg)
        self.commit_id = self._get_commit_id(arg)

    def _get_commit_id(self, arg):
        if arg in self.branches_list:
            arg = self.branches_list[arg]
        return arg

    def merge(self):
        if not self.wit_exist:
            return
        if len(self.changes_to_be_committed) != 0:
            print("Please commit first. action was cancelled")
            return
        copy_tree(self.commit_folder, self.staging_area)
        self.commit("Automatic from merge", merge=self.commit_id)


if len(sys.argv) > 1:
    if sys.argv[1] == "init":
        init()
    elif sys.argv[1] == "add":
        wit = Wit(sys.argv[2])
        wit.add()
    elif sys.argv[1] == "commit":
        wit = Commit()
        wit.commit(sys.argv[2])
    elif sys.argv[1] == "status":
        wit = Status()
        print(wit)
        if len(sys.argv) > 2:
            wit.wit_rm()
    elif sys.argv[1] == "checkout":
        wit = CheckOut(sys.argv[2])
        wit.copy_files()
    elif sys.argv[1] == "branch":
        wit = Commit()
        wit.branch(sys.argv[2])
    elif sys.argv[1] == "graph":
        wit = Graph()
        Graph.graph()
    elif sys.argv[1] == "merge":
        wit = Merge(sys.argv[2])
        wit.merge()
    else:
        print("Please check your parameters!")
else:
    print("No function was given as a parameter!")
# reupload
