import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
import plotly.express as px
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc

# Column variables created to make code maintainable and avoid typo's
quote_number = "Quote Number"
transaction_date = "Transaction Date"
test_group = "Test Group"
sale_indicator = "Sale Indicator"
net_price = "Net Price"
profit = "Profit"
tax = "Tax"
total_price = "Total Price"
customer_age = "Customer Age"
licence_length = "Licence Length"
marital_status = "Marital Status"
credit_score = "Credit Score"
vehicle_mileage = "Vehicle Mileage"
vehicle_value = "Vehicle Value"

df = pd.read_csv('../resources/hastingsdata.csv')
dp = df  # Create a duplicate of the table to per form operations
dp[transaction_date] = pd.to_datetime(dp[transaction_date])  # Convert Date column from string format to date
# dp = dp.iloc[1:, :]  # Get rid of the first row as they are column names
dp[customer_age] = pd.to_numeric(dp[customer_age])  # Convert age column from string to numeric value
dp[licence_length] = dp[licence_length].apply(np.ceil)  # Apply a round function on Licence Length to get graph
dupli = dp[[quote_number, transaction_date, test_group, net_price, profit, customer_age, vehicle_mileage, vehicle_value, credit_score, marital_status, tax]]
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])  # Apply theme

# The layout for the dashboard
app.layout = html.Div([
    dbc.Row(dbc.Col(html.H3("DashBoard"),
                    width={'size': 6, 'offset': 5},
                    ),
            ),
    dbc.Row(
        [
            dbc.Col(dcc.Dropdown(id='Metrics',
                                 options=[
                                     {'label': customer_age, 'value': customer_age},
                                     {'label': vehicle_value, 'value': vehicle_value},
                                     {'label': vehicle_mileage, 'value': vehicle_mileage},
                                     {'label': 'By Day', 'value': transaction_date},
                                     {'label': 'By Week', 'value': 'By Week'},
                                     {'label': licence_length, 'value': licence_length},
                                     {'label': credit_score, 'value': credit_score}
                                 ], value="Customer Age"
                                 ),
                    width={'size': 4, "offset": 4, 'order': 3}
                    )], className="h-20"
    ),

    dbc.Row([html.Br()
             ]),

    dbc.Row(
        [
            dbc.Col(dcc.Graph(id='my-graph-Profit', figure={}),
                    width=4, lg={'size': 4, "offset": 0, 'order': 'first'}
                    ),
            dbc.Col(dcc.Graph(id='my-graph-NetPrice', figure={}),
                    width=4, lg={'size': 4, "offset": 0, 'order': 'last'}
                    ),
            dbc.Col(dcc.Graph(id='my-graph-TotalPrice', figure={}),
                    width=4, lg={'size': 4, "offset": 0, 'order': 'first'}
                    ),

        ], justify="around"
    ),

    dbc.Row([html.Br()
             ]),

    dbc.Row(
        [
            dbc.Col(
                dash_table.DataTable(id='mydatatable',
                                     columns=[
                                         {'name': quote_number, 'id': quote_number, 'type': 'numeric',
                                          'editable': False},
                                         {'name': transaction_date, 'id': transaction_date, 'type': 'datetime',
                                          'editable': False},
                                         {'name': test_group, 'id': test_group, 'type': 'text', 'editable': True},
                                         {'name': net_price, 'id': net_price, 'type': 'float', 'editable': True},
                                         {'name': profit, 'id': profit, 'type': 'float', 'editable': True},
                                         {'name': customer_age, 'id': customer_age, 'type': 'numeric',
                                          'editable': True},
                                         {'name': vehicle_mileage, 'id': vehicle_mileage, 'float': 'numeric',
                                          'editable': True},
                                         {'name': vehicle_value, 'id': vehicle_value, 'float': 'numeric',
                                          'editable': True},
                                         {'name': credit_score, 'id': credit_score, 'float': 'numeric',
                                          'editable': True},
                                         {'name': marital_status, 'id': marital_status, 'text': 'numeric',
                                          'editable': True},
                                         {'name': tax, 'id': tax, 'type': 'float',
                                          'editable': True},
                                     ], data=dupli.to_dict('records'), page_size=10, editable=True),
                width=4, lg={'size': 12, "offset": 0, 'order': 'first'}
            )

        ],
    ),

    dbc.Row([
        dbc.Col(html.Button('Add Row', id='editing-rows-button', n_clicks=0),
                width=4, lg={'size': 4, "offset": 0, 'order': 'first'}
                ),
        ]),

])


