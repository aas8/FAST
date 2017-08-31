'''
This file is part of an ICSE'18 submission that is currently under review. 
For more information visit: https://github.com/icse18-FAST/FAST.
    
This is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as 
published by the Free Software Foundation, either version 3 of the 
License, or (at your option) any later version.

This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this source.  If not, see <http://www.gnu.org/licenses/>.
'''

import os
import plotly
import plotly.graph_objs as go
import sys


usage = """USAGE: python tools/plot-scalability-results.py <tcsize> <time> <algorithm> ... <algorithm>
OPTIONS:
  <tcsize>: size of test cases considered for the plot.
    options: small, medium, large
  <time>: time considered for the plot.
    options: prioritization, total
  <algorithm>: algorithm to include in the plot.
    options: FAST-pw, FAST-1, FAST-log, FAST-sqrt, FAST-all,
             STR, I-TSD,
             ART-D, ART-F, GT, GA, GA-S
EXAMPLE:
  To compare all the FAST approaches using large test cases and considering only prioritization time, the right usage is
  python tools/plot-scalability-results.py large prioritization FAST-pw FAST-one FAST-log FAST-sqrt FAST-all"""


def parse_results_file():
    results = {}
    filename = "results/RQ3-ScalabilityResults.tsv"
    with open(filename, "r") as fin:
        count = 0
        for line in fin:
            count += 1
            if count == 1:
                continue
            tokens = line.split("\t")
            approach = tokens[0].strip()
            tssize = int(tokens[1].strip())
            tcsize = int(tokens[2].strip())
            stime = float(tokens[3].strip())
            ptime = float(tokens[4].strip())
            ttime = float(tokens[5].strip())
            print "approach: {}, tssize: {}, tcsize: {}, stime: {}, ptime: {}, ttime: {}".format(approach, tssize, tcsize, stime, ptime, ttime)
            try:
                results[approach][tcsize].update({tssize: {'stime': stime, 'ptime': ptime, 'ttime': ttime}})
            except KeyError:
                try:
                    results[approach].update({tcsize: {tssize: {'stime': stime, 'ptime': ptime, 'ttime': ttime}}})
                except KeyError:
                    results.update({approach: {tcsize: {tssize: {'stime': stime, 'ptime': ptime, 'ttime': ttime}}}})
    return results

#===============================================================================
# Filter data and add traces to the plot
#===============================================================================

#for target_time in ['ttime', 'ptime']
def get_traces_to_plot(results):
    data = []
    for approach in target_app:
        times = []
        for ts_size in ts_sizes:
            try:
                if ts_size in results[approach][target_tc]:
                    v = results[approach][target_tc][ts_size][target_time]
                    if v <= 7200:  # 2 hours
                        times.append(v)
                else:
                    times.append(None)
            except KeyError:
                print 'approach, ts_size: ', approach, ts_size
        trace = go.Scatter(
            x=ts_sizes,
            y=times,
            mode='lines+markers',
            name=names_map[approach],
            # marker=plot_style[approach],
            # line=plot_line_style[approach],
        )
        data.append(trace)
    return data



#===============================================================================
# Configure and export the line plot
#===============================================================================
def get_layout():
    tc_size_map = {1000: "Small", 10000: "Medium", 100000: "Large"}
    target_time_map = {
        'ttime': 'Total Time (preparation + prioritization)',
        'ptime': 'Prioritization Time'
    }

    x_max = 1000000 + 5000
    x_min = 0

    layout = dict(
        title=target_time_map[target_time],
        xaxis=dict(title='Test Suite Size', range=[x_min, x_max],),
        yaxis=dict(title='Time (in seconds)', range=[0, 7300],),
        # xaxis=dict(
        #     range=[x_min, x_max],
        #     # tickfont=dict(
        #     #     size=22,
        #     # ),
        # ),
        # yaxis=dict(
        #     range=[0, 7300],
        #     # tickfont=dict(
        #     #     size=22,
        #     # ),
        # ),
        shapes=[
            {  # 1 hour dotted line
                'type': 'line',
                'x0': 0,
                'y0': 3600,
                'x1': x_max,
                'y1': 3600,
                'line': {
                    'color': 'red',
                    'width': 1,
                    'dash': 'dot',
                }
            },
            # {  # 2 hours dotted line
            #     'type': 'line',
            #     'x0': 0,
            #     'y0': 7200,
            #     'x1': x_max,
            #     'y1': 7200,
            #     'line': {
            #         'color': 'red',
            #         'width': 1,
            #         'dash': 'dot',
            #     }
            # }
        ],
        annotations=[
            dict(  # 1 hour annotation
                x=x_max - 35000,
                y=3750,
                xref='x',
                yref='y',
                text=' 1 hour',
                showarrow=False,
                arrowhead=7,
                ax=0,
                ay=0,
                font=dict(
                    color="red",
                )
            ),
            # dict(  # 2 hours annotation
            #     x=x_max - 35000,
            #     y=7300,
            #     xref='x',
            #     yref='y',
            #     text='2 hours',
            #     showarrow=False,
            #     arrowhead=7,
            #     ax=0,
            #     ay=0,
            #     font=dict(
            #         color="red",
            #     )
            # )
        ],
        margin=dict(
            l=80,
            r=50,
            b=50,
            t=50,
            pad=10
        ),
        # legend
        showlegend=True,
        # legend=dict(orientation="h"),
    )
    return layout

def plot(data, layout):
    plotly.offline.plot({"data": data, "layout": layout}, image='svg')


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Wrong input.")
        print(usage)
        exit()
    tcsize, plot_time = sys.argv[1:3]
    target_app = sys.argv[3:]

    algnames = {"FAST-pw", "FAST-one", "FAST-log", "FAST-sqrt", "FAST-all",
                "STR", "I-TSD",
                "ART-D", "ART-F", "GT", "GA", "GA-S"}
    tcsizes = {"small", "medium", "large"}
    times = {"prioritization", "total"}

    for alg in target_app:
        if alg not in algnames:
            print("<algorithm> input incorrect.")
            print(usage)
            exit()
    if tcsize not in tcsizes:
        print("<tcsize> input incorrect.")
        print(usage)
        exit()
    elif plot_time not in times:
        print("<time> input incorrect.")
        print(usage)
        exit()

    target_tc_map = {
        'small': 1000,
        'medium': 10000,
        'large': 100000
    }
    target_time_map = {
        'prioritization': 'ptime',
        'total': 'ttime'
    }

    target_tc = target_tc_map[tcsize]
    target_time = target_time_map[plot_time]

    ts_sizes = (
        range(1000, 10000, 1000) +
        range(10000, 100000, 10000) +
        range(100000, 1000000+1, 100000)
    )
    # display names
    names_map = {
        'FAST-pw': 'FAST-pw',
        'FAST-one': 'FAST-one',
        'FAST-all': 'FAST-all',
        'FAST-sqrt': 'FAST-sqrt',
        'FAST-logSq': 'FAST-logSq',
        'FAST-log': 'FAST-log',
        'GA': 'GA',
        'GT': 'GT',
        'GA-S': 'GA-S',
        'I-TSD': 'I-TSD',
        'ART-D': 'ART-D',
        'ART-F': 'ART-F',
        'STR': 'STR'
    }

    # dict
    results = parse_results_file()
    data = get_traces_to_plot(results)
    #print type(data[4]), len(data[4]), data[4]
    #exit()
    layout = get_layout()
    plot(data, layout)

    os.rename(
        "temp-plot.html",
        "scalability/plots/{}_{}_{}.html".format(
            tcsize, plot_time, "_".join(sorted(target_app))
        )
    )
