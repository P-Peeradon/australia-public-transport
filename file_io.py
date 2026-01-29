import geopandas as gpd
import pandas as pd
import os
from shapely import wkt
from shapely.validation import make_valid

class TextFileIO:
    def __init__(self):
        self.supported_extensions = {'.csv', '.txt', '.tsv'}

    def read_text_file(self, file_path, delimiter=','):
        """
        Reads text files with strict validation of path and extension.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Path '{file_path}' does not exist.")

        # Separate name and extension for validation
        base_name, extension = os.path.splitext(file_path)
        extension = str(extension).lower()

        if extension not in self.supported_extensions:
            raise TypeError(f"Format Error: '{extension}' is not a supported text format.")

        try:
            # Low_memory=False prevents mixed type guessing errors in large datasets
            df = pd.read_csv(file_path, sep=delimiter, low_memory=False)
            
            if df.empty:
                raise ValueError(f"File '{file_path}' contains no data.")
                
            return df
        except Exception as e:
            raise RuntimeError(f"Could not parse '{file_path}'. Reason: {e}")

    def write_text_file(self, df: pd.DataFrame, output_directory, filename, extension):
        """
        Writes data to disk, ensuring directory existence and format safety.
        """
        if not os.path.exists(output_directory):
            raise FileNotFoundError(f"IO Error: Directory '{output_directory}' not found.")

        extension = extension.lower()
        if extension not in self.supported_extensions:
            raise TypeError(f"Format Error: Cannot write to '{extension}' format.")

        full_path = os.path.join(output_directory, f"{filename}{extension}")

        try:
            # index=False is standard for database-ready CSVs
            df.to_csv(full_path, index=False)
            print(f"Success: Text data saved to {full_path}")
            return full_path
        except Exception as e:
            raise RuntimeError(f"Write Failure: Failed to save '{full_path}'. Reason: {e}") 
    

class GeoFileIO: 
    """
    Handles the technical aspects of reading and writing spatial files.
    Responsibility: Disk <-> Memory, Projection (CRS) management.
    """
    
    dir_pattern: str = r"^(North|South|East|West|Inner|Outer)?\s*(.*?)\s*(North|South|East|West|Inner|Outer)?$"
    supported_read_extensions: set[str] = {'.shp', '.geojson', '.gpkg', '.json'}
    supported_write_extensions: set[str] = {'.shp', '.geojson', '.gpkg', '.parquet'}
    
    def __init__(self, target_crs="EPSG:4326"):
        self.target_crs = target_crs
    
    def process_file_path(self, file_path):
        """
        Splits name and extension, and validates format.
        """
        file_name, file_extension = os.path.splitext(os.path.basename(file_path))
        
        if not file_extension:
            raise ValueError(f"The file {file_path} has no extension.")
        
        if str(file_extension).lower() not in self.supported_read_extensions.union(self.supported_write_extensions):
            raise TypeError(f"Extension '{file_extension}' is not a valid geometry format.")
        
        return file_name, str(file_extension).lower()
    
    def get_driver(self, extension):
        """
        Helper to map extension to the correct OGR driver.
        """
        mapping = {
            '.shp': 'ESRI Shapefile',
            '.geojson': 'GeoJSON',
            '.gpkg': 'GPKG'
        }
        return mapping.get(extension)
    
    def fix_invalid_geometries(self, gdf):
        """
        Fixes 'Self-Intersection' errors common in complex river boundaries like Brisbane.
        """
        if not isinstance(gdf, gpd.GeoDataFrame):
            raise TypeError("Expected a GeoDataFrame.")
        
        # apply make_valid to fix topological errors without losing data
        gdf['geometry'] = gdf['geometry'].apply(lambda x: make_valid(x) if not x.is_valid else x)
        return gdf
    
    def add_centroids(self, gdf):
        """
        Calculates the center point of each suburb for map markers or station linking.
        """
        # We use a representative_point() because it's guaranteed to be inside the polygon
        # whereas a mathematical centroid might fall outside for 'C' shaped suburbs.
        if not isinstance(gdf, gpd.GeoDataFrame):
            raise TypeError("Expected a GeoDataFrame.")
        
        gdf['centroid'] = gdf.geometry.representative_point()
        return gdf
    
    def calculate_area_km2(self, gdf):
        """Calculates the area in square kilometers."""
        # Geometry must be projected to a metric system (like GDA2020) to calculate area accurately
        # Then we convert from m2 to km2
        if not isinstance(gdf, gpd.GeoDataFrame):
            raise TypeError("Expected a GeoDataFrame.")
        
        temp_gdf = gdf.to_crs(epsg=7855) # GDA2020 / MGA zone 55 (approx for SE Australia)
        gdf['area_km2'] = temp_gdf.area / 10**6
        return gdf
    
    def read_geometry(self, file_path):
        """
        Extracts extension, validates, and reads the geometry file.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"IO Error: The file path '{file_path}' does not exist.")

        # Separate name and extension
        base_name, extension = os.path.splitext(file_path)
        extension = str(extension).lower()

        if extension not in self.supported_read_extensions:
            raise TypeError(f"Extension '{extension}' is not supported for reading.")

        try:
            gdf = gpd.read_file(file_path)
            
            # Immediate validation of geometry data
            if gdf.empty:
                raise ValueError(f"The file '{file_path}' is empty.")
            
            # Ensure spatial consistency across all four cities
            if gdf.crs is None:
                raise ValueError(f"File '{file_path}' is missing a Coordinate Reference System.")
            
            return gdf.to_crs(self.target_crs)
        
        except Exception as e:
            raise RuntimeError(f"Failed to process '{file_path}'. Reason: {e}")
    
    def write_geometry(self, gdf: gpd.GeoDataFrame, output_directory, filename, extension):
        """
        Writes geometry data to a specified format with separate name/extension logic.
        """
        if not os.path.exists(output_directory):
            raise FileNotFoundError(f"Output directory '{output_directory}' does not exist.")

        extension = extension.lower()
        if extension not in self.supported_write_extensions:
            raise TypeError(f"Extension '{extension}' is not supported for writing.")

        # Construct full path
        full_output_path = os.path.join(output_directory, f"{filename}{extension}")

        try:
            if extension == '.parquet':
                gdf.to_parquet(full_output_path)
            else:
                gdf.to_file(full_output_path, driver=self.get_driver(extension))
            
            print(f"Success: File saved to {full_output_path}")
            return full_output_path
        
        except Exception as e:
            raise RuntimeError(f"Write Failure: Could not save to '{full_output_path}'. Reason: {e}")

