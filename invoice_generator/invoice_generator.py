"""Main module."""
import os
from pathlib import Path
import re
import subprocess
import uuid
import jinja2

from .models import Invoice


JINJA_CONF = {
    "block_start_string": r'\BLOCK{',
    "block_end_string": '}',
    "variable_start_string": r'\VAR{',
    "variable_end_string": '}',
    "comment_start_string": r'\#{',
    "comment_end_string": '}',
    "line_statement_prefix": '%%',
    "line_comment_prefix": '%#',
    "trim_blocks": True,
    "autoescape": False,
}


class InvoiceGenerator:
    """Invoice Generator.

    Generate an invoice in pdf using LaTeX.

    :param template_dir: Filepath to the directory that contains LaTeX
        templates.
    :type template_dir: pathlib.Path or str
    :param template_name: The name of that LaTeX template to use.
    :type template_name: str
    :param data: The data to use for populating the template.
    :type data: Invoice
    :param output_directory: Path of output directory
    :type output_directory: pathlib.Path or str
    :param invoice_name: The name of the outputed pdf, defaults to None. If
        no invoice_name are passed to generator, it will generate one using
        uuid4.
    :type invoice_name: str, optional
    """

    def __init__(self,
                 data,
                 template_dir=None,
                 template_name=None,
                 output_directory=None,
                 invoice_name=None):
        self.template_dir = template_dir
        self.template_name = template_name
        self.invoice_name = invoice_name
        self.output_directory = output_directory
        self.data = data

    @property
    def template_dir(self):
        return self._template_dir

    @template_dir.setter
    def template_dir(self, template_dir):
        if not template_dir:
            template_dir = Path(__file__).resolve().parents[0] / 'templates'
        if not os.path.exists(template_dir):
            msg = f"The directory {template_dir} doens't exists."
            raise FileNotFoundError(msg)
        if type(template_dir) == str:
            template_dir = Path(template_dir).resolve()
        self._template_dir = template_dir

    @property
    def output_directory(self):
        return self._output_directory

    @output_directory.setter
    def output_directory(self, output_directory):
        if not output_directory:
            output_directory = self.template_dir
        if type(output_directory) == str:
            output_directory = Path(output_directory).resolve()
        self._output_directory = output_directory

    @property
    def template_name(self):
        return self._template_name

    @template_name.setter
    def template_name(self, template_name):
        if not template_name:
            template_name = "main.tex"
        self._template_name = template_name

    @property
    def invoice_name(self):
        return self._invoice_name

    @invoice_name.setter
    def invoice_name(self, invoice_name):
        invoice_name = invoice_name or str(uuid.uuid4())
        if invoice_name.endswith('.pdf'):
            self._invoice_name.replace('.pdf', '')
        else:
            self._invoice_name = invoice_name

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        data = self._escape_latex_characters(data.dict())
        self._data = Invoice(**data)

    @property
    def _file_to_compile(self):
        return self.output_directory / (self.invoice_name)

    @property
    def _latex_jinja_env(self):
        loader = jinja2.FileSystemLoader(self.template_dir)
        return jinja2.Environment(loader=loader, **JINJA_CONF)

    @staticmethod
    def _tex_escape(text):
        """
        :param text: a plain text message
        :return: the message escaped to appear correctly in LaTeX

        from https://stackoverflow.com/questions/16259923/how-can-i-escape-latex-special-characters-inside-django-templates  # noqa
        """
        conv = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\^{}',
            '\\': r'\textbackslash{}',
            '<': r'\textless{}',
            '>': r'\textgreater{}',
        }
        regex = re.compile('|'.join(re.escape(str(key)) for key in
                           sorted(conv.keys(), key=lambda item: - len(item))))
        return regex.sub(lambda match: conv[match.group()], text)

    @staticmethod
    def _escape_latex_characters(data):
        """
        Recursively escape all values in a dictionary
        :param data:
        :return: escaped dictionary
        :rtype: dict

        Adapted from https://gist.github.com/zenweasel/8bf8b4dfed2c5d2c8805
        """
        if isinstance(data, list):
            for x, l in enumerate(data):
                if isinstance(l, dict) or isinstance(l, list):
                    InvoiceGenerator._escape_latex_characters(l)
                else:
                    if type(l) == str:
                        data[x] = InvoiceGenerator._tex_escape(l)

        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, dict) or isinstance(v, list):
                    InvoiceGenerator._escape_latex_characters(v)
                else:
                    if type(v) == str:
                        data[k] = InvoiceGenerator._tex_escape(v)
            return data

    def _load_template(self):
        self._template = self._latex_jinja_env\
                                .get_template(self.template_name)

    def _generate_tex(self):
        to_compile = self._template.render(invoice=self._data)
        with open(str(self._file_to_compile) + '.tex', 'w') as file:
            file.write(to_compile)

    def _check_compilation_success(self):
        if not re.search('Output written on', self.__stdout.decode()):
            raise ValueError('Compilation failed')

    def _clean(self):
        for dirname, _, filenames in os.walk(self.output_directory):
            for f_name in filenames:
                if f_name.startswith(self._invoice_name):
                    if not f_name.endswith('.pdf'):
                        os.remove(os.path.join(dirname, f_name))

    def _compile_latex(self):
        cmd = ['pdflatex',
               "-synctex=1",
               "-interaction=nonstopmode",
               '-output-directory',
               self.output_directory,
               self._file_to_compile
               ]
        process = subprocess.Popen(cmd,
                                   cwd=self._template_dir,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        self.__stdout, self.__stderr = process.communicate()
        self._check_compilation_success()

        return self

    def run(self, clean=True):
        self._load_template()
        self._generate_tex()
        self._compile_latex()._compile_latex()
        if clean:
            self._clean()
        return self.output_directory / (self.invoice_name + '.pdf')
