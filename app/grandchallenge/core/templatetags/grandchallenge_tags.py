import logging
import os
import random
import re
import string
import traceback
from io import StringIO

from django import template
from django.core.exceptions import SuspiciousFileOperation
from django.core.files.storage import DefaultStorage
from django.utils._os import safe_join
from matplotlib.backends.backend_svg import FigureCanvasSVG as FigureCanvas
from matplotlib.figure import Figure

from grandchallenge.challenges.models import Challenge
from grandchallenge.core.templatetags import library_plus
from grandchallenge.subdomains.utils import reverse

register = library_plus.LibraryPlus()
logger = logging.getLogger(__name__)


@register.simple_tag()
def url(view_name, *args, **kwargs):
    return reverse(view_name, args=args, kwargs=kwargs)


def substitute(string, substitutions):
    """
    Take each key in the substitutions dict. See if this key exists
    between double curly braces in string. If so replace with value.

    Examples
    --------
        substitute("my name is {{name}}.",{version:1,name=John})
        > "my name is John"
    """
    for key, value in substitutions:
        string = re.sub(re.escape("{{" + key + "}}"), value, string)
    return string


@register.tag(name="insert_graph")
def insert_graph(parser, token):
    """Render a csv file from the local dropbox to a graph."""
    usagestr = """Tag usage: {% insert_graph <file> type:<type>%}
                  <file>: filepath relative to project dropboxfolder.
                  <type>: how should the file be parsed and rendered?
                  Example: {% insert_graph results/test.txt %}
                  You can use url parameters in <file> by using {{curly braces}}.
                  Example: {% inster_graphfile {{id}}/result.txt %} called with ?id=1234
                  appended to the url will show the contents of "1234/result.txt".
                  """
    split = token.split_contents()
    all_args = split[1:]
    if len(all_args) > 2:
        error_message = "Expected no more than 2 arguments, found " + str(
            len(all_args)
        )
        return TemplateErrorNode(error_message + "usage: \n" + usagestr)

    else:
        args = {"file": all_args[0]}
        if len(all_args) == 2:
            args["type"] = all_args[1].split(":")[1]
        else:
            args["type"] = "anode09"  # default
    return InsertGraphNode(args)


class InsertGraphNode(template.Node):
    def __init__(self, args):
        self.args = args

    def make_error_msg(self, msg):
        logger.error(
            "Error rendering graph from file '"
            + ","
            + self.args["file"]
            + "': "
            + msg
        )
        errormsg = "Error rendering graph from file"
        return make_error_message_html(errormsg)

    def render(self, context):  # noqa: C901
        filename_raw = self.args["file"]
        filename_clean = substitute(
            filename_raw, context["request"].GET.items()
        )
        # If any url parameters are still in filename they were not replaced.
        # This filename is missing information..
        if re.search(r"{{\w+}}", filename_clean):
            missed_parameters = re.findall(r"{{\w+}}", filename_clean)
            found_parameters = context["request"].GET.items()
            if not found_parameters:
                found_parameters = "None"
            error_msg = (
                "I am missing required url parameter(s) %s, url parameter(s) found: %s "
                "" % (missed_parameters, found_parameters)
            )
            return self.make_error_msg(error_msg)

        challenge: Challenge = context["currentpage"].challenge

        try:
            filename = safe_join(
                challenge.get_project_data_folder(), filename_clean
            )
        except SuspiciousFileOperation:
            return self.make_error_msg("file is outside the challenge folder.")

        storage = DefaultStorage()
        try:
            storage.open(filename, "r").read()
        except Exception as e:
            return self.make_error_msg(str(e))

        # TODO check content safety

        try:
            render_function = getrenderer(self.args["type"])
        # (table,headers) = read_function(filename)
        except Exception as e:
            return self.make_error_msg("getrenderer: %s" % e)

        try:
            svg_data = render_function(filename)
        except Exception:
            return self.make_error_msg(
                str(
                    "Error in render funtion '%s()' : %s"
                    % (render_function.__name__, traceback.format_exc(0))
                )
            )

        return svg_data


