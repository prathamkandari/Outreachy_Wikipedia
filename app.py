from flask import Flask, render_template, request, url_for
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

app = Flask(__name__)

# Load data
# Load data
df_revisions = pd.read_csv('https://public-paws.wmcloud.org/User:Pablo%20(WMF)/outreachy/round28/features_scores_climatechange_2022.csv.zip', parse_dates=['revision_timestamp'])


# Define a function for filtering and aggregation
def filter_and_aggregate(data, feature, start_date, end_date):
    # Filter the data based on the specified date range
    filtered_data = data[(data['revision_timestamp'] >= start_date) & (data['revision_timestamp'] <= end_date)]
    
    # Group by month and calculate the mean value of the feature
    aggregated_data = filtered_data.groupby(filtered_data['revision_timestamp'].dt.to_period('M'))[feature].mean()
    
    return aggregated_data

# Define a function to generate line chart
def generate_line_chart(data, feature, page_id):
    # Filter data for the specified page ID
    filtered_data = data[data['page_id'] == int(page_id)]

    # Convert 'revision_timestamp' to datetime
    filtered_data['revision_timestamp'] = pd.to_datetime(filtered_data['revision_timestamp'])

    # Define the date range for filtering
    start_date = filtered_data['revision_timestamp'].min()
    end_date = filtered_data['revision_timestamp'].max()

    # Filter and aggregate data
    aggregated_data = filter_and_aggregate(filtered_data, feature, start_date, end_date)

    # Plot the data
    plt.figure(figsize=(10, 6))
    plt.plot(aggregated_data.index.to_timestamp(), aggregated_data.values, marker='o')
    plt.xlabel('Date')
    plt.ylabel(feature.capitalize())
    plt.title(f'{feature.capitalize()} Over Time for Page ID {page_id}')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot to the static directory
    plot_filename = f'temp_plot_line.png'
    plt.savefig(os.path.join('static', plot_filename))

    return plot_filename

# Define a function to generate bar chart
def generate_bar_chart(data, feature, page_id):
    # Filter data for the specified page ID
    filtered_data = data[data['page_id'] == int(page_id)]

    # Group by month and calculate the sum value of the feature
    aggregated_data = filtered_data.groupby(filtered_data['revision_timestamp'].dt.to_period('M'))[feature].sum()

    # Plot the data
    plt.figure(figsize=(10, 6))
    aggregated_data.plot(kind='bar')
    plt.xlabel('Date')
    plt.ylabel(feature.capitalize())
    plt.title(f'{feature.capitalize()} Over Time for Page ID {page_id}')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot to the static directory
    plot_filename = f'temp_plot_bar.png'
    plt.savefig(os.path.join('static', plot_filename))

    return plot_filename

# Define a function to generate heatmap
# Define a function to generate heatmap
# def generate_heatmap(data, feature):
#     # Pivot the data for heatmap
#     pivot_data = data.pivot_table(index='page_id', columns='revision_timestamp', values=feature, aggfunc='mean')

#     # Plot the heatmap
#     plt.figure(figsize=(10, 6))
#     sns.heatmap(pivot_data, cmap='viridis')
#     plt.xlabel('Date')
#     plt.ylabel('Page ID')
#     plt.title(f'Heatmap of {feature.capitalize()}')
#     plt.tight_layout()

#     # Save the plot to the static directory
#     plot_filename = f'temp_plot_heatmap.png'
#     plt.savefig(os.path.join('static', plot_filename))

#     return plot_filename


# Define a function to generate pie chart
def generate_pie_chart(data, feature):
    # Calculate total count for each category
    category_counts = data[feature].value_counts()

    # Plot the pie chart
    plt.figure(figsize=(8, 8))
    plt.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title(f'Pie Chart of {feature.capitalize()}')
    plt.tight_layout()

    # Save the plot to the static directory
    plot_filename = f'temp_plot_pie.png'
    plt.savefig(os.path.join('static', plot_filename))

    return plot_filename

# Define a function to generate histogram
def generate_histogram(data, feature):
    # Plot the histogram
    plt.figure(figsize=(10, 6))
    plt.hist(data[feature].dropna(), bins=20, color='skyblue', edgecolor='black')
    plt.xlabel(feature.capitalize())
    plt.ylabel('Frequency')
    plt.title(f'Histogram of {feature.capitalize()}')
    plt.tight_layout()

    # Save the plot to the static directory
    plot_filename = f'temp_plot_histogram.png'
    plt.savefig(os.path.join('static', plot_filename))

    return plot_filename

# Define a function to generate boxplot
def generate_boxplot(data, feature):
    # Plot the boxplot
    plt.figure(figsize=(10, 6))
    sns.boxplot(x=data[feature])
    plt.xlabel(feature.capitalize())
    plt.title(f'Boxplot of {feature.capitalize()}')
    plt.tight_layout()

    # Save the plot to the static directory
    plot_filename = f'temp_plot_boxplot.png'
    plt.savefig(os.path.join('static', plot_filename))

    return plot_filename

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get user inputs from the form
        page_id = request.form['page_id']
        feature = request.form['feature']

        # Generate all types of charts
        plot_filenames = []
        for chart_function in [generate_line_chart, generate_bar_chart, generate_pie_chart, generate_histogram, generate_boxplot]:
            plot_filename = chart_function(df_revisions, feature, page_id) if chart_function in [generate_line_chart, generate_bar_chart] else chart_function(df_revisions, feature)
            plot_filenames.append(url_for('static', filename=plot_filename))

        # Generate heatmap separately
        # heatmap_plot_filename = generate_heatmap(df_revisions, feature)
        # plot_filenames.append(url_for('static', filename=heatmap_plot_filename))

        # Render the template with the plot filenames
        return render_template('index.html', plot_filenames=plot_filenames)
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)