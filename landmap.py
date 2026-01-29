# Reading the Sydney, Melbourne and Adelaide data file.
import os
import pandas as pd
import geopandas as gpd
from shapely import wkt
import re

base_dir = os.getcwd()

# Greater capital area.
path_to_geo = os.path.join(base_dir, 'geom','GCCSA_2021_AUST_GDA2020.shp')
gdf = gpd.read_file(path_to_geo)

#print(gdf.columns)
#print(gdf.loc[:, ['GCC_CODE21', 'GCC_NAME21', 'geometry']])

target_area = ['1GSYD', '2GMEL', '3GBRI', '4GADE']
#print(gdf[gdf['GCC_CODE21'].isin(target_area)].loc[:, ['GCC_CODE21', 'GCC_NAME21', 'geometry']])

greater_capital_gdf = gdf[gdf['GCC_CODE21'].isin(target_area)].loc[:, ['GCC_CODE21', 'GCC_NAME21', 'geometry']]
#print(greater_capital_gdf, '\n', greater_capital_gdf.crs)
syd_boundary = gdf[gdf['GCC_CODE21'] == '1GSYD']
mel_boundary = gdf[gdf['GCC_CODE21'] == '2GMEL']
bne_boundary = gdf[gdf['GCC_CODE21'] == '3GBRI']
adl_boundary = gdf[gdf['GCC_CODE21'] == '4GADE']

#####################################################################

#suburb and localities
path_to_sal = os.path.join(base_dir, 'geom', 'SAL_2021_AUST_GDA2020.shp')
gdf2 = gpd.read_file(path_to_sal)
#print(gdf2)
gdf2['centroid'] = gdf2.geometry.representative_point()
gdf2_centroid = gdf2.set_geometry('centroid')

#print(gdf2.columns)
#print(gdf2_centroid.loc[:, ['SAL_CODE21', 'SAL_NAME21', 'STE_NAME21']])
syd_suburb = gpd.sjoin(gdf2_centroid, syd_boundary, predicate='intersects').loc[:, ['SAL_CODE21', 'SAL_NAME21', 'STE_NAME21_left', 'geometry']].set_geometry('geometry')
mel_suburb = gpd.sjoin(gdf2_centroid, mel_boundary, predicate='intersects').loc[:, ['SAL_CODE21', 'SAL_NAME21', 'STE_NAME21_left', 'geometry']].set_geometry('geometry')
bne_suburb = gpd.sjoin(gdf2_centroid, bne_boundary, predicate='intersects').loc[:, ['SAL_CODE21', 'SAL_NAME21', 'STE_NAME21_left', 'geometry']].set_geometry('geometry')
adl_suburb = gpd.sjoin(gdf2_centroid, adl_boundary, predicate='intersects').loc[:, ['SAL_CODE21', 'SAL_NAME21', 'STE_NAME21_left', 'geometry']].set_geometry('geometry')

#########################################

#local government
path_to_lga = os.path.join(base_dir, 'geom', 'LGA_2025_AUST_GDA2020.shp')
gdf3 = gpd.read_file(path_to_lga)
#print(gdf3)
gdf3['centroid'] = gdf3.geometry.representative_point()
gdf3_centroid = gdf3.set_geometry('centroid')

#print(gdf3.columns)
#print(gdf3.loc[:, ['LGA_CODE25', 'LGA_NAME25', 'geometry']])
syd_council = gpd.sjoin(gdf3_centroid, syd_boundary, predicate='intersects').loc[:, ['LGA_CODE25', 'LGA_NAME25', 'STE_NAME21_left', 'geometry']].set_geometry('geometry')
mel_council = gpd.sjoin(gdf3_centroid, mel_boundary, predicate='intersects').loc[:, ['LGA_CODE25', 'LGA_NAME25', 'STE_NAME21_left', 'geometry']].set_geometry('geometry')
bne_council = gpd.sjoin(gdf3_centroid, bne_boundary, predicate='intersects').loc[:, ['LGA_CODE25', 'LGA_NAME25', 'STE_NAME21_left', 'geometry']].set_geometry('geometry')
adl_council = gpd.sjoin(gdf3_centroid, adl_boundary, predicate='intersects').loc[:, ['LGA_CODE25', 'LGA_NAME25', 'STE_NAME21_left', 'geometry']].set_geometry('geometry')