def getrenderer(renderer_format):
    """
    Holds list of functions which can take in a filepath and return html to
    show a graph.

    By using this function we can easily list all available renderers and
    provide some safety: only functions listed here can be called from the
    template tag render_graph.
    """
    renderers = {
        "anode09": render_anode09_result,
        "anode09_table": render_anode09_table,
    }
    if renderer_format not in renderers:
        raise Exception(
            "reader for format '%s' not found. Available formats: %s"
            % (renderer_format, ",".join(renderers.keys()))
        )

    return renderers[renderer_format]


def canvas_to_svg(canvas):
    """
    Render matplotlib canvas as string containing html/svg instructions.

    These instructions can be pasted into any html page and will be rendered as
    a graph by any modern browser.
    """
    imgdata = StringIO()
    imgdata.seek(0, os.SEEK_END)
    canvas.print_svg(imgdata, format="svg")
    svg_data = imgdata.getvalue()
    imgdata.close()
    return svg_data


def render_anode09_result(filename):
    """
    Read in a file with the anode09 result format, return html to render an
    FROC graph. To be able to read this without changing the evaluation
    executable. anode09 results have the following format:

    <?php
        $x=array(1e-39,1e-39,1e-39,1e-39,1e-39,1e-39,1e-39,1e-39,1e-39,...
        $frocy=array(0,0.00483092,0.00966184,0.0144928,0.014492,...
        $frocscore=array(0.135266,0.149758,0.193237,0.236715,0.246377,...
        $pleuraly=array(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,...
        $pleuralscore=array(0.0508475,0.0508475,0.0677966,0.118644,...
        $fissurey=array(0,0,0,0.0285714,0.0285714,0.0285714,0.0571429,...
        $fissurescore=array(0.171429,0.171429,0.285714,0.314286,0.314286,...
        $vasculary=array(0,0.0116279,0.0116279,0.0116279,0.0116279,...
        $vascularscore=array(0.116279,0.139535,0.186047,0.209302,0.22093,...
        $isolatedy=array(0,0,0.0238095,0.0238095,0.0238095,0.0238095,...
        $isolatedscore=array(0.238095,0.261905,0.309524,0.380952,...
        $largey=array(0,0.0111111,0.0111111,0.0111111,0.0111111,0.0111111,...
        $largescore=array(0.111111,0.122222,0.144444,0.177778,0.177778,...
        $smally=array(0,0,0.00854701,0.017094,0.017094,0.017094,0.025641,...
        $smallscore=array(0.153846,0.17094,0.230769,0.282051,0.29914,...
    ?>

    First row are x values, followed by alternating rows of FROC scores for
    each x value and xxxscore variables which contain FROC scores at
    [1/8     1/4    1/2    1     2    4    8    average] respectively and are
    meant to be plotted in a table

    Returns: string containing html/svg instruction to render an anode09 FROC
    curve of all the variables found in file
    """
    # small nodules, large nodules, isolated nodules, vascular nodules,
    # pleural nodules, peri-fissural nodules, all nodules
    variables = parse_php_arrays(filename)

    assert variables != {}, (
        "parsed result of '%s' was emtpy. I cannot plot anything" % filename
    )

    fig = Figure(facecolor="white")
    canvas = FigureCanvas(fig)
    classes = {
        "small": "nodules < 5mm",
        "large": "nodules > 5mm",
        "isolated": "isolated nodules",
        "vascular": "vascular nodules",
        "pleural": "pleural nodules",
        "fissure": "peri-fissural nodules",
        "froc": "all nodules",
    }
    for key, label in classes.items():
        fig.gca().plot(
            variables["x"], variables[key + "y"], label=label, gid=key
        )
    fig.gca().set_xlim([10 ** -2, 10 ** 2])
    fig.gca().set_ylim([0, 1])
    fig.gca().legend(loc="best", prop={"size": 10})
    fig.gca().grid()
    fig.gca().grid(which="minor")
    fig.gca().set_xlabel("Average FPs per scan")
    fig.gca().set_ylabel("Sensitivity")
    fig.gca().set_xscale("log")
    fig.set_size_inches(8, 6)
    return canvas_to_svg(canvas)


