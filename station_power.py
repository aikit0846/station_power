import processing
import pandas as pd
from qgis.core import QgsProject, QgsFeatureRequest, QgsVectorFileWriter, NULL

dir = '〜/Desktop/station_power/'
input_fname = 'data/target_stations.csv'
output_fname = 'data/result.csv'
l = 500

# データの読み込み
df = pd.read_csv(dir + input_fname, encoding='cp932')
df['number_of_stores'] = 0

# レイヤーの選択
station_layer = QgsProject.instance().mapLayersByName('N02-20_Station_XY')[0]
mesh_layer = QgsProject.instance().mapLayersByName('MESH')[0]

for i in range(len(df)):
    # 駅名
    target = df['station_name'].iloc[i]
    
    # 駅名に対応する地物
    station_layer.selectByExpression(('"N02_005"=\'' + target + '\''))
    target_station_layer = station_layer.materialize(QgsFeatureRequest().setFilterFids(station_layer.selectedFeatureIds()))
    QgsVectorFileWriter.writeAsVectorFormat(target_station_layer,dir + 'data/rail/target_station.shp', 'cp932', driverName='ESRI Shapefile')

    # バッファリング
    buffer_output = processing.run("native:buffer", {'INPUT':target_station_layer,'DISTANCE':l,
    'SEGMENTS':5,'END_CAP_STYLE':0,'JOIN_STYLE':0,'MITER_LIMIT':2,'DISSOLVE':False,'OUTPUT':dir + 'data/rail/buffer_output.shp'})

    # 交差しているメッシュの取り出し
    processing.run("native:selectbylocation", {'INPUT':dir + 'data/mesh/MESH.shp','PREDICATE':[0],
    'INTERSECT':dir + 'data/rail/buffer_output.shp','METHOD':0})

    # メッシュ内の事業所数を集計
    num_stores = 0
    for mesh_feature in mesh_layer.selectedFeatures():
        if mesh_feature['retail'] != NULL:
            num_stores += mesh_feature['retail']
    df['number_of_stores'].iloc[i] = num_stores


df.to_csv(dir + output_fname, encoding='cp932')