# This is a call back function for getting the profit graphs
@app.callback(
    Output(component_id="my-graph-Profit", component_property='figure'),
    Input(component_id="Metrics", component_property='value')
)
# This method helps calculate the profit from the different metrics selected.
def calculate_gross_profit(value_metrics):
    if value_metrics == transaction_date:
        td = dp.sort_values(by=transaction_date)
        fd = td.groupby(value_metrics)
        return setup_graph(fd, "scatter", profit)
    elif value_metrics == "By Week":
        bw = dp.groupby([test_group, pd.Grouper(key=transaction_date, freq='W')])[profit].sum().reset_index()\
            .sort_values(transaction_date)
        fd = bw.groupby(transaction_date)
        return setup_graph(fd, "scatter", profit)
    elif value_metrics == licence_length:
        fd = dp.groupby(licence_length)
        return setup_graph(fd, "line", profit)
    else:
        fd = dp.groupby(value_metrics)
        return setup_graph(fd, "line", profit)


# This is a call back for the net price
@app.callback(
    Output(component_id="my-graph-NetPrice", component_property='figure'),
    Input(component_id="Metrics", component_property='value')
)
# This method calculates the net price of the metric given
def calculate_net_price(value_metrics):
    if value_metrics == transaction_date:
        td = dp.sort_values(by=transaction_date)
        fd = td.groupby(value_metrics)
        return setup_graph(fd, "scatter", net_price)
    elif value_metrics == "By Week":
        bw = dp.groupby([test_group, pd.Grouper(key=transaction_date, freq='W')])[
            net_price].sum().reset_index().sort_values(transaction_date)
        fd = bw.groupby(transaction_date)
        return setup_graph(fd, "scatter", net_price)
    elif value_metrics == licence_length:
        fd = dp.groupby(licence_length)
        return setup_graph(fd, "line", net_price)
    else:
        fd = dp.groupby(value_metrics)
        return setup_graph(fd, "line", net_price)


# App callback for totalPrice
@app.callback(
    Output(component_id="my-graph-TotalPrice", component_property='figure'),
    Input(component_id="Metrics", component_property='value')
)
# This method calculates Total Price and takes the metrics by which the graph should be plotted
def calculate_total_price(value_metrics):
    if value_metrics == transaction_date:
        td = dp.sort_values(by=value_metrics)
        fd = td.groupby(value_metrics)
        return setup_graph(fd, "scatter", total_price)
    elif value_metrics == "By Week":
        bw = dp.groupby([test_group, pd.Grouper(key=transaction_date, freq='W')])[
            total_price].sum().reset_index().sort_values(transaction_date)
        fd = bw.groupby(transaction_date)
        return setup_graph(fd, "scatter", total_price)
    elif value_metrics == licence_length:
        dkk = dp.groupby(licence_length)
        return setup_graph(dkk, "line", total_price)
    else:
        fd = dp.groupby(value_metrics)
        return setup_graph(fd, "line", total_price)


@app.callback(
    Output('mydatatable', 'data'),
    Input('editing-rows-button', 'n_clicks'),
    State('mydatatable', 'data'),
    State('mydatatable', 'columns'))
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c[quote_number]: '' for c in columns})
    return rows


# This method creates a chart to represent the data provided
def setup_graph(dataset, type_of_graph, y_axis):
    # if statement to check the type of graph to plot
    if type_of_graph == "line":
        fig = px.line(dataset.first(), y=y_axis, color=test_group, title=y_axis)
    else:
        fig = px.scatter(dataset.first(), y=y_axis, color=test_group, title=y_axis)
    return fig


if __name__ == '__main__':
    app.run_server()