def render_anode09_table(filename):
    """
    Read in a file with the anode09 result format and output html for an
    anode09 table.

    anode09 results have the following format:

    <?php
        $x=array(1e-39,1e-39,1e-39,1e-39,1e-39,1e-39,1e-39,1e-39,1e-39,...
        $frocy=array(0,0.00483092,0.00966184,0.0144928,0.014492,...
        $frocscore=array(0.135266,0.149758,0.193237,0.236715,0.246377,...
        $pleuraly=array(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,...
        $pleuralscore=array(0.0508475,0.0508475,0.0677966,0.118644,...
        $fissurey=array(0,0,0,0.0285714,0.0285714,0.0285714,0.0571429,...
        $fissurescore=array(0.171429,0.171429,0.285714,0.314286,0.314286,...
        $vasculary=array(0,0.0116279,0.0116279,0.0116279,0.0116279,...
        $vascularscore=array(0.116279,0.139535,0.186047,0.209302,0.22093,...
        $isolatedy=array(0,0,0.0238095,0.0238095,0.0238095,0.0238095,...
        $isolatedscore=array(0.238095,0.261905,0.309524,0.380952,...
        $largey=array(0,0.0111111,0.0111111,0.0111111,0.0111111,0.0111111,...
        $largescore=array(0.111111,0.122222,0.144444,0.177778,0.177778,...
        $smally=array(0,0,0.00854701,0.017094,0.017094,0.017094,0.025641,...
        $smallscore=array(0.153846,0.17094,0.230769,0.282051,0.29914,...
    ?>

    First row are x values, followed by alternating rows of FROC scores for
    each x value and xxxscore variables which contain FROC scores at
    [1/8     1/4    1/2    1     2    4    8    average] respectively and are
    meant to be plotted in a table

    Returns: string containing html/svg instruction to render an anode09 FROC
    curve of all the variables found in file
    """
    # small nodules, large nodules, isolated nodules, vascular nodules,
    # pleural nodules, peri-fissural nodules, all nodules
    variables = parse_php_arrays(filename)
    assert variables != {}, (
        "parsed result of '%s' was emtpy. I cannot create table" % filename
    )

    table_id = id_generator()
    table_html = (
        """<table border=1 class = "csvtable sortable" id="%s">
                        <thead><tr>
                            <td class ="firstcol">FPs/scan</td><td align=center width='54'>1/8</td>
                            <td align=center width='54'>1/4</td>
                            <td align=center width='54'>1/2</td><td align=center width='54'>1</td>
                            <td align=center width='54'>2</td><td align=center width='54'>4</td>
                            <td align=center width='54'>8</td><td align=center width='54'>average</td>
                        </tr></thead>"""
        % table_id
    )
    table_html += "<tbody>"
    table_html += array_to_table_row(
        ["small nodules"] + variables["smallscore"]
    )
    table_html += array_to_table_row(
        ["large nodules"] + variables["largescore"]
    )
    table_html += array_to_table_row(
        ["isolated nodules"] + variables["isolatedscore"]
    )
    table_html += array_to_table_row(
        ["vascular nodules"] + variables["vascularscore"]
    )
    table_html += array_to_table_row(
        ["pleural nodules"] + variables["pleuralscore"]
    )
    table_html += array_to_table_row(
        ["peri-fissural nodules"] + variables["fissurescore"]
    )
    table_html += array_to_table_row(["all nodules"] + variables["frocscore"])
    table_html += "</tbody>"
    table_html += "</table>"
    return '<div class="tablecontainer">' + table_html + "</div>"


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    """
    Generate a random ascii string.

    Source: Ignacio Vazquez-Abrams on Stack Overflow
    """
    return "".join(random.choice(chars) for x in range(size))


