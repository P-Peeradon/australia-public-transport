import geopandas as gpd
import os
import sys
import string
import re

_REGIONAL_CRS = {
        "Australia": "EPSG:7844",  # GDA2020 (Australia)
        "New Zealand": "EPSG:4167",  # NZGD2000 (New Zealand)
        "Papua New Guinea": "EPSG:5110", # PNG94 (Papua New Guinea)
        "Web": "EPSG:4326" # WGS84 (Global/Web)
    }

_NAME_MAPPINGS = {
        "Australia": {"LGA_NAME24": "region_name", "STE_NAME21": "state"},
        "New Zealand": {"TA2024_NAM": "region_name", "REGC2024_N": "state"},
        "Papua New Guinea": {"ADM1_EN": "state", "ADM2_EN": "region_name"}
    }

class OceaniaGeoReader:
    """
    A unified utility to read, clean, and nourish spatial data (LGA/SAL)
    for Australia, New Zealand, and Papua New Guinea.
    """
    global _REGIONAL_CRS
    global _NAME_MAPPINGS
    
    def __init__(self, data_folder):
        self.data_folder = data_folder
        
    #Filename input only w/o .shp
    def read_and_standardize(self, file_name, country):
        """
            Instance method to load a shapefile and force it to its 
            correct regional CRS, then unify to WGS84.
        """
        if '.' in file_name:
            print('ValueError: File name cannot contain period (.)', file=sys.stderr)
            raise ValueError('Error: File name cannot contain period (.)')
        
        
        if self.validate_shp(file_name)[0]:
            missing = ', '.join(self.validate_shp(file_name)[1])
            print(f"FileNotFoundError: Missing {missing}", file=sys.stderr)
            raise FileNotFoundError(f"FileNotFoundError: Missing {missing}")
        
        file_path = os.path.join(self.data_folder, f'{file_name}.shp')
        
        try:
            gdf = gpd.read_file(file_path)
            target_crs = _REGIONAL_CRS.get(string.capwords(country), "EPSG:4326")
            
            if gdf.crs is None:
                gdf.set_crs(target_crs, inplace=True)
                
            gdf = gdf.to_crs(_REGIONAL_CRS["GLOBAL"])
            
            # Standardize Names
            mapping = _NAME_MAPPINGS.get(country, {})
            gdf = gdf.rename(columns=mapping)
            
            return gdf
        except Exception as e:
            print(f"{e}: Failed to process {file_name}", file=sys.stderr)
            raise Exception(f"{e}: Failed to process {file_name}")
        
    def add_calculation(self, gdf: gpd.GeoDataFrame):
        """
            Nourishes data with Centroids (points) and Area (km2).
            Calculations are done in meters, then returned to degrees.
        """
        # Projected CRS (Meters) for accurate math
        gdf_m = gdf.to_crs(epsg=3857) 
        gdf['area_km2'] = gdf_m.area / 10**6
        gdf['centroid'] = gdf_m.centroid.to_crs(_REGIONAL_CRS["WGS84"])
        return gdf
    
    def auto_standardize(self, gdf: gpd.GeoDataFrame):
        """
            Automatically finds and renames columns based on patterns.
        """
        new_columns = {}
        for col in gdf.columns:
            # Pattern for Region Name (LGA Name, Suburb Name, etc.)
            if re.search(r'(LGA|SAL|TA|ADM2).*NAME', col, re.IGNORECASE):
                new_columns[col] = "region_name"
            # Pattern for State/Province
            elif re.search(r'(STE|REGC|ADM1).*NAME', col, re.IGNORECASE):
                new_columns[col] = "state_name"
        
        return gdf.rename(columns=new_columns)
    
    def filter_greater_capital(self, gdf: gpd.GeoDataFrame, capital_names):
        """Filters the dataset to only include specific major capital regions."""
        return gdf[gdf['region_name'].str.contains('|'.join(capital_names), case=False)]
        
    @staticmethod
    def validate_shp(file_name):
        """
            Static method to ensure the .shp has its required siblings.
            A .shp cannot function without .shx and .dbf.
        """
        base = os.path.splitext(file_name)
        required = [".shp", ".shx", ".dbf"]
        missing = [ext for ext in required if not os.path.exists(base + ext)]
        return len(missing) == 0, missing
    
    