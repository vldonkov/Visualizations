import numpy as np
from bokeh.models import ColumnDataSource, Button, Select, Div
from bokeh.sampledata.iris import flowers
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, row

# Important: You must also install pandas for the data import.

# calculate the cost of the current medoid configuration
# The cost is the sum of all minimal distances of all points to the closest medoids
def get_cost(meds):
    dist_1 = np.linalg.norm(data.iloc[:, 0:4] - data.iloc[meds[0], 0:4],ord=1,axis=1)
    dist_2 = np.linalg.norm(data.iloc[:, 0:4] - data.iloc[meds[1], 0:4],ord=1,axis=1)
    dist_3 = np.linalg.norm(data.iloc[:, 0:4] - data.iloc[meds[2], 0:4],ord=1,axis=1)
    return np.sum(np.amin(np.column_stack((dist_1, dist_2, dist_3)),axis = 1))

# implement the k-medoids algorithm in this function and hook it to the callback of the button in the dashboard
# check the value of the select widget and use random medoids if it is set to true and use the pre-defined medoids
# if it is set to false
def k_medoids():
    # number of clusters:
    k = 3
    # Use the following medoids if random medoid is set to false in the dashboard. These numbers are indices into the
    # data array. If random medoids is set to true, generate random indices
    if medoids_select.value == 'False':
        medoids = [24, 74, 124]
    else:
        rng = np.random.default_rng()
        medoids = rng.choice(len(data), size=3, replace=False).tolist()

    # Implement greedy algorithm for finding the optimal medoids
    j_index_new = None
    while True:
        cost_clustering_begin = get_cost(medoids)
        cost_clustering_end = cost_clustering_begin
        non_medoids = [x for x in data.index.to_list() if x not in medoids]
        medoids_index = [x for x in list(range(k)) if x not in [j_index_new]]
        for j_index in medoids_index:
            for i in non_medoids:
                medoids_new = medoids.copy()
                medoids_new[j_index] = i
                cost_clustering_temp = get_cost(medoids_new)
                if cost_clustering_temp < cost_clustering_end:
                    cost_clustering_end = cost_clustering_temp
                    j_index_new = j_index
                    i_new = i
        if cost_clustering_end < cost_clustering_begin:
            medoids[j_index_new] = i_new
        else:
            break

    # Assign colors to the data points, according to which cluster they belong to
    dist_1 = np.linalg.norm(data.iloc[:, 0:4] - data.iloc[medoids[0], 0:4],ord=1,axis=1)
    dist_2 = np.linalg.norm(data.iloc[:, 0:4] - data.iloc[medoids[1], 0:4],ord=1,axis=1)
    dist_3 = np.linalg.norm(data.iloc[:, 0:4] - data.iloc[medoids[2], 0:4],ord=1,axis=1)
    colors_list = np.argmin(np.column_stack((dist_1, dist_2, dist_3)),axis = 1).astype(str)
    colors_list = np.where(colors_list == '0', "red", colors_list)
    colors_list = np.where(colors_list == '1', "green", colors_list)
    colors_list = np.where(colors_list == '2', "blue", colors_list)

    # Update plots with new clustering results
    new_data = dict(sepal_length=data['sepal_length'].tolist(),
                    sepal_width=data['sepal_width'].tolist(),
                    petal_length=data['petal_length'].tolist(),
                    petal_width=data['petal_width'].tolist(),
                    color=colors_list.tolist()
                    )
    source.data = new_data

    # Update DIV element with new clustering cost
    cluster_cost_text.text = "The final cost is: {:.2f}".format(cost_clustering_end)


# read and store the dataset
data = flowers.copy(deep=True)
data = data.drop(['species'], axis=1)

# create a color column in your dataframe and set it to gray on startup
data['color'] = "gray"

# Create a ColumnDataSource from the data
source = ColumnDataSource(data)

# Create a select widget, a button, a DIV to show the final clustering cost and two figures for the scatter plots.

# Creating first plot
p1 = figure(sizing_mode="scale_width")
p1.scatter('petal_length','sepal_length',color='color', size=5,
           line_width=1, fill_alpha=0.2,source = source)
p1.title.text = 'Scatterplot of flower distribution by petal length and sepal length'
p1.yaxis.axis_label = "Sepal length"
p1.xaxis.axis_label = "Petal length"

# Creating second plot
p2 = figure(sizing_mode="scale_width")
p2.scatter('petal_width','petal_length',color='color', size=5,
           line_width=1, fill_alpha=0.2,source = source)
p2.title.text = 'Scatterplot of flower distribution by petal width and petal length'
p2.yaxis.axis_label = "Petal length"
p2.xaxis.axis_label = "Petal width"

# Creating select widget
medoids_select = Select(title='Random Medoids', value='False', options=['True', 'False'],sizing_mode="stretch_both")

# Creating cluster button and attaching k_medoids callback to it
cluster_button = Button(label="Cluster data",sizing_mode="stretch_both")
cluster_button.on_click(k_medoids)

# Create DIV element
cluster_cost_text = Div(text = "The final cost is: 0.00",sizing_mode="stretch_both")

# use curdoc to add your widgets to the document
lt = row(column(medoids_select,cluster_button,cluster_cost_text,sizing_mode="fixed", height = 100, width=300),
         p1,p2,sizing_mode="stretch_both")
curdoc().add_root(lt)
curdoc().title = "Kmedoids"

# use on of the commands below to start your application
# bokeh serve --show kmedoids.py
# python -m bokeh serve --show kmedoids.py
# bokeh serve --dev --show kmedoids.py
# python -m bokeh serve --dev --show kmedoids.py