import pandas as pd
import geopandas as gpd
from pathlib import Path

def load_secciones_of(state:Path) -> gpd.GeoDataFrame:
    """This function loads the GeoDataFrame from the .shp files. This DataFrame does not contain the names of the municipios, only their number and the number
    of the secciones.

    Args:
        state (Path): .shp files downloaded from the INE

    Returns:
        gpd.GeoDataFrame: The GeoDataFrame containing the geometry of the secciones
    """
    secciones = gpd.read_file(state)
    secciones.columns = [col.lower() for col in secciones.columns]
    secciones = secciones.sort_values(by=['municipio', 'seccion'])
    secciones['id_municipio'] = secciones['municipio']
    secciones = secciones.drop(['id', 'entidad', 'distrito_f', 'distrito_l', 'tipo', 'control', 'geometry1_'], axis=1)
    secciones = secciones.loc[:,['id_municipio', 'municipio', 'seccion', 'geometry']]
    # This transform the geometry data into altitude and latitude so it can be opened with Google earth
    return secciones.to_crs('EPSG:4326')

def load_municipio_of(state:Path) -> gpd.GeoDataFrame:
    """This function get the names of the municipios from the .xls files.

    Args:
        state (Path): .xls files downloaded from the INE

    Returns:
        pd.GeoDataFrame: The DataFrame only contains the names of the minucipios and their id.
    """
    if state.suffix not in ('.xls', '.xlsx'):
        raise TypeError("You did not enter a valid excel file")
    municipios = pd.read_excel(state, engine='openpyxl')
    municipios.columns = [col.lower() for col in municipios.columns]
    return municipios.drop(['entidad'], axis=1)

def assign_seccion_to_municipio(secciones:gpd.GeoDataFrame, municipios:gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """This function combines the secciones and municipios DataFrame.

    Args:
        secciones (gpd.GeoDataFrame): DataFrame with the secciones' geometry
        municipios (gpd.GeoDataFrame): DataFrame with the names of the municipios

    Returns:
        gpd.GeoDataFrame: Final DataFrame to be exported
    """
    gdf = gpd.GeoDataFrame(pd.merge(municipios, secciones, left_on='municipio', right_on='municipio'))
    gdf = gdf.loc[:, ['seccion', 'nombre entidad', 'id_municipio', 'nombre municipio', 'geometry']]
    return gdf.rename(columns={'seccion':'id'})

def export_to_geojson(secciones_by_municipio:gpd.GeoDataFrame) -> str:
    """Exports the secciones files divided by municipio, in this way, the files are separated by municipios in Google earth
    and inside of each miunicipio are the secciones.

    Args:
        secciones_by_municipio (gpd.GeoDataFrame): Final DataFrame to be exported.
    """
    municipio_dict = dict(zip(secciones_by_municipio['id_municipio'].values, secciones_by_municipio['nombre municipio'].values))
    state_name = secciones_by_municipio['nombre entidad'].unique()
    storage_location = define_storage_location(state_name)
    storage_location.mkdir(parents=True, exist_ok=True)
    for id_municipio in secciones_by_municipio['id_municipio'].unique():
        municipio_name = municipio_dict[id_municipio]
        municipio_secciones = secciones_by_municipio[secciones_by_municipio['id_municipio'] == id_municipio]
        municipio_secciones.to_file(storage_location.joinpath(f'{municipio_name}.geojson'))
    return str(storage_location)

def define_storage_location(state_name:str) -> Path:
    """Helper function to defined the location where the files must be stored."""
    return Path(__file__).parent.joinpath(state_name)

if __name__ == '__main__':

    # Load the file with the secciones
    secciones_file = input('Enter the path to the secciones file (It must be and shp file):\n').strip()
    secciones = load_secciones_of(secciones_file)

    # Load the file with the minucipio catalog
    municipios_file = input('Enter the path to the municipios file (It must be an excel file):\n').strip()
    municipios = load_municipio_of(municipios_file)

    # DataFrames are combined to get the secciones and municipios name
    municipios_with_secciones = assign_seccion_to_municipio(secciones, municipios)
    
    # Geojson files are stored here, divided in municipios
    files_location = export_to_geojson(municipios_with_secciones)
    print(f'Files stored at {files_location}')