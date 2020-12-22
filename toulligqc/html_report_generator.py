# -*- coding: utf-8 -*-
#
#                  ToulligQC development code
#
# This code may be freely distributed and modified under the
# terms of the GNU General Public License version 3 or later
# and CeCILL. This should be distributed with the code. If you
# do not have a copy, see:
#
#      http://www.gnu.org/licenses/gpl-3.0-standalone.html
#      http://www.cecill.info/licences/Licence_CeCILL_V2-en.html
#
# Copyright for this code is held jointly by the Genomic platform
# of the Institut de Biologie de l'École Normale Supérieure and
# the individual authors.
#
# For more information on the ToulligQC project and its aims,
# visit the home page at:
#
#      https://github.com/GenomicParisCentre/toulligQC
#
# First author: Lionel Ferrato-Berberian
# Maintainer: Bérengère Laffay
# Since version 0.1

# Generates a quality control report in HTML format including graphs and statistical tables
import base64
import datetime
import pkgutil


def html_report(config_dictionary, result_dict, graphs):
    """
    Creation of a html report
    :param config_dictionary: dictionary containing file or directory paths
    :param result_dict: result dictionary containing all statistics
    :param graphs:
    """

    result_directory = config_dictionary['result_directory']
    report_name = config_dictionary['report_name']


    report_date = result_dict['toulligqc.info.start.time']

    # from Fast5 file
    run_date = result_dict['sequencing.telemetry.extractor.exp.start.time']
    run_id = result_dict['sequencing.telemetry.extractor.sample.id']


    # Read CSS file resource
    css = pkgutil.get_data(__name__, "resources/toulligqc.css").decode('utf8')

    # Read Plotly JavaScript code
    plotly_min_js = pkgutil.get_data(__name__, "resources/plotly-latest.min.js").decode('utf8')

    f = open(result_directory + 'report.html', 'w')

    # Create the report
    report = """<!doctype html>
<html>
  <head>
    <title>Report run MinION : {report_name} </title>
    <meta charset='UTF-8'>
    <script>{plotlyjs}</script>

    <!-- CSS stylesheet -->
    <style type="text/css">
    {css}
    </style>

  </head>

    <!-- The banner -->
    <div class="header">
      <div id="header_title">ToulligQC report for {report_name} <br/></div>
      <div id="header_filename">
        Run id: {run_id} <br>
        Report name: {report_name} <br>
        Run date: {run_date} <br>
        Report date : {report_date} <br>
      </div>
    </div>

    <!-- The summary -->
    <div class='summary'>
      <h2>Summary</h2>
      {summary_list}
    </div>

    <!-- Module results -->
    <div class = 'main'>
    {modules_report}
    </div>

    <!-- Footer -->
    <div class="footer"> Produced by <a href="{app_url}">{app_name}</a> (version {app_version})</div>
  </body>

</html>""".format(report_name=report_name,
                  plotlyjs=plotly_min_js,
                  css=css,
                  run_id=run_id,
                  run_date=run_date,
                  report_date=report_date,
                  summary_list=_summary(graphs),
                  modules_report=_modules_report(graphs, result_dict, run_id, report_name, run_date, config_dictionary['app.version']),
                  app_url=config_dictionary['app.url'],
                  app_name=config_dictionary['app.name'],
                  app_version=config_dictionary['app.version'])

    # Write the HTML page
    f.write(report)
    f.close()

def _summary(graphs):
    """
    Compose the summary section of the page
    :param graphs:
    :return: a string with HTML code for the module list
    """
    result = "        <ol>\n"
    result += "          <li><a href=\"#Basic-statistics" "\"> Basic Statistics </a></li>\n"
    for i, t in enumerate(graphs):
        result += "          <li><a href=\"#M" + str(i) + "\">" + t[0] + "</a></li>\n"
    result += "        </ol>\n"
    return result


def _modules_report(graphs, result_dict, run_id, report_name, run_date, toulligqc_version):

    result =  _basic_statistics_module_report(result_dict, run_id, report_name, run_date, toulligqc_version)
    result += _other_module_reports(graphs)
    return result

