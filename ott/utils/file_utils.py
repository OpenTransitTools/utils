import os
import sys
import re
import csv
import datetime
import zipfile
import filecmp
import shutil
import inspect

from . import string_utils
from . import date_utils

import logging
log = logging.getLogger(__file__)


NEW_SUFFIX = "-new"
OLD_DIR_NAME = "OLD"


def find_files(dir_path, ext=".txt", contains=False, sub_dirs=[""]):
    """ find files that have a certain ending extension """
    ret_val = []
    for sd in sub_dirs:
        path = os.path.join(dir_path, sd)
        if os.path.exists(path):
            for file in listdir(path):
                if (contains and ext in file) or file.endswith(ext):
                    f = os.path.join(path, file)
                    ret_val.append(f)
    return ret_val


def find_files_in_subdirs(dir_path, ext=".txt", contains=False):
    """ find files that have a certain ending extension """
    ret_val = []
    for file in listdir(dir_path):
        if (contains and ext in file) or file.endswith(ext):
            f = os.path.join(dir_path, file)
            ret_val.append(f)
    return ret_val


def read_file_into_string_list(file_path):
    """read file into a string"""
    ret_val = None
    with open(file_path, "r") as f:
        ret_val = f.readlines()
    return ret_val


def read_file_into_string(file_path, sep=""):
    """read file into a string"""
    l = read_file_into_string_list(file_path)
    ret_val = sep.join(l)
    return ret_val


def prepend_file(file_path, content):
    """ simple file prepender
        @note: assumes there are no issues loading the contents of the file into memory
        @see http://stackoverflow.com/questions/5914627/prepend-line-to-beginning-of-a-file
    """
    if os.path.exists(file_path):
        fperms = 'r+'
    else:
        fperms = 'w+'
    with open(file_path, fperms) as f:
        old_content = f.read()
        f.seek(0, 0)
        f.write(content)
        f.write(old_content)


def get_mtime(file_path):
    """ datetime for the modified file time ... returns time in seconds """
    # import pdb; pdb.set_trace()
    try:
        mtime = os.path.getmtime(file_path)
    except:
        try:
            # attempt to get time from a symlink (ln -s file)
            mtime = os.path.getmtime(os.readlink(file_path))
        except:
            # one last sym link try...
            mtime = os.lstat(file_path).st_mtime
    return mtime


def file_time(file_path):
    mtime = get_mtime(file_path)
    dt = datetime.datetime.fromtimestamp(mtime)
    return dt


def file_pretty_date(file_path, fmt=None):
    dt = file_time(file_path)
    return date_utils.pretty_date(dt, fmt)


def file_age(file_path):
    """ age in days """
    mtime = file_time(file_path)
    now = datetime.datetime.now()
    diff = now - mtime
    return diff.days


def file_age_seconds(file_path):
    """ age in days """
    mtime = file_time(file_path)
    now = datetime.datetime.now()
    diff = now - mtime
    ret_val = diff.seconds + diff.days * 86400
    return ret_val


def file_size(file_path):
    """ return size of file path
        note: symlinks are kinda broken here python
              os.path.realpath(path) doesn't work on mac to get real file path
    """
    try:
        s = os.stat(file_path)
    except:
        s = os.stat(os.readlink(file_path))
    return s.st_size


def chmod(file_path, perms=0o644):
    """ py 2.x == 0755 vs py 3.x 0o755 """
    # import pdb; pdb.set_trace()
    try:
        os.chmod(file_path, perms)  # py 3.x ...
    except:
        try:
            p = oct(perms).lstrip('0o').lstrip('0')
            os.system("chmod {} {}".format(p, file_path))
        except:
            pass


def touch(file_path):
    try:
        os.utime(file_path, None)
    except:
        # doesn't exist ... unlike touch, don't create the file tho...
        pass


def exists(dir, file_name=None):
    ret_val = False

    if dir:
        if file_name:
            file_path = os.path.join(dir, file_name)
        else:
            file_path = dir

        if os.path.exists(file_path):
            ret_val = True
    return ret_val


def exists_and_newer(file_path, age=10000):
    ret_val = False
    if os.path.exists(file_path):
        log.info("{} does exist ".format(file_path))
        ret_val = True
        if file_age(file_path) > age:
            log.info("{} is {} days old, thus older than the {} days specified".format(file_path, file_age(file_path), age))
            ret_val = False
    return ret_val


