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
    if not os.path.exists(file_b):
        ret_val = True
        logging.info("{} doesn't exist ".format(file_b))
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
        logging.info("{} doesn't exist ".format(file_b))
    else:
        a_age = os.path.getmtime(file_a)
        b_age = os.path.getmtime(file_b)
        if a_age > b_age:
            ret_val = True
    return ret_val

def dir_has_newer_files(file, dir):
    ret_val = False
    if not os.path.exists(file):
        logging.info("{} doesn't exist ".format(file))
        ret_val = True
    else:
        file_paths = next(os.walk(dir))[2]
        for f in file_paths:
            dir_file = os.path.join(dir, f)
            if is_a_newer_than_b(dir_file, file):
                ret_val = True
                break
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

def envvar(name, def_val=None, suffix=None):
    """ envvar interface
    """
    ret_val = os.environ.get(name, def_val)
    if suffix is not None:
        ret_val = ret_val + suffix
    return ret_val

def unzip_file(zip_path, file_name, target_file_path=None, log_exceptions=False):
    """ unzips a file from a zip file...
        @returns True if there's a problem...
    """
    ret_val = False

    try:
        if target_file_path is None:
            target_file_path = os.path.dirname(zip_path)
            target_file_path = os.path.join(target_file_path, file_name)
        rm(target_file_path)
        zip = zipfile.ZipFile(zip_path, 'r')
        file = open(target_file_path, 'wb')
        file.write(zip.read(file_name))
        file.flush()
        file.close()
        zip.close()
    except Exception, e:
        if log_exceptions:
            logging.warn("problems extracting {} from {} into file {} ({})".format(file_name, zip_path, target_file_path, e.message))
        ret_val = True

    return ret_val

def remove_file_from_zip(zip_path, file_name):
    ''' remove a file(s) from a zip
    '''
    # step 1: remove tmp zip file file
    tmpzip = zip_path + '.tmp'
    rm(tmpzip)

    # step 2: copy files from source zip file to tmp zip file
    zin = zipfile.ZipFile (zip_path, 'r')
    zout = zipfile.ZipFile (tmpzip, 'w')
    for item in zin.infolist():
        buffer = zin.read(item.filename)
        if file_name not in item.filename[-4:]:
            zout.writestr(item, buffer)
    zout.close()
    zin.close()

    # step 3: move tmp file to zip file
    rm(zip_path)
    mv(tmpzip, zip_path)

def add_file_to_zip(filename, zippath):
    ''' remove a file(s) from a zip
    '''
    zip = zipfile.ZipFile(zippath, mode='a', compression=zipfile.ZIP_DEFLATED)
    zip.write(filename)
    zip.close()