def _basic_statistics_module_report(result_dict, run_id, report_name, run_date, toulligqc_version):

    minknow_version = result_dict['sequencing.telemetry.extractor.minknow.version']

    td = datetime.timedelta(hours=result_dict["basecaller.sequencing.summary.1d.extractor.run.time"])
    seconds = td.total_seconds()
    run_time = '%d:%02d:%02d' % (seconds / 3600, seconds / 60 % 60, seconds % 60)

    read_count = result_dict["basecaller.sequencing.summary.1d.extractor.read.count"]
    run_yield = round(result_dict["basecaller.sequencing.summary.1d.extractor.yield"]/1000000000, 2)
    n50 = result_dict["basecaller.sequencing.summary.1d.extractor.n50"]

    # from telemetry file
    flow_cell_id = result_dict['sequencing.telemetry.extractor.flowcell.id']
    flowcell_version = _get_result_value(result_dict, 'sequencing.telemetry.extractor.flowcell.version', "Unknown")
    kit_version = _get_result_value(result_dict, 'sequencing.telemetry.extractor.kit.version', "Unknown")
    basecaller_name = _get_result_value(result_dict, 'sequencing.telemetry.extractor.software.name', "Unknown")
    basecaller_version = _get_result_value(result_dict, 'sequencing.telemetry.extractor.software.version', "Unknown")
    basecaller_analysis = _get_result_value(result_dict, 'sequencing.telemetry.extractor.software.analysis', "Unknown")
    hostname = _get_result_value(result_dict, 'sequencing.telemetry.extractor.hostname', "Unknown")
    device_id = _get_result_value(result_dict, 'sequencing.telemetry.extractor.device.id', "Unknown")
    device_type = _get_result_value(result_dict, 'sequencing.telemetry.extractor.device.type', "Unknown")
    model_file = _get_result_value(result_dict, 'sequencing.telemetry.extractor.model.file', "Unknown")
    sample_id = _get_result_value(result_dict, 'sequencing.telemetry.extractor.sample.id', "Unknown")

    # Compose the main of the page
    result = """
      <div class=\"module\" id="Basic-statistics">
        <div class = "info-box">
            <h2 id=M{0}>Basic Statistics</h2>
            <h2 id=M{0}></h2>
            <h3 style="text-align:center">Run info</h3>
            <table class=\" dataframe \" border="1">
              <thead><tr><th>Measure</th><th>Value</th></tr></thead>
              <tbody>
              <tr><th>Run id</th><td> {0} </td></tr>
              <tr><th>Sample</th><td> {1} </td></tr>
              <tr><th>Report name </th><td> {2} </td></tr>
              <tr><th>Run date</th><td> {3} </td></tr>
              <tr><th>Run duration </th><td> {4} </td></tr>
              <tr><th>Flowcell id </th><td> {5} </td></tr>
              <tr><th>Flowcell version</th><td> {6} </td></tr>
              <tr><th>Kit</th><td> {7} </td></tr>
              <tr><th>Yield (Gbp)</th><td> {8} </td></tr>
              <tr><th>Read count</th><td> {9} </td></tr>
              <tr><th>N50 (bp)</th><td> {10} </td></tr>
              </tbody>
            </table>
        </div> <!-- end .info-box -->
      </div>
    """.format(run_id,sample_id, report_name, run_date, run_time, flow_cell_id, flowcell_version, kit_version, run_yield, read_count, n50)

    result += """
      <div class=\"module\">
        <div class = "info-box-left">
            <h2 id=M{0}></h2>
            <h2 id=M{0}></h2>
            <h3 style="text-align:center">Software info</h3>
            <table class=\" dataframe \" border="1">
                <thead><tr><th>Measure</th><th>Value</th></tr></thead>
                <tbody>
                <tr><th>MinKNOW version </th><td> {0} </td></tr>
                <tr><th>Basecaller name</th><td> {1} </td></tr>
                <tr><th>Basecaller version</th><td> {2} </td></tr>
                <tr><th>Basecaller analysis</th><td> {3} </td></tr>
                <tr><th>ToulligQC version</th><td> {4} </td></tr>
                <tr><th>Hostname</th><td> {5} </td></tr>
                <tr><th>Device</th><td> {6} </td></tr>
                <tr><th>Device ID</th><td> {7} </td></tr>
                <tr><th>Model file</th><td> {8} </td></tr>
                </tbody>
            </table>
        </div> <!-- end .info-box-left -->
        <div class=\"after-box\"><p></p></div>
      </div>
    """.format(minknow_version, basecaller_name, basecaller_version, basecaller_analysis, toulligqc_version, hostname, device_type, device_id, model_file)

    return result

def _other_module_reports(graphs):

    result = ""

    for i, t in enumerate(graphs):


      if len(t)==5:
       # Plotly Graph

        name, path, table, tip, html = t

       # Plotly graph with table
        if table is not None:
            result += """
      <div class="module" id=M{i}></div>
      {html}
      <div class="box-left">
      {table}
      </div>
      <div class="after-box"><p></p></div>
""".format(i=i, html=html, table=table)

        # Plotly graph without table
        else:
            result += """
      <div class="module" id=M{i}></div>
      {html}
      <div class="after-box"><p></p></div>
""".format(i=i, html=html, table=table)


      elif len(t)==4:
          # image
          name, path, table, tip = t

          # Image with table
          if table is not None:
              result += """
            <div class="module" id=M{i}>
              <h2>{name} <a title="{tip}">&#x1F263;</a></h2>
            </div>
            <div class="box"><img src="{image}">" "</div>
            <div class=\"box-left\">
            {table}
            </div>
            <div class="after-box"><p></p></div>
            """.format(i=i, name=name, tip=tip, image=_embedded_image(path), table=table)

          # Image without table
          else:
              result += """
            <div class="module" id=M{i}>
              <h2>{name} <a title="{tip}">&#x1F263;</a></h2>
            </div>
            <div class="box"><img src="{image}">" "</div>
            <div class="after-box"><p></p></div>
            """.format(i=i, name=name, tip=tip, image=_embedded_image(path))

    return result


def _embedded_image(image_path):
    """
    Embedded an image
    :param image_path: path of the image
    :return: a string with the image in base64
    """
    with open(image_path, "rb") as image_file:
        result = "data:image/png;base64," + base64.b64encode(image_file.read()).decode('ascii')

    return result


def _get_result_value(result_dict, key , default_value = ""):
    """
    Get the value of the result dictionary or a default value if the key does not exists.
    :param result_dict: result dictionary
    :param key: the key to use
    :param default_value: the default value
    :return: the value of key in the dictionary or the default value if the key does not exists in the dictionary
    """
    if key in result_dict:
        return result_dict[key]
    else:
        return default_value
