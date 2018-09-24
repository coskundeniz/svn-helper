#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
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
        selected_indexes = raw_input("\nEnter requested indexes: ")
    else:
        print "\nThere is no changes to show\n"
        return ([], output)

    try:
        indexes = [int(item) for item in selected_indexes.strip().split()]
    except ValueError:
        print "Invalid index!"
        sys.exit(0)

    return (indexes, output)


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

    return status_result.communicate()[0]


def diff():
    """Get diff of selected files"""

    selected_indexes, output = get_requested_indexes(True)

    # run svn diff on selected files
    for index, file_path in output:
        if index in selected_indexes:

            diff_command = "svn diff %s" % file_path.strip("MDA!+ ")
            diff_result = subprocess.Popen(diff_command, shell=True, stdout=subprocess.PIPE)

            print diff_result.communicate()[0]


def revision_diff(first_revision, second_revision):
    """Get diff of files between specific revisions

    :type first_revision: string
    :param first_revision: first revision number for diff
    :type second_revision: string
    :param second_revision: second revision number for diff
    """

    print "\nSelect files to see revision diff"
    selected_indexes, output = get_requested_indexes(True)

    for index, file_path in output:
        if index in selected_indexes:

            revision_diff_command = "svn diff -r %s:%s %s" % (first_revision, second_revision,
                                                              file_path.strip("MD!+ "))
            diff_result = subprocess.Popen(revision_diff_command, shell=True, stdout=subprocess.PIPE)

            print diff_result.communicate()[0]


def commit():
    """Commit selected files/folders"""

    selected_indexes, output = get_requested_indexes(True)

    commit_list = []

    # determine files to commit
    for index, file_path in output:
        if index in selected_indexes:
            commit_list.append(file_path.strip("MDA!+ "))

    # commit selected files
    commit_command = "svn commit %s" % (" ".join(file_to_commit for file_to_commit in commit_list))
    subprocess.call(commit_command, shell=True)


def log():
    """Get log of selected files"""

    selected_indexes, output = get_requested_indexes(True)

    for index, file_path in output:
        if index in selected_indexes:
            file_for_log = file_path.strip("MD!+ ")

            log_command = "svn log %s" % file_for_log
            log_result = subprocess.Popen(log_command, shell=True, stdout=subprocess.PIPE)

            print log_result.communicate()[0]


def directory_log():
    """Get log of selected directories"""

    directory_list = []

    # get list of directories in current directory
    for name in os.listdir(os.getcwd()):
        if not (name.startswith(".") or name.startswith("svn") or os.path.isfile(name)):
            directory_list.append(name)

    # show indexed directory list
    indexed_output = zip(range(1, len(directory_list)+1), directory_list)
    show_indexed_result(indexed_output)

    # get selected indexes from user
    indexes = raw_input("\nEnter requested indexes: ")

    try:
        selected_indexes = [int(item) for item in indexes.strip().split()]
    except ValueError:
        print "Invalid index!"
        sys.exit(0)

    # run log command for selected directory/directories
    for index, folder_path in indexed_output:
        if index in selected_indexes:
            log_command = "svn log %s" % folder_path
            log_result = subprocess.Popen(log_command, shell=True, stdout=subprocess.PIPE)

            print log_result.communicate()[0]


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
            blame_list.append(file_path.strip("MD!+ "))

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

    indexed_output = zip(range(1, len(output)+1), output.split("\n"))

    return indexed_output[:-1]


def show_indexed_result(output):
    """Show indexed output

    :type output: tuple
    :param output: tuple that contains indexed svn status output
    """

    for index, filepath in output:
        print "%2s -- %s" % (index, filepath)


if __name__ == '__main__':

    # run in working directory
    os.chdir(os.getcwd())

    args = sys.argv

    if "-s" in args:
        print status(False)
    elif "-d" in args:
        diff()
    elif "-dr" in args:
        first_revision = raw_input("Enter first revision:  ")
        second_revision = raw_input("Enter second revision: ")
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
    else:
        print "Invalid argument!"
        
