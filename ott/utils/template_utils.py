from . import file_utils
import logging
log = logging.getLogger(__file__)


def apply_template(tmpl, kv):
    from string import Template
    s = Template(tmpl)
    u = s.safe_substitute(kv)
    return u


def apply_template_to_files(kv, dir_path='.', ext=".txt", rewrite=False):
    """
    will look for files that appear to be templates, and apply the key-values (kv) to the template
    """
    ret_val = []
    for f in file_utils.find_files(dir_path, ext):
        c = file_utils.read_file_into_string(f)
        if c and len(c) > 0 and '$' in c:
            s = apply_template(c, kv)
            if s != c:
                z = {'template': c, 'applied': s, 'file': f}
                ret_val.append(z)
                if rewrite:
                    with open(z['file'], "w") as file:
                        file.write(z['applied'])

    return ret_val


def apply_kv_to_files(key='PASSWORD', value='PASSWORD', dir_path='.', ext=".txt", rewrite=False):
    # import pdb; pdb.set_trace()
    kv = {key: value}
    ret_val = apply_template_to_files(kv, dir_path, ext, rewrite)
    return ret_val