def array_to_table_row(rowvalues, trclass=""):
    output = '<tr class = "%s">' % trclass
    for value in rowvalues:
        if type(value) is float:
            output = output + "<td>%.3f</td>" % value
        else:
            output = output + "<td>%s</td>" % str(value)
    output = output + "</tr>"
    return output


def parse_php_arrays(filename):
    """
    Parse a php page containing only php arrays like $x=(1,2,3).

    Created to parse anode09 eval results.

    Returns: dict{"varname1",array1,....},
    array1 is a float array
    """
    verbose = False
    output = {}
    storage = DefaultStorage()
    with storage.open(filename, "r") as f:
        content = f.read()
        content = content.replace("\n", "")
        php = re.compile(r"\<\?php(.*?)\?\>", re.DOTALL)
        s = php.search(content)
        assert s is not None, (
            "trying to parse a php array, but could not find anything like &lt;? php /?&gt; in '%s'"
            % filename
        )
        phpcontent = s.group(1)
        phpvars = phpcontent.split("$")
        phpvars = [x for x in phpvars if x != ""]  # remove empty
        if verbose:
            print("found %d php variables in %s. " % (len(phpvars), filename))
            print("parsing %s into int arrays.. " % filename)
        # check whether this looks like a php var
        phpvar = re.compile(
            r"([a-zA-Z]+[a-zA-Z0-9]*?)=array\((.*?)\);", re.DOTALL
        )
        for var in phpvars:
            result = phpvar.search(var)

            if result is None or len(result.groups()) != 2:
                continue

            (varname, varcontent) = result.groups()
            output[varname] = [float(x) for x in varcontent.split(",")]

    return output


@register.tag(name="url_parameter")
def url_parameter(parser, token):
    """Try to read given variable from given url."""
    split = token.split_contents()
    all_args = split[1:]
    if len(all_args) != 1:
        error_message = "Expected 1 argument, found " + str(len(all_args))
        return TemplateErrorNode(error_message)

    else:
        args = {"url_parameter": all_args[0]}
    args["token"] = token
    return UrlParameterNode(args)


class UrlParameterNode(template.Node):
    def __init__(self, args):
        self.args = args

    def make_error_msg(self, msg):
        logger.error(
            "Error in url_parameter tag: '" + ",".join(self.args) + "': " + msg
        )
        errormsg = "Error in url_parameter tag"
        return make_error_message_html(errormsg)

    def render(self, context):
        if self.args["url_parameter"] in context["request"].GET:
            return context["request"].GET[self.args["url_parameter"]]

        else:
            logger.error(
                "Error rendering %s: Parameter '%s' not found in request URL"
                % (
                    "{%  " + self.args["token"].contents + "%}",
                    self.args["url_parameter"],
                )
            )
            error_message = "Error rendering"
            return make_error_message_html(error_message)


class TemplateErrorNode(template.Node):
    """
    Render error message in place of this template tag. This makes it directly
    obvious where the error occured
    """

    def __init__(self, errormsg):
        self.msg = html_encode_django_chars(errormsg)

    def render(self, context):
        return make_error_message_html(self.msg)


def html_encode_django_chars(txt):
    """
    Replace curly braces and percent signs that used in the django template
    tags with their html encoded equivalents.
    """
    txt = txt.replace("{", "&#123;")
    txt = txt.replace("}", "&#125;")
    txt = txt.replace("%", "&#37;")
    return txt


def make_error_message_html(text):
    return (
        '<p><span class="pageError"> '
        + html_encode_django_chars(text)
        + " </span></p>"
    )
