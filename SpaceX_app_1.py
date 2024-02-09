# Import required libraries
import pandas as pd
import dash
from dash import html,dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
#                                 dcc.Dropdown(
#                                             id='site-dropdown',
#                                             options=[
#                                                 {'label': 'All Sites', 'value': 'All Sites'}
#                                             ] + [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
#                                              value='ALL',
#                                              multi=False,
#                                              style={'width': '80%'}
#                                              ),
#
                                dcc.Dropdown(id='site-dropdown',
                                options=[
                                    {'label': 'All Sites', 'value': 'All Sites'},
                                    {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
                                ],
                                placeholder='Select a Launch Site Here',
                                value='All Sites',
                                searchable=True
                                ),
                                 html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0,
                                                max=10000,
                                                step=1000,
                                                marks={i: str(i) for i in range(0,10000, 1000)},
                                                value=[min_payload, max_payload]
                                                ),
                                html.Br(),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# @app.callback(
#     Output('success-pie-chart', 'figure'),
#     [Input('site-dropdown', 'value')]
# )
# def update_pie_chart(selected_site):
#     if selected_site == 'ALL':
#         fig = px.pie(spacex_df, names='class', title='Success vs. Failure for All Sites')
#     else:
#         filtered_data = spacex_df[spacex_df['Launch Site'] == selected_site]
#         fig = px.pie(filtered_data, names='class', title=f'Success vs. Failure for {selected_site}')
#     return fig

# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback( Output(component_id='success-pie-chart', component_property='figure'),
               Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(launch_site):
    if launch_site == 'All Sites':
        fig = px.pie(values=spacex_df.groupby('Launch Site')['class'].mean(),
                     names=spacex_df.groupby('Launch Site')['Launch Site'].first(),
                     title='Total Success Launches by Site')
    else:
        fig = px.pie(values=spacex_df[spacex_df['Launch Site']==str(launch_site)]['class'].value_counts(normalize=True),
                     names=spacex_df['class'].unique(),
                     title='Total Success Launches for Site {}'.format(launch_site))
    return(fig)

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, selected_payload_range):
    if selected_site == 'All Sites':
        filtered_data = spacex_df[
            (spacex_df['Payload Mass (kg)'] >= selected_payload_range[0]) &
            (spacex_df['Payload Mass (kg)'] <= selected_payload_range[1])
        ]
        fig = px.scatter(filtered_data, x='Payload Mass (kg)', y='class', color=spacex_df['Booster Version'].str.split().str[1],
                         labels={'Payload Mass (kg)': 'Payload Mass (kg)', 'class': 'Success'},
                         title='Payload Success vs Payload Mass for All Sites')
    else:
        filtered_data = spacex_df[
            (spacex_df['Launch Site'] == selected_site) &
            (spacex_df['Payload Mass (kg)'] >= selected_payload_range[0]) &
            (spacex_df['Payload Mass (kg)'] <= selected_payload_range[1])
        ]
        fig = px.scatter(filtered_data, x='Payload Mass (kg)', y='class', color=spacex_df['Booster Version'].str.split().str[1],
                         labels={'Payload Mass (kg)': 'Payload Mass (kg)', 'class': 'Success'},
                         title=f'Payload Success vs Payload Mass for {selected_site}')
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(port=1234)