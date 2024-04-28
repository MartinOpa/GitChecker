import json
import datetime
from datetime import datetime as dt
import pytz
import pandas as pd
from bokeh.models import ColumnDataSource, HoverTool, TapTool, OpenURL
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.models import Range1d
from .models import Test

# Test query parameters
class TestQueryData: 
    __slots__ = ['param_options', 'param_name', 'date_from', 'date_to']

    def __init__(self, param_options=None, param_name=None, date_from=None, date_to=None):
        self.param_options = param_options
        self.param_name = param_name
        self.date_from = date_from
        self.date_to = date_to

# Datetime to str convert for chart filtering
def get_date(request, id):
    date_str = request.GET.get(id, '')
    if date_str != '':
        return dt.strptime(date_str, '%Y-%m-%d')
    else:
        return None

# Get filtered test query set
def get_filtered_tests(repo_id, query_data):
    tests = Test.objects.filter(commit__repository__id=repo_id)

    if query_data.param_name != 'Any':
        tests = tests.filter(params__param_name=query_data.param_name)
    
    if query_data.date_from is not None:
        tests = tests.filter(timestamp__gt=pytz.timezone("CET").localize(query_data.date_from))

    if query_data.date_to is not None:
        tests = tests.filter(timestamp__lt=pytz.timezone("CET").localize(query_data.date_to + datetime.timedelta(days=1)))

    return tests

# Load data
def prepare_datasets(test_set):
    chart_figs = {}
    for test in test_set:
        summary_json = json.loads(test.summary)
        try:
            for key, value in summary_json.items():
                try:
                    if key not in chart_figs:
                        chart_figs.setdefault(key, [])
                        
                    chart_figs[key].append({
                        'commit': test.commit.id,
                        'url': test.commit.commit_url,
                        'commit_message': test.commit.commit_message,
                        'timestamp': test.timestamp,
                        key: value
                    })

                except Exception as e:
                    print(e)
                    continue
        except:
            # summary is a json list and likely a test with an error output
            continue

    return chart_figs

def get_charts(test_set, metrics_selected, theme):
    curdoc().clear()
    chart_figs = prepare_datasets(test_set)

    figs = []
    options = []

    for current_key in chart_figs:
        options.append(current_key)

        # Filter by selected metrics, if none are selected display all
        if current_key in metrics_selected or len(metrics_selected) == 0:
            data = chart_figs[current_key]
            df = pd.DataFrame(data)
            source = ColumnDataSource(df)

            xr1 = Range1d(start=(df['timestamp'].min()) - datetime.timedelta(hours=1), 
                          end=(df['timestamp'].max()) + datetime.timedelta(hours=1))
            yr1 = Range1d(start=(df[current_key].min())*0.99, end=(df[current_key].max())*1.01)

            fig = figure(x_range=xr1, y_range=yr1, sizing_mode='stretch_width', height=300, active_scroll='wheel_zoom',tools='pan,wheel_zoom,box_zoom,reset')
            
            # Apply theme from cookie
            if theme == 'light':
                curdoc().theme = 'light_minimal'
            else:
                curdoc().theme = 'dark_minimal'
            curdoc().add_root(fig)

            # Make line chart
            fig.line(x='timestamp', y=current_key, source=source)
            fig.title.text = current_key
            fig.title.align = 'center'
            if theme == 'light':
                fig.title.text_color = 'black'
            else:
                fig.title.text_color = 'white'
            fig.title.text_font_size = '20px'
            fig.xaxis.axis_label = 'timestamp'
            fig.yaxis.axis_label = current_key

            # Cycle through data and add tooltips, format timestamp
            tooltips = []
            for key, _ in data[0].items():
                if key == 'timestamp':
                    tooltips.append((f'{key}', '@timestamp{%F %T}'))
                else:
                    tooltips.append((f'{key}', '@{' + f'{key}' + '}'))
                
            # For commit URLs
            tap_tool = TapTool()
            tap_tool.callback = OpenURL(url='@url')

            # Display data on hover
            hover = HoverTool()
            hover.tooltips = tooltips
            hover.formatters = {
                '@timestamp': 'datetime'
            }
            hover.mode = 'vline'
            
            fig.add_tools(hover, tap_tool)
            figs.append(fig)
    try:
        return components(figs), options
    except:
        return None, None
    