class SpatialInterchange:
    def __init__(self):
        pass

    def geo_to_text(self, gdf):
        """
        Converts Geometry objects into WKT text strings for CSV storage.
        """
        if not isinstance(gdf, gpd.GeoDataFrame):
            raise TypeError("Input Error: Expected a GeoDataFrame.")

        # Create a copy to avoid modifying the original
        df_text = pd.DataFrame(gdf.drop(columns='geometry'))
        
        # Convert geometry to WKT (Well-Known Text) string
        # e.g., 'POLYGON ((153.0 -27.4, ...))'
        df_text['geometry_wkt'] = gdf.geometry.apply(lambda x: x.wkt)
        
        return df_text

    def text_to_geo(self, df, wkt_column='geometry_wkt', crs="EPSG:4326"):
        """Converts a DataFrame with WKT text back into a GeoDataFrame."""
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Expected a DataFrame.")
        
        if wkt_column not in df.columns:
            raise KeyError(f"Column '{wkt_column}' not found in the text data.")

        try:
            # Convert the string column back into real geometry objects
            df['geometry'] = df[wkt_column].apply(wkt.loads)
            gdf = gpd.GeoDataFrame(df, geometry='geometry', crs=crs)
            
            # Remove the string version to keep it clean
            return gdf.drop(columns=[wkt_column])
        except Exception as e:
            raise ValueError(f"Failed to parse WKT strings. Reason: {e}")