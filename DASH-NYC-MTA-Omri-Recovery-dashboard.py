import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

# Prepare the data
#df = pd.read_csv("/Users/omri_/Github_projects/Dask_competition_MTA/mta_data_ridership1.csv")

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/refs/heads/master/MTA_Ridership_by_DATA_NY_GOV.csv')
df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')  # Ensure 'Date' is in datetime format

df['Total Estimated Ridership'] =     (df['Subways: Total Estimated Ridership']+
                                       df['Buses: Total Estimated Ridership']+
                                       df['LIRR: Total Estimated Ridership']+
                                       df['Metro-North: Total Estimated Ridership']+
                                       df['Staten Island Railway: Total Estimated Ridership'])



# Initialize the Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1('MTA Post-Pandemic Ridership Recovery Dashboard', 
            style={'textAlign': 'center', 'color': '#1E90FF', 'marginBottom': '20px'}),
    
    # Top-level insights section
    html.Div([
        html.H3('Recovery Insights', style={'color': '#4682B4'}),
        html.Div(id='recovery-summary', style={
            'backgroundColor': '#F0F8FF', 
            'padding': '15px', 
            'borderRadius': '10px'
        })
    ], style={'margin': '20px'}),
    
    # Visualization controls
    html.Div([
        # Ridership Type Selector
        html.Div([
            html.Label('Select Metric:'),
            dcc.Dropdown(
                id='metric-selector',
                options=[
                        {'label': 'Subways', 'value': 'Subways'},
                        {'label': 'Buses', 'value': 'Buses'},
                        {'label': 'Long Island Rails', 'value': 'Long Island Rails'},
                        {'label': 'Metro-North', 'value': 'Metro-North'},
                        {'label': 'Staten Island Railway', 'value': 'Staten Island Railway'},
                        {'label': 'Access-A-Rid', 'value': 'Access-A-Rid'},
                        {'label': 'Bridges and Tunnels', 'value': 'Bridges and Tunnels'},
                ],
                value=['Subways','Buses', 'Bridges and Tunnels'],
                style={'width': '100%'}
            )
        ], style={'width': '30%', 'display': 'inline-block', 'margin': '10px'}),
        
        # Transit Mode Selector
        html.Div([
            html.Label('Select Transit Modes:'),
            dcc.Dropdown(
                id='transit-mode-selector',
                options=[
                    {'label': 'Subways', 'value': 'Subways'},
                    {'label': 'Buses', 'value': 'Buses'},
                    {'label': 'LIRR', 'value': 'LIRR'},
                    {'label': 'Metro-North', 'value': 'Metro-North'},
                ],
                value=['Subways', 'Buses', 'LIRR', 'Metro-North'],
                multi=True,
                style={'width': '100%'}
            )
        ], style={'width': '60%', 'display': 'inline-block', 'margin': '10px'}),
    ], style={'textAlign': 'center', 'marginBottom': '20px'}),
    
    # Main Visualization
    dcc.Graph(id='recovery-trend-graph'),
    
    # Comparative Analysis Section
    html.Div([
        html.H3('Comparative Analysis', style={'color': '#4682B4'}),
        dash_table.DataTable(
            id='comparative-table',
            columns=[{'name': col, 'id': col} for col in ['Transit Mode', 'Peak Ridership', 'Recovery Percentage']],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left'},
            style_header={
                'backgroundColor': 'lightblue',
                'fontWeight': 'bold'
            }
        )
    ], style={'margin': '20px'})
])

# Callbacks for dynamic updates
@app.callback(
    [Output('recovery-trend-graph', 'figure'),
     Output('recovery-summary', 'children'),
     Output('comparative-table', 'data')],
    [Input('metric-selector', 'value'),
     Input('transit-mode-selector', 'value')]
)
def update_dashboard(metric, selected_modes):
    # Prepare traces for selected modes
    traces = []
    summary_insights = []
    comparative_data = []
    
    for mode in selected_modes:
        y_column = f'{mode}_{metric}'
        color_map = {
            'Subways': '#FF6347',
            'Buses': '#4682B4',
            'LIRR': '#2E8B57',
            'Metro-North': '#DAA520',
        }
        
        traces.append(go.Scatter(
            x=df['Date'], 
            y=df[y_column], 
            mode='lines+markers',
            name=mode,
            line=dict(color=color_map.get(mode, '#000000'))
        ))
        
        # Prepare comparative data
        max_value = df[y_column].max()
        last_value = df[y_column].iloc[-1]
        recovery_percentage = (last_value / max_value * 100) if max_value > 0 else 0
        
        comparative_data.append({
            'Transit Mode': mode.replace('_', ' '),
            'Peak Ridership': f'{max_value:,.0f}',
            'Recovery Percentage': f'{recovery_percentage:.2f}%'
        })
    
    # Create figure
    fig = go.Figure(data=traces)
    fig.update_layout(
        title=f'MTA {metric} Recovery Trends',
        xaxis_title='Date',
        yaxis_title=metric,
        legend_title='Transit Modes'
    )
    
    # Summary insights
    summary_insights = html.Div([
        html.P(f"Analysis of {len(selected_modes)} transit modes"),
        html.P(f"Metric: {metric}")
    ])
    
    return fig, summary_insights, comparative_data

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)




