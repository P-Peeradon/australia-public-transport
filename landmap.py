# Reading the Sydney, Melbourne and Adelaide data file.
import os
import pandas as pd
import geopandas as gpd
from shapely import wkt

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

#print(gdf2.columns)
#print(gdf2.loc[:, ['SAL_CODE21', 'SAL_NAME21', 'geometry']])
syd_suburb = gpd.sjoin(gdf2, syd_boundary, predicate='within').loc[:, ['SAL_CODE21', 'SAL_NAME21', 'geometry']]
mel_suburb = gpd.sjoin(gdf2, mel_boundary, predicate='within').loc[:, ['SAL_CODE21', 'SAL_NAME21', 'geometry']]
bne_suburb = gpd.sjoin(gdf2, bne_boundary, predicate='within').loc[:, ['SAL_CODE21', 'SAL_NAME21', 'geometry']]
adl_suburb = gpd.sjoin(gdf2, adl_boundary, predicate='within').loc[:, ['SAL_CODE21', 'SAL_NAME21', 'geometry']]

#########################################

#local government
path_to_lga = os.path.join(base_dir, 'geom', 'LGA_2025_AUST_GDA2020.shp')
gdf3 = gpd.read_file(path_to_lga)
#print(gdf3)

#print(gdf3.columns)
#print(gdf3.loc[:, ['SAL_CODE21', 'SAL_NAME21', 'geometry']])
syd_council = gpd.sjoin(gdf3, syd_boundary, predicate='within').loc[:, ['LGA_CODE25', 'LGA_NAME25', 'geometry']]
mel_council = gpd.sjoin(gdf3, mel_boundary, predicate='within').loc[:, ['LGA_CODE25', 'LGA_NAME25', 'geometry']]
bne_council = gpd.sjoin(gdf3, bne_boundary, predicate='within').loc[:, ['LGA_CODE25', 'LGA_NAME25', 'geometry']]
adl_council = gpd.sjoin(gdf3, adl_boundary, predicate='within').loc[:, ['LGA_CODE25', 'LGA_NAME25', 'geometry']]

"""
print(syd_suburb)
print(mel_suburb)
print(bne_suburb)
print(adl_suburb)
"""

##########################################

land_csv_path = os.path.join(base_dir, 'area-destination')

#write suburb data into .csv files
syd_suburb['wkt_geom'] = syd_suburb.geometry.apply(lambda x: x.wkt)
pd.DataFrame(syd_suburb.drop(columns='geometry')).to_csv(os.path.join(land_csv_path, 'syd_suburb.csv'), index=False)

mel_suburb['wkt_geom'] = mel_suburb.geometry.apply(lambda x: x.wkt)
pd.DataFrame(mel_suburb.drop(columns='geometry')).to_csv(os.path.join(land_csv_path, 'mel_suburb.csv'), index=False)

bne_suburb['wkt_geom'] = bne_suburb.geometry.apply(lambda x: x.wkt)
pd.DataFrame(bne_suburb.drop(columns='geometry')).to_csv(os.path.join(land_csv_path, 'bne_suburb.csv'), index=False)

adl_suburb['wkt_geom'] = adl_suburb.geometry.apply(lambda x: x.wkt)
pd.DataFrame(adl_suburb.drop(columns='geometry')).to_csv(os.path.join(land_csv_path, 'adl_suburb.csv'), index=False)
