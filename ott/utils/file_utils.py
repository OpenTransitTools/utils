import os
import logging
import datetime
import zipfile
import filecmp
import shutil

def file_time(file):
    ''' datetime for the modified file time '''
    mtime = os.path.getmtime(file)
    dt = datetime.datetime.fromtimestamp(mtime)
    return dt

def file_age(file):
    ''' age in days '''
    mtime = file_time(file)
    now = datetime.datetime.now()
    diff = now - mtime
    return diff.days

def file_size(file):
    s = os.stat(file)
    return s.st_size

def exists_and_sized(file, size, expire):
    #import pdb; pdb.set_trace()
    ret_val = True
    if os.path.exists(file) is False:
        logging.info("{} doesn't exist ".format(file))
        ret_val = False
    elif file_age(file) > expire:
        logging.info("{} is {} days old, thus older than the {} day refresh threshold".format(file, file_age(file), expire))
        ret_val = False
    elif file_size(file) < size:
        logging.info("{} is smaller than {} bytes in size".format(file, size))
        ret_val = False
    return ret_val

def is_min_sized(file, min_size=1000000):
    ret_val = False
    size = file_size(file)
    if size >= min_size:
        ret_val = True
    return ret_val

def is_a_larger_than_b(file_a, file_b):
    ret_val = False
    a_size = file_size(file_a)
    b_size = file_size(file_b)
    if a_size > b_size:
        ret_val = True
    return ret_val

def is_a_newer_than_b(file_a, file_b):
    ret_val = False
    a_age = os.path.getmtime(file_a)
    b_age = os.path.getmtime(file_b)
    if a_age > b_age:
        ret_val = True
    return ret_val

def bkup(file, rm_orig=True):
    #import pdb; pdb.set_trace()
    if os.path.exists(file):
        mtime = file_time(file)
        tmp_file = "{}.{:%Y%m%d}".format(file, mtime)
        rm(tmp_file)
        if rm_orig:
            os.rename(file, tmp_file)
        else:
            cp(file, tmp_file)

def mv(src, dst):
    os.rename(src, dst)

def cp(src, dst):
    if os.path.isfile(src):
        shutil.copy2(src, dst)
    else:
        logging.error('could not copy file {} to {}'.format(src, dst))

def rm(file):
    if os.path.exists(file):
        os.remove(file)

def cd(dir):
    os.chdir(dir)

def mkdir(dir):
    if not os.path.exists(dir):
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

def diff_files(old_name, new_name):
    """ return True if the files are DIFFERENT ... False == files are THE SAME...
    """
    ret_val = True

    #import pdb; pdb.set_trace()
    try:
        # check #1
        ret_val = not filecmp.cmp(old_name, new_name)
        logging.info("{0} {1} different from {2} (according to os.stat)".format(old_name, "IS" if ret_val else "is NOT", new_name))

        # check #2
        # adapted from http://stackoverflow.com/questions/3043026/comparing-two-text-files-in-python
        of = open(old_name, "r")
        nf = open(new_name, "r")
        olist = of.readlines()
        nlist = nf.readlines()
        k=1
        for i,j in zip(olist, nlist): #note: zip is used to iterate variables in 2 lists in single loop
            if i != j:
                logging.info("At line #{0}, there's a difference between the files:\n\t{1}\t\t--vs--\n\t{2}\n".format(k, i, j))
                ret_val = True
                break
            k=k+1
    except Exception, e:
        logging.warn("problems comparing {} and {}".format(old_name, new_name))
        ret_val = True
    return ret_val

def unzip_file(zip_file, target_file, file_name, log_exceptions=False):
    """ unzips a file from a zip file...
        @returns True if there's a problem...
    """
    ret_val = False

    try:
        rm(target_file)
        zip = zipfile.ZipFile(zip_file, 'r')
        file = open(target_file, 'wb')
        file.write(zip.read(file_name))
        file.flush()
        file.close()
        zip.close()
    except Exception, e:
        if log_exceptions:
            logging.warn("problems extracting {} from {} into file {} ({})".format(file_name, zip_file, target_file, e.message))
        ret_val = True

    return ret_val

def envvar(name, def_val=None, suffix=None):
    """ envvar interface
    """
    ret_val = os.environ.get(name, def_val)
    if suffix is not None:
        ret_val = ret_val + suffix
    return ret_val
