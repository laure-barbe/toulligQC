# -*- coding: utf-8 -*-

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

import pandas as pd
import sys
from toulligqc import graph_generator
import numpy as np
import re
import csv

class albacore_stats_extractor():

    def __init__(self, config_dictionary):
        self.global_dictionnary = {}
        self.config_dictionary = config_dictionary
        self.albacore_log = pd.read_csv(config_dictionary['albacore_summary_source'], sep="\t")
        self.result_directory = config_dictionary['result_directory']
        self.channel = self.albacore_log['channel']
        self.sequence_length_template = self.albacore_log['sequence_length_template']
        self.null_event = self.albacore_log[self.albacore_log['num_events'] == 0]
        self.albacore_log = self.albacore_log.replace([np.inf, -np.inf], 0)
        self.albacore_log = self.albacore_log[self.albacore_log['num_events'] != 0]
        self.fast5_tot = len(self.albacore_log)
        self.is_barcode = config_dictionary['barcoding']
        self.my_dpi = int(config_dictionary['dpi'])

        if self.is_barcode:

            self.barcode_selection = config_dictionary['barcode_selection']

            try:
                self.albacore_log.loc[~self.albacore_log['barcode_arrangement'].isin(
                    self.barcode_selection), 'barcode_arrangement'] = 'unclassified'
            except:
                print('You put the barcode argument but no barcode is present in your sequencing summary file')
                sys.exit(0)

    def init(self):
        return 1

    def check_conf(self):
        return 1

    def extract(self, result_dict):
        if self.is_barcode:
            self.barcode_selection.append('unclassified')
            for index_barcode, barcode in enumerate(self.barcode_selection):
                barcode_selected_dataframe = self.albacore_log[self.albacore_log['barcode_arrangement'] == barcode]
                result_dict['mean_qscore_statistics_' + barcode] = \
                    barcode_selected_dataframe['mean_qscore_template'].describe()
                result_dict['sequence_length_statistics_' + barcode] = \
                    barcode_selected_dataframe['sequence_length_template'].describe()
        else:

            mean_qscore_template = self.albacore_log['mean_qscore_template']
            result_dict['mean_qscore_statistics'] = pd.DataFrame.describe(mean_qscore_template).drop("count")
            result_dict['sequence_length_statistics'] = self.albacore_log['sequence_length_template'].describe()

        result_dict['channel_occupancy_statistics'] = self._occupancy_channel()
        result_dict['sequence_length_template'] = self.sequence_length_template
        result_dict['run_date'] = self._run_date()
        return result_dict

    # def check_conf():
    #     #self.config_dictionary['dpi'] = 100
    #     return



    def graph_generation(self):
        images = []
        title, image_path = graph_generator.read_count_histogram(self.albacore_log, self.my_dpi, self.result_directory)
        images.append((title, image_path))
        title, image_path = graph_generator.read_quality_boxplot(self.albacore_log, self.my_dpi, self.result_directory)
        images.append((title, image_path))
        title, image_path = graph_generator.channel_count_histogram(self.albacore_log, self.my_dpi, self.result_directory)
        images.append((title, image_path))
        title, image_path = graph_generator.read_number_run(self.albacore_log,self. my_dpi, self.result_directory)
        images.append((title, image_path))
        title, image_path = graph_generator.read_length_histogram(self.albacore_log, self.my_dpi, self.result_directory)
        images.append((title, image_path))
        if self.is_barcode:
            title, image_path = graph_generator.barcode_percentage_pie_chart(self.albacore_log, self.barcode_selection, self.my_dpi, self.result_directory)
            images.append((title, image_path))
            title, image_path = graph_generator.barcode_length_boxplot(self.albacore_log, self.barcode_selection, self.my_dpi, self.result_directory)
            images.append((title, image_path))
            title, image_path = graph_generator.barcoded_phred_score_frequency(self.albacore_log, self.barcode_selection, self.my_dpi, self.result_directory)
            images.append((title, image_path))


        channel_count = self.channel
        total_number_reads_per_pore = pd.value_counts(channel_count)
        title, image_path = graph_generator.plot_performance(total_number_reads_per_pore, self.my_dpi, self.result_directory)
        images.append((title, image_path))
        #####title, image_path = graph_generator.occupancy_pore()
        ######images.append((title, image_path))
        title, image_path = graph_generator.phred_score_frequency(self.albacore_log, self.my_dpi, self.result_directory)
        images.append((title, image_path))
        title, image_path = graph_generator.scatterplot(self.albacore_log, self.my_dpi, self.result_directory)
        images.append((title, image_path))
        return images

    def clean(self):
        return

    def _occupancy_channel(self):
        channel_count = self.channel
        total_number_reads_per_channel = pd.value_counts(channel_count)
        channel_count_statistics = pd.DataFrame.describe(total_number_reads_per_channel)
        return channel_count_statistics

    def _run_date(self):
        """
        Returns the date of a Minion run from the log file provided by albacore
        """
        file_name = self.albacore_log['filename'].iloc[0]
        pattern = re.search(r'(_(\d+)_)', file_name)
        return pattern.group(2)