def exists_and_sized(file_path, size, expire=None):
    ret_val = True
    if os.path.exists(file_path) is False:
        log.info("{} doesn't exist ".format(file_path))
        ret_val = False
    elif file_size(file_path) < size:
        log.info("{} is smaller than {} bytes in size".format(file_path, size))
        ret_val = False
    elif expire and file_age(file_path) > expire:
        log.info("{} is {} days old, thus older than the {} day refresh threshold".format(file_path, file_age(file_path), expire))
        ret_val = False
    return ret_val


def is_min_sized(file_path, min_size=1000000, quiet=False):
    ret_val = False
    try:
        size = file_size(file_path)
        if size >= min_size:
            ret_val = True
    except Exception as e:
        if not quiet:
            log.warning("{}".format(e))
    return ret_val


def is_a_larger_than_b(file_a, file_b):
    ret_val = False
    if not os.path.exists(file_b):
        ret_val = True
        log.info("{} doesn't exist ".format(file_b))
    else:
        a_size = file_size(file_a)
        b_size = file_size(file_b)
        if a_size > b_size:
            ret_val = True
    return ret_val


def is_a_newer_than_b(file_a, file_b, offset_minutes=0):
    ret_val = False
    if os.path.exists(file_a):
        if not os.path.exists(file_b):
            ret_val = True
            log.info("{} doesn't exist ".format(file_b))
        else:
            a_age = get_mtime(file_a)
            b_age = get_mtime(file_b)
            if a_age > b_age + (offset_minutes * 60):
                ret_val = True
    else:
        log.info("{} doesn't exist ".format(file_a))
    return ret_val


def dir_has_newer_files(cmp_file, dir_path, offset_minutes=0, include_filter=None, exclude_filter=None):
    """ determine if any files in the directory have a newer update date than target file
    """
    # import pdb; pdb.set_trace()
    ret_val = False
    if not os.path.exists(cmp_file):
        log.info("{} doesn't exist ".format(cmp_file))
        ret_val = True
    else:
        file_paths = next(os.walk(dir_path))[2]
        for f in file_paths:
            if include_filter and not string_utils.is_in_string(f, include_filter):
                continue
            if exclude_filter and string_utils.is_in_string(f, exclude_filter):
                continue
            dir_file = os.path.join(dir_path, f)
            if is_a_newer_than_b(dir_file, cmp_file, offset_minutes):
                log.info("IMPORTANT: {} *has* newer files: {} is newer than {}!".format(dir_path, dir_file, cmp_file))
                ret_val = True
                break
    return ret_val


def bkup(file_path, rm_orig=True):
    ret_val = False
    try:
        if os.path.exists(file_path):
            mtime = file_time(file_path)
            tmp_file = "{}.{:%Y%m%d}".format(file_path, mtime)
            rm(tmp_file)
            if rm_orig:
                os.rename(file_path, tmp_file)
            else:
                cp(file_path, tmp_file)
            ret_val = True
    except:
        log.error('could not backup file {}'.format(file_path))
    return ret_val


def cd(dir_path):
    if dir_path:
        os.chdir(dir_path)


def envvar(name, def_val=None, suffix=None):
    """ envvar interface
    """
    ret_val = os.environ.get(name, def_val)
    if suffix is not None:
        ret_val = ret_val + suffix
    return ret_val


def mv(src, dst, delete_dst_first=True, update_ftime=True):
    ret_val = False
    try:
        if delete_dst_first:
            rm(dst)
        os.rename(src, dst)
        if update_ftime:
            touch(dst)
        ret_val = True
    except:
        log.error('could not mv file {} to {}'.format(src, dst))
    return ret_val


def cp(src, dst):
    # import pdb; pdb.set_trace()
    if src and dst and os.path.isfile(src):
        shutil.copy2(src, dst)
        touch(dst)
    else:
        log.error('could not copy file {} to {}'.format(src, dst))


def rm(file_path):
    if file_path and os.path.exists(file_path):
        os.remove(file_path)


def purge(dir_path, pattern):
    """ remove multiple files
        borrowed from http://stackoverflow.com/questions/1548704/delete-multiple-files-matching-a-pattern
    """
    try:
        for f in listdir(dir_path):
            if re.search(pattern, f):
                os.remove(os.path.join(dir_path, f))
    except Exception as e:
        log.info(e)


