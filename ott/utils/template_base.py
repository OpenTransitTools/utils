import os
import inspect
import pystache
import datetime

import logging
log = logging.getLogger(__file__)


class TemplateBase(object):
    _renderer = pystache.Renderer()

    @classmethod
    def _goose_content(cls, content):
        """ append helper content before rendering """

        # utc date string
        dt = "{} UTC".format(datetime.datetime.utcnow())
        content["utcnow"] = dt

        return content

    @classmethod
    def _render_path(cls, template, content):
        return cls._renderer.render_path(template, cls._goose_content(content))

    @classmethod
    def _render_string(cls, template, content):
        return cls._renderer.render(template, cls._goose_content(content))

    @classmethod
    def render_template_file(cls, template, content):
        """treat template as a file (path) and try rendering the content """
        ret_val = None
        try:
            ret_val = cls._render_path(template, content)
        except FileNotFoundError:
            # try adding mustache extension to see if that renders
            try:
                ret_val = cls._render_path(template + ".mustache", content)
            except Exception as e:
                log.info(e)
                ret_val = None
        return ret_val

    @classmethod
    def render_templates_dir(cls, template, content):
        """ treat template as a template in this 'templates' directory """
        dir_path = os.path.dirname(inspect.getfile(cls))
        ret_val = cls.render_template_file(os.path.join(dir_path, template), content)
        return ret_val

    @classmethod
    def render_template_string(cls, template, content):
        ret_val = cls._render_string(template, content)
        return ret_val

    @classmethod
    def render(cls, template, content):
        # import pdb; pdb.set_trace()

        # try 1: treat template as a template in this current directory
        ret_val = cls.render_templates_dir(template, content)

        # try 2: treat template as a path to a template
        if ret_val is None:
            ret_val = cls.render_template_file(template, content)

        # try 3: treat template as a string template (will usually render something...)
        if ret_val is None:
            ret_val = cls.render_template_string(template, content)

        return ret_val
