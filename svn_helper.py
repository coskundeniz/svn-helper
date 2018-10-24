import sys

if sys.version_info.major < 3:
    print("Use python3 to run the script!")
    sys.exit(1)

import datetime
import os
import subprocess


def get_requested_indexes(is_quiet):
    """Run svn status and get file indexes to process from user

    :type is_quiet: bool
    :param is_quiet: if true svn status command runs with -q parameter
    :rtype: tuple
    :returns: a tuple containing selected indexes, and svn status output
    """

    # run status command
    status_output = status(is_quiet)

    # index status output
    output = index_command_output(status_output)

    # show indexed result
    show_indexed_result(output)

    # get selected indexes from user
    if output:
        selected_indexes = input("\nEnter requested indexes: ")
    else:
        print("\nThere is no changes to show\n")
        return ([], output)

    try:
        indexes = []

        for entry in selected_indexes.strip().split():
            if "-" in entry:
                indexes.extend(map(int, expand_range(entry)))
            else:
                indexes.append(int(entry))
    except ValueError:
        print("Invalid index!")
        sys.exit(1)

    return (indexes, output)


def expand_range(entry):
    """Expand the given range

    :type entry: string
    :param entry: index range in number1-number2 format
    :rtype: list
    :returns: list of values from number1 to number2 included
    """

    start = int(entry.split("-")[0])
    end = int(entry.split("-")[-1]) + 1

    return range(start, end)


def status(is_quiet):
    """Run svn status command

    :type is_quiet: bool
    :param is_quiet: if true svn status command runs with -q parameter
    :rtype: string
    :returns: svn status command output
    """

    status_command = "svn status"

    if is_quiet:
        status_command += " -q"

    status_result = subprocess.Popen(status_command, shell=True, stdout=subprocess.PIPE)

    return status_result.communicate()[0].decode("utf-8")


def diff():
    """Get diff of selected files"""

    selected_indexes, output = get_requested_indexes(True)

    # run svn diff on selected files
    for index, file_path in output:
        if index in selected_indexes:

            diff_command = "svn diff %s" % file_path.split()[-1]
            diff_result = subprocess.Popen(diff_command, shell=True, stdout=subprocess.PIPE)

            show_command_output(diff_result.communicate()[0])


def revision_diff(first_revision, second_revision):
    """Get diff of files between specific revisions

    :type first_revision: string
    :param first_revision: first revision number for diff
    :type second_revision: string
    :param second_revision: second revision number for diff
    """

    print("\nSelect files to see revision diff")
    selected_indexes, output = get_requested_indexes(True)

    for index, file_path in output:
        if index in selected_indexes:

            revision_diff_command = "svn diff -r %s:%s %s" % (first_revision, second_revision,
                                                              file_path.split()[-1])
            diff_result = subprocess.Popen(revision_diff_command, shell=True, stdout=subprocess.PIPE)

            show_command_output(diff_result.communicate()[0])


def commit():
    """Commit selected files/folders"""

    selected_indexes, output = get_requested_indexes(True)

    commit_list = []

    # determine files to commit
    for index, file_path in output:
        if index in selected_indexes:
            commit_list.append(file_path.split()[-1])

    # commit selected files
    commit_command = "svn commit %s" % (" ".join(file_to_commit for file_to_commit in commit_list))
    subprocess.call(commit_command, shell=True)


def log():
    """Get log of selected files"""

    selected_indexes, output = get_requested_indexes(True)

    for index, file_path in output:
        if index in selected_indexes:
            file_for_log = file_path.split()[-1]

            log_command = "svn log %s" % file_for_log
            os.system(log_command)


def directory_log():
    """Get log of selected directories"""

    directory_list = []

    # get list of directories in current directory
    for name in os.listdir(os.getcwd()):
        if not (name.startswith(".") or name.startswith("svn") or os.path.isfile(name)):
            directory_list.append(name)

    # show indexed directory list
    indexed_output = list(zip(range(1, len(directory_list)+1), directory_list))
    show_indexed_result(indexed_output)

    # get selected indexes from user
    indexes = input("\nEnter requested indexes: ")

    try:
        selected_indexes = [int(item) for item in indexes.strip().split()]
    except ValueError:
        print("Invalid index!")
        sys.exit(1)

    # run log command for selected directory/directories
    for index, folder_path in indexed_output:
        if index in selected_indexes:
            log_command = "svn log %s" % folder_path
            os.system(log_command)