def ls(dir_path, include_filter=None, full_paths=False):
    """ return a list of files in a directory, with an optional name filter
    """
    ret_val = []
    file_paths = next(os.walk(dir_path))[2]
    for f in file_paths:

        # file filter
        if include_filter:
            # extension filter ... triggered by regex '$'
            if include_filter.endswith('$'):
                extension = include_filter.rstrip('$')
                if not f.endswith(extension):
                    continue
            # any string match filter
            elif not string_utils.is_in_string(f, include_filter):
                continue

        # add file to result list
        if full_paths:
            f = os.path.join(dir_path, f)
        ret_val.append(f)

    return ret_val


def grep(file_path, search_regexp, case=True):
    ret_val = []
    if case:
        p = re.compile(search_regexp)
    else:
        p = re.compile(search_regexp, re.IGNORECASE)
    with open(file_path) as f:
        for num, line in enumerate(f):
            if p.search(line):
                ret_val.append(line)
                log.debug("{} found on line {}: {}".format(search_regexp, num, line))
    return ret_val


def mkdir(dir_path):
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)


def cat(dir, file_name=None, input=None):
    """ act like unix 'cat' - put string into file (or echo data out """
    ret_val = None

    # step 1: figure out the file path
    if dir:
        if file_name:
            file_path = os.path.join(dir, file_name)
        else:
            file_path = dir

        # step 2: write to the file if we have something to input
        if input:
            with open(file_path, "w+") as f:
                f.write(input)

        # step 3: read contents of the file
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                ret_val = f.readlines()
    return ret_val


def copy_contents(src_dir, target_dir, overwrite=True):
    file_paths = next(os.walk(src_dir))[2]
    for f in file_paths:
        src = os.path.join(src_dir, f)
        tgt = os.path.join(target_dir, f)
        if overwrite or not os.path.exists(tgt):
            cp(src, tgt)


def get_file_name_from_url(url):
    ret_val = url.split('/')[-1:][0]
    return ret_val


def get_file_name_from_path(file_path):
    return os.path.basename(file_path)


def append_to_path(path, append, end_with_sep=True):
    """  with return .../path/append/ from separate .../path + append variables
         (will try to do the best thing to figure out the proper separator character, and where to place it)
    """
    # step 1: figure out separator
    sep = None
    if "/" in path:
        sep = "/"
    elif "\\" in path:
        sep = "\\"

    # step 2: if current path doesn't end with a sep, append one
    if sep and not path.endswith(sep):
        path = path + sep

    # step 3: append path with thing we're appending
    ret_val = path + append

    # step 4: optional ending separator (default)
    if sep and end_with_sep:
        ret_val = ret_val + sep

    return ret_val


def path_join(dir, file):
    """ append file (or file path) to a direcory path
    """
    # step 1: handle relative paths
    if file.startswith('/'):
        file = file[1:]
    if file.startswith('./'):
        file = file[2:]
    if file.startswith('../'):
        file = file[3:]
        # TODO: os.pardir is ".." -- and we cange to full path w.out .. crap?
        # also would like .join to accpet fwd slash junk and refactor on Win/DOS to backslahses, etc...
        dir = os.path.join(dir, os.pardir)

    # step 2: join dir to a file path
    # TODO if 'file' is actually a path with fwd slashes (ala ../x/y/z.file, split that path and then join in an os acceptable way
    file_path = os.path.join(dir, file)
    return file_path


def make_new_path(dir_path, file_name=None, new_suffix=NEW_SUFFIX):
    if file_name:
        new_path = os.path.join(dir_path, file_name + new_suffix)
    else:
        new_path = dir_path + new_suffix
    return new_path


def make_old_dir(dir_path, old_name=OLD_DIR_NAME):
    old_path = os.path.join(dir_path, old_name)
    mkdir(old_path)
    return old_path


def diff_files(old_name, new_name):
    """ return True if the files are DIFFERENT ... False == files are THE SAME...
    """
    ret_val = True

    try:
        # check #1
        ret_val = not filecmp.cmp(old_name, new_name)
        log.info("{0} {1} different from {2} (according to os.stat)".format(old_name, "IS" if ret_val else "is NOT", new_name))

        # check #2 : compare two files line by line
        # adapted from http://stackoverflow.com/questions/3043026/comparing-two-text-files-in-python
        of = open(old_name, "r")
        olist = of.readlines()
        of.close()

        nf = open(new_name, "r")
        nlist = nf.readlines()
        nf.close()

        if olist and nlist and len(olist) > 0 and len(nlist) > 0:
            if len(olist) == len(nlist):
                k=1
                for i,j in zip(olist, nlist): #note: zip is used to iterate variables in 2 lists in single loop
                    if i != j:
                        log.info("At line #{}, there's a difference between the files:\n\t{}\t\t--vs--\n\t{}\n".format(k, i, j))
                        ret_val = True
                        break
                    k=k+1
            else:
                log.info("Files {} ({} lines) and {} ({} lines) have different number of lines".format(old_name, len(olist), new_name, len(nlist)))
                ret_val = True
        else:
            log.debug("Files {} and {} are both empty".format(old_name, new_name))
    except Exception as e:
        log.warning("problems comparing {} and {}".format(old_name, new_name))
        ret_val = True
    return ret_val


