import os

import pandas as pd
import pycountry
import matplotlib.pyplot as plt
import plotly.express as px

from datetime import datetime, timedelta
from databases import MongoDBHandler
from typing import Optional

from logger import Logger

logger = Logger().get_logger()

class DataVisualizationHandler:
    """
    Class to visualize data based on certain criterias.
    """
    def __init__(self):
        """
        Initializing the DataVisualizationHandler class with mongo db handler and dataframe.
        """
        self.mongo_handler = MongoDBHandler()
        self._dataframe = None
    
    def __call__(self):
        """
        The __call__ method allows an instance of the class to be used as if it were a function.
        Ensures the creation of a directory and generates a diagram.
        This method makes the instance callable. When called, it performs the following operations:
        1. Ensures that a directory named "visualized_diagram" exists. If the directory does not exist, it creates it.
        2. Calls the `generate_diagram` method to create and save a visualization diagram in the "visualized_diagram" directory.
        """
        os.makedirs("visualized_diagram", exist_ok=True)
        self.generate_diagram()

    @property
    def dataframe(self) -> pd.DataFrame:
        """
        Check if dataframe exists or not. If not, then generate the dataframe via fetching the data from mongodb
        and use pandas libraries to generate the dataframe type data.
        """
        if self._dataframe is None:
            data = self.mongo_handler.get_all_data()
            self._dataframe = pd.DataFrame(data)
        return self._dataframe
    
    def plot_bar(self, x_data: pd.Index, y_data: pd.Series, x_label: str, y_label: str, title: str, x_ticks: Optional[pd.Series] = None):
        """
        Common function to generate the bar plot diagram and save to the provided directory
        with the title as file name in jpeg format.
        """
        plt.figure(figsize=(8, 6))
        plt.bar(x_data, y_data)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)
        if x_ticks is not None and isinstance(x_ticks, pd.Series):
            plt.xticks(x_ticks.index)
        plt.savefig(f'visualized_diagram/{title}.jpeg')
        logger.info(f'Completed saving the bar plot diagram with file name {title}.jpeg')
    
    def visualization_by_operating_system(self):
        """
        Generate the bar plot visualizing the counts of different host by OS.
        """
        logger.info("Starting to generate the bar plot diagram by operating systems")
        os_counts = self.dataframe['os'].value_counts()
        self.plot_bar(os_counts.index, os_counts.values, "Operating System", "Count", "Distribution of Operating Systems")
    
    def visualization_by_old_host_vs_new_host(self):
        """
        Generate the bar plot visualizing the counts of old host vs new hosts.
        """
        logger.info("Starting to generate the bar plot diagram of old host vs new hosts")
        cutoff_date = datetime.now() - timedelta(days=30)
        self.dataframe['host_age'] = self.dataframe['last_seen'].apply(lambda x: 'Old' if x < cutoff_date else 'New')
        host_age_counts = self.dataframe['host_age'].value_counts()
        self.plot_bar(host_age_counts.index, host_age_counts.values, "Host Age", "Count", "Distribution of Old vs New Hosts")
    
    def visualization_by_agent_version(self):
        """
        Generate the bar plot visualizing the counts by agent version.
        """
        logger.info("Starting to generate the bar plot diagram by agent version")
        self.dataframe['agent_version_major'] = self.dataframe['agent_version'].str.split('.', expand=True)[0]
        agent_version_counts = self.dataframe['agent_version_major'].value_counts()
        self.plot_bar(agent_version_counts.index, agent_version_counts.values, "Agent Version (Major)", "Count", "Distribution of Agent Versions")
    
    def visualization_by_host_year_created(self):
        """
        Generate the bar plot visualizing the counts of different host by year created.
        """
        logger.info("Starting to generate the bar plot diagram by host year created")
        self.dataframe['created_year'] = self.dataframe['created'].dt.year
        created_year_counts = self.dataframe['created_year'].value_counts().sort_index()
        self.plot_bar(created_year_counts.index, created_year_counts.values, "Year Created", "Count", "Distribution of Hosts by Year Created", x_ticks=created_year_counts)
    
    def visualization_by_host_status(self):
        """
        Generates a bar plot visualizing the counts of different host statuses
        """
        logger.info("Starting to generate the bar plot diagram by host status")
        status_counts = self.dataframe['status'].value_counts()
        self.plot_bar(status_counts.index, status_counts.values, "Status", "Count", "Status Counts")
    
    def visualization_by_countries_for_host(self):
        """
        Generate the choropleth map visualizing the counts of different host by countries.
        """
        countries = {}
        for country in pycountry.countries:
            countries[country.name] = country.alpha_2
        
        # Extract country names from the 'location' column
        self.dataframe['country'] = self.dataframe['location'].str.split(',').str[-1]
        self.dataframe['country'] = self.dataframe['country'].apply(lambda x: countries.get(x, x))

        # Group by country and count occurrences
        country_counts = self.dataframe['country'].value_counts().reset_index()
        country_counts.columns = ['country', 'count']

        # Create the choropleth map
        logger.info("Starting to generate the choropleth map of different host by countries")
        fig = px.choropleth(
            country_counts,
            locations='country',
            locationmode='country names',
            color='count',
            color_continuous_scale=px.colors.sequential.Plasma,
            title='Host Distribution by Country'
        )
        fig.show()
        fig.write_image("visualized_diagram/Host Distribution by Country.jpeg")
    
    def generate_diagram(self):
        """
        Generate the diagram based on certain criteria's
        """
        logger.info("Starting to generate the diagram")
        self.visualization_by_operating_system()
        self.visualization_by_old_host_vs_new_host()
        self.visualization_by_agent_version()
        self.visualization_by_host_year_created()
        self.visualization_by_host_status()
        self.visualization_by_countries_for_host()
        logger.info("Completed generating the diagram")

