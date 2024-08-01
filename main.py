import asyncio
from data_fetcher import data_fetcher
from data_normalizer  import DataNormalizer
from data_visualizer import DataVisualizationHandler
from databases  import mongo_db
from logger import Logger
import time
import schedule

logger = Logger().get_logger()

async def extract_data():
    """
    Call the API used for Qualys and CrowdStrike data.
    """
    qualys_data, crowdstrike_data = await data_fetcher.fetch_all_data()
    return qualys_data, crowdstrike_data

def transform_data(qualys_data, crowdstrike_data):
    """
    Normalize the data obtained from qualys and crowdstrike to same format
    and remove duplicates if exists.
    """
    data_normalizer = DataNormalizer()
    normalized_data = []

    if qualys_data:
        logger.info("Normalizing Qualys Data")
        normalized_data.extend(data_normalizer.normalize_qualys_data(qualys_data))
    
    if crowdstrike_data:
        logger.info("Normalizing CrowdStrike Data")
        normalized_data.extend(data_normalizer.normalize_crowdstrike_data(crowdstrike_data))

    unique_data = data_normalizer.remove_duplicates(normalized_data)
    return unique_data

def load_data_to_database(normalized_data):
    """
    Inserting the normalized_data into the mongo db databases.
    """
    logger.info("Starting to insert the normalized data into the mongodb")
    mongo_db.insert_data_operations(normalized_data)

def visualize_data():
    """
    Visualize the data by calling instance of DataVisualizationHandler class
    """
    logger.info("Starting to visualize the data and save the generated diagram to the designated folders.")
    visualizer = DataVisualizationHandler()
    visualizer()

def main():
    """
    Following steps are performed  in this function
        1. Call the API to fetch the data
        2. If data exists, transform the data to the same format and remove the duplicate if exists.
        3. Insert the transformed data to database
        4. Load the data inserted to database and generate the diagram.
    """
    logger.info("Starting to call the main function at time")
    start_time = time.time()
    logger.info("Starting to fetch data for both Qualys and CrowdStrike API")
    qualys_data, crowdstrike_data = asyncio.run(extract_data())
    if not (qualys_data and crowdstrike_data):
        logger.info("Both Qualys Data and CrowdStrike Data are empty. Skipping data processing and visualization.")
        return
    logger.info("Starting to transfor data for Qualys Data and CrowdStrike Data")
    processed_data = transform_data(qualys_data, crowdstrike_data)
    logger.info("Starting to load processed data into mongo db databases")
    load_data_to_database(processed_data)
    logger.info("Starting to generate the diagram and save to the folder")
    visualize_data()
    end_time = time.time()
    time_taken = end_time - start_time
    logger.info(f"Completed all the operations and took time of {time_taken:.2f} seconds")

if __name__ == "__main__":
    """
    Here, we specify the job to run at a specific time every day.
    For now it is scheduled to run at every 30 seconds.
    The while True loop ensures the script keeps running, allowing schedule
    to execute the job at the specified time. schedule.run_pending() checks
    if any scheduled tasks are pending and runs them
    """
    # Schedule the job to run at a specific time every day
    schedule.every(30).seconds.do(main)
    """
    For more schedule options visit https://schedule.readthedocs.io/en/stable/examples.html#run-a-job-every-x-minute
    """
    while True:
        schedule.run_pending()
        time.sleep(1)