def sys_unzip_file(file):
    if file.endswith("tar.gz"):
        os.system("tar zxvf " + file)
    elif file.endswith("tar"):
        os.system("tar xvf " + file)
    elif file.lower().endswith("zip"):
        os.system("unzip " + file)


def unzip_file(zip_path, file_name, target_file_path=None):
    """ unzips a file from a zip file...
        @returns target_file_path
    """
    ret_val = target_file_path

    try:
        if target_file_path is None:
            target_file_path = os.path.dirname(zip_path)
            target_file_path = os.path.join(target_file_path, file_name)
            ret_val = target_file_path

        log.debug("unzipping file {} from {} (writing file {})".format(file_name, zip_path, target_file_path))
        rm(target_file_path)
        zip = zipfile.ZipFile(zip_path, 'r')
        file = open(target_file_path, 'wb')
        file.write(zip.read(file_name))
        file.flush()
        file.close()
        zip.close()
    except Exception as e:
        log.warning("problems extracting {} from {} into file {} ({})".format(file_name, zip_path, target_file_path, e))
    return ret_val


def remove_file_from_zip(zip_path, file_name):
    """ remove a file(s) from a zip
    """
    # step 1: remove tmp zip file file
    tmpzip = zip_path + '.tmp'
    rm(tmpzip)

    # step 2: copy files from source zip file to tmp zip file
    zin = zipfile.ZipFile (zip_path, 'r')
    zout = zipfile.ZipFile (tmpzip, 'w')
    for item in zin.infolist():
        if file_name not in item.filename:
            buffer = zin.read(item.filename)
            zout.writestr(item, buffer)
    zout.close()
    zin.close()

    # step 3: move tmp file to zip file
    rm(zip_path)
    mv(tmpzip, zip_path)


def add_file_to_zip(zip_path, file_path, file_name=None):
    """ add a file to a zip file
    """
    if file_name is None:
        file_name = os.path.basename(file_path)
    zip = zipfile.ZipFile(zip_path, mode='a', compression=zipfile.ZIP_DEFLATED)
    zip.write(file_path, file_name)
    zip.close()


def replace_file_in_zipfile(zip_path, file_path, file_name=None):
    if file_name is None:
        file_name = os.path.basename(file_path)
    remove_file_from_zip(zip_path, file_name)
    add_file_to_zip(zip_path, file_path, file_name)

def replace_strings_in_zipfile(zip_path, file_name, regex_str, replace_str, zip_basename=None):
    """ collective of file utils functions to open a file from a .zip file, replace contents in that zip, and bundle
        the .zip file back up with the edited contents
    """
    file_path = unzip_file(zip_path, file_name)
    replace_strings_in_file(file_path, regex_str, replace_str)
    replace_file_in_zipfile(zip_path, file_path, zip_basename)

def replace_strings_in_file(file_path, regex_str, replace_str):
    """ replace a pattern in each line of a text file
    """
    try:
        if os.path.exists(file_path):
            # step 1: setup tmp file
            tmp_file_path = file_path + ".tmp"
            rm(tmp_file_path)

            # step 2: open files
            fin = open(file_path,'r')
            tmp = open(tmp_file_path,'w')

            # step 3: replace strings and write them to tmp
            regex = re.compile(regex_str, re.IGNORECASE)
            for line in fin.readlines():
                line = regex.sub(replace_str, line)
                tmp.write(line)

            # step 4: close files
            fin.close()
            tmp.flush()
            tmp.close()

            # step 5: mv tmp file into place for file
            rm(file_path)
            mv(tmp_file_path, file_path)
    except Exception as e:
        log.warning("problems editing file {}\n(exception: {})".format(file_path, e))


