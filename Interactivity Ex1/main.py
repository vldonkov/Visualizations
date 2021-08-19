import pandas as pd 
import numpy as np
import bokeh.palettes as bp
from bokeh.plotting import figure
from bokeh.io import output_file, show, save
from bokeh.models import ColumnDataSource, HoverTool, ColorBar, RangeTool
from bokeh.transform import linear_cmap
from bokeh.layouts import gridplot


# ==========================================================================
# Goal: Visualize Covid-19 Tests statistics in Switzerland with linked plots
# Dataset: covid19_tests_switzerland_bag.csv
# Data Interpretation: 
# 		n_negative: number of negative cases in tests
# 		n_positive: number of positive cases in tests
# 		n_tests: number of total tests
# 		frac_negative: fraction of POSITIVE cases in tests
# ==========================================================================



### Task1: Data Preprocessing


## T1.1 Read the data to the dataframe "raw"
# You can read the latest data from the url, or use the data provided in the folder (update Nov.3, 2020)

# url = 'https://github.com/daenuprobst/covid19-cases-switzerland/blob/master/covid19_tests_switzerland_bag.csv'
raw = pd.read_csv("covid19_tests_switzerland_bag.csv")



## T1.2 Create a ColumnDataSource containing: date, positive number, positive rate, total tests
# All the data can be extracted from the raw dataframe.

date = pd.to_datetime(raw.date.tolist())
pos_num = raw.n_positive.tolist()
pos_rate = raw.frac_positive.tolist()
test_num = raw.n_tests.tolist()

source_dict = {'date':date,
               'pos_num':pos_num,
               'pos_rate':pos_rate,
               'test_num':test_num}

source = ColumnDataSource(data=source_dict)


## T1.3 Map the range of positive rate to a colormap using module "linear_cmap"
# "low" should be the minimum value of positive rates, and "high" should be the maximum value

low = min(pos_rate)
high = max(pos_rate)
mapper = linear_cmap('pos_rate',bp.Inferno256,low,high)




### Task2: Data Visualization
# Reference link:
# (range tool example) https://docs.bokeh.org/en/latest/docs/gallery/range_tool.html?highlight=rangetool


## T2.1 Covid-19 Total Tests Scatter Plot
# x axis is the time, and y axis is the total test number. 
# Set the initial x_range to be the first 30 days.

TOOLS = "box_select,lasso_select,wheel_zoom,pan,reset,help"
p = figure(x_axis_type="datetime",x_range = (date[0],date[29]),plot_height=600,tools=TOOLS)
p.scatter('date','test_num',size=10,color=mapper,line_width=1,line_color="blue",source = source)

p.title.text = 'Covid-19 Tests in Switzerland'
p.yaxis.axis_label = "Total Tests"
p.xaxis.axis_label = "Date"
p.sizing_mode = "stretch_both"

# Add a hovertool to display date, total test number
hover = HoverTool(tooltips=[("Date", "@date{%F}"),
							('Total tests','@test_num')
                            ],
                  formatters={'@date': 'datetime'})
p.add_tools(hover)


## T2.2 Add a colorbar to the above scatter plot; please use the color mapper defined in T1.3

color_bar = ColorBar(color_mapper=mapper["transform"],title="P_Rate",location=(0,0))
p.add_layout(color_bar, 'right')




## T2.3 Covid-19 Positive Number Plot using RangeTool
# In this range plot, x axis is the time, and y axis is the positive test number.

select = figure(title="Drag the middle and edges of the selection box to change the range above",
                x_axis_type="datetime",plot_height=250,tools="", toolbar_location=None)

# Define a RangeTool to link with x_range in the scatter plot
range_tool = RangeTool(x_range=p.x_range)
range_tool.overlay.fill_color = "green"
range_tool.overlay.fill_alpha = 0.2


# Draw a line plot and add the RangeTool to the plot
select.line('date', 'pos_num', source=source)
select.yaxis.axis_label = "Positive Cases"
select.xaxis.axis_label = "Date"
select.ygrid.grid_line_color = None
select.add_tools(range_tool)
select.toolbar.active_multi = range_tool



# Add a hovertool to the range plot and display date, positive test number
hover2 = HoverTool(tooltips=[("Date", "@date{%F}"),
							('Positive tests','@pos_num')
                            ],
                  formatters={'@date': 'datetime'})
select.add_tools(hover2)


## T2.4 Layout arrangement and display

linked_p = gridplot([p,select],ncols=1,sizing_mode='stretch_width')
show(linked_p)
output_file("main.html")
save(linked_p)

