import os
import re
import datetime
import zipfile
import filecmp
import shutil

from . import string_utils

import logging
log = logging.getLogger(__file__)


NEW_SUFFIX = "-new"
OLD_DIR_NAME = "OLD"


def get_mtime(file):
    """ datetime for the modified file time """
    try:
        mtime = os.path.getmtime(file)
    except:
        try:
            # attempt to get time from a symlink (ln -s file)
            mtime = os.path.getmtime(os.readlink(file))
        except:
            # one last sym link try...
            mtime = os.lstat(file).st_mtime
    return mtime


def file_time(file):
    mtime = get_mtime(file)
    dt = datetime.datetime.fromtimestamp(mtime)
    return dt


def file_age(file):
    """ age in days """
    mtime = file_time(file)
    now = datetime.datetime.now()
    diff = now - mtime
    return diff.days


def file_age_seconds(file):
    """ age in days """
    mtime = file_time(file)
    now = datetime.datetime.now()
    diff = now - mtime
    ret_val = diff.seconds + diff.days * 86400
    return ret_val


def file_size(file):
    """ return size of file path
        note: symlinks are kinda broken here python
              os.path.realpath(path) doesn't work on mac to get real file path
    """
    try:
        s = os.stat(file)
    except:
        s = os.stat(os.readlink(file))
    return s.st_size


def touch(file):
    try:
        os.utime(file, None)
    except:
        # doesn't exist ... unlike touch, don't create the file tho...
        pass


def exists_and_sized(file, size, expire):
    ret_val = True
    if os.path.exists(file) is False:
        log.info("{} doesn't exist ".format(file))
        ret_val = False
    elif file_age(file) > expire:
        log.info("{} is {} days old, thus older than the {} day refresh threshold".format(file, file_age(file), expire))
        ret_val = False
    elif file_size(file) < size:
        log.info("{} is smaller than {} bytes in size".format(file, size))
        ret_val = False
    return ret_val


def is_min_sized(file, min_size=1000000, quiet=False):
    ret_val = False
    try:
        size = file_size(file)
        if size >= min_size:
            ret_val = True
    except Exception, e:
        if not quiet:
            log.warn("{}".format(e))
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


def is_a_newer_than_b(file_a, file_b):
    ret_val = False
    if not os.path.exists(file_b):
        ret_val = True
        log.info("{} doesn't exist ".format(file_b))
    else:
        a_age = get_mtime(file_a)
        b_age = get_mtime(file_b)
        if a_age > b_age:
            ret_val = True
    return ret_val


def dir_has_newer_files(file, dir, include_filter=None, exclude_filter=None):
    """ determine if any files in the directory have a newer update date than target file
    """
    #import pdb; pdb.set_trace()
    ret_val = False
    if not os.path.exists(file):
        log.info("{} doesn't exist ".format(file))
        ret_val = True
    else:
        file_paths = next(os.walk(dir))[2]
        for f in file_paths:
            if include_filter and not string_utils.is_in_string(f, include_filter):
                continue
            if exclude_filter and string_utils.is_in_string(f, exclude_filter):
                continue
            dir_file = os.path.join(dir, f)
            if is_a_newer_than_b(dir_file, file):
                ret_val = True
                break
    return ret_val


def bkup(file, rm_orig=True):
    ret_val = False
    try:
        if os.path.exists(file):
            mtime = file_time(file)
            tmp_file = "{}.{:%Y%m%d}".format(file, mtime)
            rm(tmp_file)
            if rm_orig:
                os.rename(file, tmp_file)
            else:
                cp(file, tmp_file)
            ret_val = True
    except:
        log.error('could not backup file {}'.format(file))
    return ret_val


def cd(dir):
    if dir:
        os.chdir(dir)


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
    if src and dst and os.path.isfile(src):
        shutil.copy2(src, dst)
        touch(dst)
    else:
        log.error('could not copy file {} to {}'.format(src, dst))


def rm(file):
    if file and os.path.exists(file):
        os.remove(file)


def purge(dir, pattern):
    """ remove multiple files
        borrowed from http://stackoverflow.com/questions/1548704/delete-multiple-files-matching-a-pattern
    """
    try:
        for f in os.listdir(dir):
            if re.search(pattern, f):
                os.remove(os.path.join(dir, f))
    except Exception, e:
        log.info(e)


def ls(dir, include_filter=None):
    """ return a list of files in a directory, with an optional name filter
    """
    ret_val = []
    file_paths = next(os.walk(dir))[2]
    for f in file_paths:
        if include_filter and not string_utils.is_in_string(f, include_filter):
            continue
        ret_val.append(f)
    return ret_val


def mkdir(dir):
    if dir and not os.path.exists(dir):
        os.makedirs(dir)


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


def make_new_path(dir, file_name, new_suffix=NEW_SUFFIX):
    new_path = os.path.join(dir, file_name + new_suffix)
    return new_path


def make_old_dir(dir, old_name=OLD_DIR_NAME):
    old_path = os.path.join(dir, old_name)
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
        #import pdb; pdb.set_trace()
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

        #import pdb; pdb.set_trace()
    except Exception, e:
        log.warn("problems comparing {} and {}".format(old_name, new_name))
        ret_val = True
    return ret_val


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
    except Exception, e:
        log.warn("problems extracting {} from {} into file {} ({})".format(file_name, zip_path, target_file_path, e))
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


def add_file_to_zip(zip_path, file_path, basename=None):
    """ add a file to a zip file
    """
    if basename is None:
        basename = os.path.basename(file_path)
    zip = zipfile.ZipFile(zip_path, mode='a', compression=zipfile.ZIP_DEFLATED)
    zip.write(file_path, basename)
    zip.close()


def replace_strings_in_zipfile(zip_path, file_name, regex_str, replace_str, zip_basename=None):
    """ collective of file utils functions to open a file from a .zip file, replace contents in that zip, and bundle
        the .zip file back up with the edited contents
    """
    file_path = unzip_file(zip_path, file_name)
    replace_strings_in_file(file_path, regex_str, replace_str)
    remove_file_from_zip(zip_path, file_name)
    add_file_to_zip(zip_path, file_path, zip_basename)


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
    except Exception, e:
        log.warn("problems editing file {}\n(exception: {})".format(file_path, e))