def add():
    """Add selected files to svn"""

    selected_indexes, output = get_requested_indexes(False)

    add_list = []

    # determine files to add
    for index, file_path in output:
        if index in selected_indexes:
            add_list.append(file_path.strip("? "))

    # add selected files to svn
    add_command = "svn add %s" % (" ".join(file_to_add for file_to_add in add_list))
    subprocess.call(add_command, shell=True)


def blame():
    """Run svn blame for selected files"""

    selected_indexes, output = get_requested_indexes(True)

    blame_list = []

    # determine files to add
    for index, file_path in output:
        if index in selected_indexes:
            blame_list.append(file_path.split()[-1])

    # add selected files to svn
    blame_command = "svn blame %s" % (" ".join(file_to_blame for file_to_blame in blame_list))
    subprocess.call(blame_command, shell=True)


def index_command_output(output):
    """Return indexed output

    :type output: string
    :param output: output to index
    :rtype: list
    :returns: indexed output
    """

    indexed_output = list(zip(range(1, len(output)+1), output.split("\n")))

    return indexed_output[:-1]


def backup_files(dirname):
    """Backup changed files to given directory. New directory will be
    created in the home directory. Files will be prefixed with the
    name of the immediate parent folder.

    :type dirname: string
    :param dirname: name of backup directory
    """

    selected_indexes, output = get_requested_indexes(True)
    backup_dir = os.path.join(os.path.expanduser("~"), dirname)

    if not os.path.exists(backup_dir):
        print("Creating {}...".format(backup_dir))
        subprocess.call("mkdir %s" % backup_dir, shell=True)
    else:
        print("Backup directory already exists! Continue to backup...")

    copy_ok = False

    for index, file_path in output:
        if index in selected_indexes:
            filename = os.path.join(os.getcwd(), file_path.split()[-1])

            immediate_parent_dirname = os.path.dirname(filename).split(os.path.sep)[-1]
            new_filename = immediate_parent_dirname + "__" + os.path.basename(filename)

            print("Copying {}...".format(filename))
            subprocess.call("cp %s %s" % (filename, os.path.join(backup_dir, new_filename)), shell=True)

            copy_ok = True

    if copy_ok:
        print("All files copied to {}".format(backup_dir))
    else:
        print("Failed to copy files!")
        if os.path.exists(backup_dir):
            subprocess.call("rm -rf %s" % backup_dir, shell=True)


def create_patch():
    """Create a patch file from current status of working copy.
    File will be created under the home directory with the following format

    <working copy directory name>_<date>.patch
    """
    
    date = datetime.datetime.now().strftime("%b-%d-%Y-%H-%M-%S")
    filename = os.path.basename(os.getcwd()) + "_" + date + ".patch"
    patch_file = os.path.join(os.path.expanduser("~"), filename)

    os.system("svn diff > %s" % patch_file)

    print("Created {}".format(patch_file))


def apply_patch(filename):
    """Apply the given patch file.
    
    :type filename: string
    :param filename: name of patch file
    """

    patch_filepath = os.path.join(os.path.expanduser("~"), filename)
    if not os.path.exists(patch_filepath):
        print("Patch file not found!")
        sys.exit(1)

    os.system("svn patch %s" % patch_filepath)


def show_indexed_result(output):
    """Show indexed output

    :type output: tuple
    :param output: tuple that contains indexed svn status output
    """

    for index, filepath in output:
        print("%2s -- %s" % (index, filepath))


def show_command_output(result):
    """Show result of command run
    
    :type result: string
    :param result: result of svn command run on selected files/folders
    """

    print(result.decode("utf-8"))


if __name__ == '__main__':

    # run in working directory
    os.chdir(os.getcwd())

    args = sys.argv

    if "-s" in args:
        print(status(False))
    elif "-d" in args:
        diff()
    elif "-dr" in args:
        first_revision = input("Enter first revision:  ")
        second_revision = input("Enter second revision: ")
        revision_diff(first_revision, second_revision)
    elif "-c" in args:
        commit()
    elif "-l" in args:
        log()
    elif "-dl" in args:
        directory_log()
    elif "-a" in args:
        add()
    elif "-b" in args:
        blame()
    elif "-bc" in args:
        backup_dir_name = input("Enter name of backup directory: ")
        print("Getting changed files...")
        backup_files(backup_dir_name)
    elif "-cp" in args:
        create_patch()
    elif "-ap" in args:
        patch_file = input("Enter name of patch file: ")
        apply_patch(patch_file)
    else:
        print("Invalid argument!")
        
