# -*- coding: utf-8
import sys
import threading
import win32api
import time
import os

# TODO:
# + 1. List logical drives in the system
# + 2. Make a list of files to be deleted
# + 3. Write a thread to scan and delete files 
# + 4. Run a scan and delete thread on each logical drive 


def get_drives_tuple() -> tuple:
    """
        :return: a tuple of strings of names of logical disks (volumes)
    """
    drives = win32api.GetLogicalDriveStrings()
    return tuple(drives.split('\000')[:-1])


def get_remove_files_list() -> tuple:
    """
        The list of files is taken from the command line arguments if they are
    were transferred, otherwise from the file remove_list.txt 
    """
    if len(sys.argv) < 2:  # Command line arguments not transferred
        with open("remove_list.txt", "r") as fptr:
            return tuple(fptr.read().split('\n'))
    else:
        return tuple(sys.argv[1::])


class Scan_remove_th(threading.Thread):
    """
        A thread that scans all files along the passed path and deletes every
    file whose name matches one of the lines in the passed list
    """
    def __init__(self,
                 path_scan: str,
                 remove_list: tuple):
        """
            :param path_scan: path for the required search
            :param remove_list: list of strings of filenames to remove
        """
        super().__init__()
        self.path_scan = path_scan
        self.remove_list = remove_list

    def run(self):
        """
            Recursive search in directories, deleting files matching by name
        with the given lines in remove_list
        """
        for root, dirs, files in os.walk(self.path_scan):
            for search_value in self.remove_list:
                if search_value in files:
                    full_path = self.make_full_path(root, search_value)
                    try:
                        os.remove(full_path)
                        print(full_path)
                    except PermissionError:
                        print(f"Insufficient rights to delete {full_path}")

    def make_full_path(self,
                       root: str,
                       filename: str) -> str:
        """
            If the file is located at the root, then adding a
		path separator is unnecessary.             

            :param root: path to file
            :param filename: short name of file
            :return: full path to file
        """
        if self.path_scan == root:
            return f"{root}{filename}"
        else:
            return f"{root}{os.path.sep}{filename}"
        

if __name__ == "__main__":
    remove_list = get_remove_files_list()

    """Creating a list of threads, launching them"""
    threads = []
    for drive_path in get_drives_tuple():
        th = Scan_remove_th(drive_path, remove_list)
        th.start()
        threads.append(th)

    """Waiting for all threads to finish"""
    while True:
        ready = True
        for th in threads:
            ready &= not th.is_alive()
        if ready:
            break
        time.sleep(0.1)