def replace_adjacent_strings_in_file(file_path, regex_str1, replace_str1, regex_str2, replace_str2, ovrwt=True):
    """
    replace a pattern in each line of a text file
    """
    try:
        if os.path.exists(file_path):
            # step 1: setup tmp file
            tmp_file_path = file_path + ".tmp"
            rm(tmp_file_path)

            # step 2: open files
            fin = open(file_path,'r')
            tmp = open(tmp_file_path,'w')

            # step 3: set up the 2 regexs and initial replace code
            regex1 = re.compile(regex_str1, re.IGNORECASE)
            regex2 = re.compile(regex_str2, re.IGNORECASE)
            replace_str = replace_str1
            regex = regex1

            # step 4: start going thru the lines of the files
            changing = False
            for line in fin.readlines():
                newln = line
                if replace_str != None and (replace_str == "" or replace_str not in line):
                    newln = regex.sub(replace_str, line)
                tmp.write(newln)

                # step 4b: if we did a regex to this line, then that's a trigger to look for 2nd line
                if line != newln:
                    sys.stdout.write('.')
                    sys.stdout.flush()

                    # import pdb; pdb.set_trace()
                    if changing:
                        # stops regex'ing since we've seen the other line to change
                        replace_str = None
                    else:
                        # switch the rexex stuff so we're looking for 2nd line
                        changing = True
                        regex = regex2
                        replace_str = replace_str2

            # step 4: close files
            fin.close()
            tmp.flush()
            tmp.close()
            print("")

            # step 5: mv tmp file into place for file
            if ovrwt:
                rm(file_path)
                mv(tmp_file_path, file_path)
    except Exception as e:
        log.warning("problems editing file {}\n(exception: {})".format(file_path, e))


def uncomment_block_xml(file_path, comment_regex="", ovrwt=True):
    """
    <!--  THIS METHOD
          will uncomment a block xml comment LIKE ME
          (and it won't mess with any 3-character comment junk below)
          note: see the main method below for a simple test using this file
    -->
    """
    regex_str1 = "<!--.*" + comment_regex
    replace_str1 = "<!-- " + comment_regex + " -->"
    regex_str2 = "-->"
    replace_str2 = ""
    replace_adjacent_strings_in_file(file_path, regex_str1, replace_str1, regex_str2, replace_str2, ovrwt)


def make_csv_writer(fp, fieldnames=None):
    """ :return from the input file pointer (and optional header field names list), return a csv writer
    """
    writer = None
    if fieldnames and len(fieldnames) > 0:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
    else:
        writer = csv.DictWriter(fp)
    return writer


def make_csv_reader(file_path, validate_element=None):
    """
    :return array of dicts representing the .csv file
    """
    ret_val = []
    with open(file_path, mode='r') as csv_file:
        for l in csv.DictReader(csv_file):
            if validate_element:
                n = l.get(validate_element)
                if n is None:
                    continue
                if len(n.strip()) == 0 or n.strip()[0] == "#" or "=>" in n:
                    continue
            ret_val.append(l)
    return ret_val


def listdir(dir_path):
    try:
        ret_val = os.listdir(dir_path)
    except OSError:
        ret_val = os.listdir(os.path.join(os.getcwd(), dir_path))
    return ret_val


def get_parent_dir(in_dir):
    """
    TODO: os.pardir is ".." -- and we cange to full path w.out .. crap?
    """
    dir = os.path.join(in_dir, os.pardir)
    return dir


def get_file_dir(file):
    """
    note: client calling this function can use __file__, ala dir = file_utils.get_file_dir(__file__)
    """
    dir = os.path.dirname(os.path.abspath(file))
    return dir


def get_module_dir(clazz):
    """
    send me a __class__, and I'll return the path to the directory where it lives
    """
    file = inspect.getsourcefile(clazz)
    dir = get_file_dir(file)
    return dir


def get_bin_dir():
    """
    :return the path to where python binary is running (e.g., <project>/bin/ for buildout projects)
    """
    python_path = os.path.dirname(sys.modules['__main__'].__file__)
    return python_path


def get_project_root_dir(path=None):
    """ :return the project root dir (assumes your python is in <project>/bin/python.exe)
    """
    # step 1: get current dir
    if path is None:
        path = os.path.abspath('.')

    # step 2: get home dir based on some known elements
    found = False
    home_dirs = ['ott', 'parts', 'bin', 'eggs']
    for d in home_dirs:
        dir = os.sep + d + os.sep
        if dir in path:
            x = path.split(dir)
            if len(x) >= 2:
                path = x[0]
                break
        dir = os.sep + d
        if path.endswith(dir):
            path = os.path.join(path, '..')
            break
    return path


def main():
    # will demo the uncomment block on this file
    # import pdb; pdb.set_trace()
    uncomment_block_xml("file_utils.py", comment_regex="THIS METHOD", ovrwt=False)


if __name__ == "__main__":
    main()
