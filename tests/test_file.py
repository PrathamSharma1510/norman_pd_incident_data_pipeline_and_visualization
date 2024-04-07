import unittest
from unittest.mock import patch
from assignment2 import (
    calculate_emsstat,
    extract_nature_column,
    calculate_day_of_week,
    calculate_incident_rank,
    fetch_weather_code_for_df,
    ensure_geocoding,
    calculate_time_of_day,
    calculate_location_rank,
    side_of_town
)
import pandas as pd

class TestDataAugmentation(unittest.TestCase):
    def setUp(self):
        #a demo values for testing perpos
        self.df = pd.DataFrame({
            'Date/Time': ['3/1/2024 00:05', '3/2/2024 01:30', '3/3/2024 15:00'],
            'Time of Day':[0,1,2],
            'Location': ['Location A', 'Location B', 'Location A'],
            'Latitude':[35.199763,35.181569,35.21418],
            'Longitude':[-97.444247,-97.49281,-97.272377],
            'Nature': ['Theft', 'Assault', 'Theft'],
            'Incident ORI': ['ori123', 'EMSSTAT', 'ORi3242']
        })
    def test_calculate_day_of_week(self):
        #example taken for check the function is performing as expected or not.
        expected = pd.Series([6, 7, 1], name='Day of Week') 
        result = calculate_day_of_week(self.df)
        pd.testing.assert_series_equal(result, expected, check_names=False)
    
    
    def test_fetch_weather_code_for_df(self):
        test_df = pd.DataFrame({
            'Date/Time': ['4/1/2024 12:00', '4/2/2024 13:00'],#date/time 
            'Latitude': [35.199763, 35.181569],
            'Longitude': [-97.444247, -97.492810],
            'Time of Day': [12, 13] 
        })
        fetch_weather_code_for_df(test_df) 
        #my expected WMO code
        expected_wmo_codes = [3, 3]  
        actual_wmo_codes = test_df['WMO Code'].tolist()
        #values should be same.
        self.assertEqual(expected_wmo_codes, actual_wmo_codes, "The 'WMO Code' values do not match the expected output.")

    def test_calculate_incident_rank(self):
        #taken another demo datset for this test
        test_df = pd.DataFrame({
            'Nature': ['Theft', 'Assault', 'Theft', 'Robbery', 'Assault', 'Theft']
        })
        # theft is more time so it should have rank 1 and so on 
        expected_ranks = pd.Series([1, 2, 1, 3, 2, 1], name='Incident Rank')
        actual_ranks = calculate_incident_rank(test_df) #calling function
        pd.testing.assert_series_equal(actual_ranks, expected_ranks) # cross check for verification 
    
    def test_calculate_time_of_day(self):
        calculate_time_of_day(self.df)
        # Construct the expected Series for comparison
        expected = pd.Series([0, 1, 15], name='Time of Day', index=self.df.index)
        # Retrieve the actual 'Time of Day' column from the modified DataFrame
        actual = self.df['Time of Day']
        pd.testing.assert_series_equal(actual, expected, check_names=False)

    def test_calculate_location_rank(self):
        # Here we assume 'Location A' occurs more frequently than 'Location B', so it gets a higher rank
        expected_ranks = pd.Series([1, 2, 1], name='Location Rank')
        self.df = calculate_location_rank(self.df) 
        pd.testing.assert_series_equal(self.df['Location Rank'], expected_ranks)

    def test_extract_nature_column(self):
        expected_nature = pd.Series(['Theft', 'Assault', 'Theft'], name='Nature')
        extracted_nature = extract_nature_column(self.df)
        pd.testing.assert_series_equal(extracted_nature, expected_nature)

    def test_calculate_emsstat(self): #checking for the emsstat calculation over her 
        self.df['EMSSTAT'] = calculate_emsstat(self.df)  
        expected_emsstat = pd.Series([False, True, False], name='EMSSTAT')
        pd.testing.assert_series_equal(self.df['EMSSTAT'], expected_emsstat) #confirming the answer

    def test_calculate_location_rank(self):
        self.df['Location Rank'] = calculate_location_rank(self.df)  
        expected_ranks = pd.Series([1, 2, 1], name='Location Rank')
        pd.testing.assert_series_equal(self.df['Location Rank'], expected_ranks)
        
    def test_side_of_town(self):
        #taking the location from one of the urls 
        test_df = pd.DataFrame({
            'Location': ['2741 CLASSEN BLVD', '1150 ALAMEDA ST']
        })
        #api key for testing purposes
        test_df = ensure_geocoding(test_df, "AIzaSyCh28Jy9e30ULUW0crS3-9NtT6khonR0sI")
        test_df = side_of_town(test_df)  
        expected_sides = ['SE', 'E'] # expected answer which should be 
        self.assertListEqual(test_df['Side of Town'].tolist(), expected_sides) # check of the result.

if __name__ == '__main__':
    unittest.main()