##########################################

land_csv_path = os.path.join(base_dir, 'area-destination')

#write suburb data into .csv files
syd_suburb['wkt_geom'] = syd_suburb.geometry.apply(lambda x: x.wkt)
syd_suburb['centroid'] = syd_suburb.geometry.representative_point()
pd.DataFrame(syd_suburb.drop(columns='geometry')).rename({'SAL_CODE21': 'SAL_CODE', 'SAL_NAME21': 'SAL_NAME', 'STE_NAME21_left': 'STE_NAME'}).to_csv(os.path.join(land_csv_path, 'syd_suburb.csv'), index=False)

mel_suburb['wkt_geom'] = mel_suburb.geometry.apply(lambda x: x.wkt)
mel_suburb['centroid'] = mel_suburb.geometry.representative_point()
pd.DataFrame(mel_suburb.drop(columns='geometry')).rename({'SAL_CODE21': 'SAL_CODE', 'SAL_NAME21': 'SAL_NAME', 'STE_NAME21_left': 'STE_NAME'}).to_csv(os.path.join(land_csv_path, 'mel_suburb.csv'), index=False)

bne_suburb['wkt_geom'] = bne_suburb.geometry.apply(lambda x: x.wkt)
bne_suburb['centroid'] = bne_suburb.geometry.representative_point()
pd.DataFrame(bne_suburb.drop(columns='geometry')).rename({'SAL_CODE21': 'SAL_CODE', 'SAL_NAME21': 'SAL_NAME', 'STE_NAME21_left': 'STE_NAME'}).to_csv(os.path.join(land_csv_path, 'bne_suburb.csv'), index=False)

adl_suburb['wkt_geom'] = adl_suburb.geometry.apply(lambda x: x.wkt)
adl_suburb['centroid'] = adl_suburb.geometry.representative_point()
pd.DataFrame(adl_suburb.drop(columns='geometry')).rename({'SAL_CODE21': 'SAL_CODE', 'SAL_NAME21': 'SAL_NAME', 'STE_NAME21_left': 'STE_NAME'}).to_csv(os.path.join(land_csv_path, 'adl_suburb.csv'), index=False)

#write lga data into .csv files
syd_council['wkt_geom'] = syd_council.geometry.apply(lambda x: x.wkt)
syd_council['centroid'] = syd_council.geometry.representative_point()
pd.DataFrame(syd_council.drop(columns='geometry')).rename({'LGA_CODE25': 'LGA_CODE', 'LGA_NAME25': 'LGA_NAME', 'STE_NAME21_left': 'STE_NAME'}).to_csv(os.path.join(land_csv_path, 'syd_council.csv'), index=False)

mel_council['wkt_geom'] = mel_council.geometry.apply(lambda x: x.wkt)
mel_council['centroid'] = mel_council.geometry.representative_point()
pd.DataFrame(mel_council.drop(columns='geometry')).rename({'LGA_CODE25': 'LGA_CODE', 'LGA_NAME25': 'LGA_NAME', 'STE_NAME21_left': 'STE_NAME'}).to_csv(os.path.join(land_csv_path, 'mel_council.csv'), index=False)

bne_council['wkt_geom'] = bne_council.geometry.apply(lambda x: x.wkt)
bne_council['centroid'] = bne_council.geometry.representative_point()
pd.DataFrame(bne_council.drop(columns='geometry')).rename({'LGA_CODE25': 'LGA_CODE', 'LGA_NAME25': 'LGA_NAME', 'STE_NAME21_left': 'STE_NAME'}).to_csv(os.path.join(land_csv_path, 'bne_council.csv'), index=False)

adl_council['wkt_geom'] = adl_council.geometry.apply(lambda x: x.wkt)
adl_council['centroid'] = adl_council.geometry.representative_point()
pd.DataFrame(adl_council.drop(columns='geometry')).rename({'LGA_CODE25': 'LGA_CODE', 'LGA_NAME25': 'LGA_NAME', 'STE_NAME21_left': 'STE_NAME'}).to_csv(os.path.join(land_csv_path, 'adl_council.csv'), index=False)


