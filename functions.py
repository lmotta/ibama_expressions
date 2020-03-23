"""
/***************************************************************************
Name                 : IBAMA expressions
Description          : Set of expressions for QGIS
Date                 : April, 2015. February, 2018 Migrated for QGIS 3
copyright            : (C) 2015 by Luiz Motta
email                : motta.luiz@gmail.com

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

Updates/New:
- 2020-03-23:
    - Rename: getDateSentinel to getDateSentinel1
    - New: getDateSentinel2
- 2020-02-12:
    - New: getUTM, getCRSLayer
    - Update: getCRSLayer, area_crs
    - Remove(exists in default expressions): is_selected, dms_x, dms_y, existsFile, getFileName

"""
__author__ = 'Luiz Motta'
__date__ = '2015-01-01'
__copyright__ = '(C) 2015, Luiz Motta'
__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import QDate

from qgis.core import (
    QgsProject,
    QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsCoordinateTransformContext,
    QgsGeometry,
    QgsExpression
)
from qgis.utils import qgsfunction


def getCRSLayer(layer_id):
    project = QgsProject.instance()
    layer = project.mapLayer( layer_id )
    return layer.crs()

@qgsfunction(args='auto', group='Ibama', register=False, usesgeometry=True, referenced_columns=[])
def getUTMZone(feature, parent, context):
    """
  <h4>Return</h4>UTM zone: Number(longitudinal) and Letter(latitudinal)
    <p> Point: The coordinate itself</p>
    <p> Line: The coordinate of center</p>
    <p> Polygon: The coordinate of centroid</p>
  <p><h4>Syntax</h4>getUTMZone()</p>
  <p><h4>Example</h4>getUTMZone() --> 20M</p>
    """
    geom = feature.geometry().centroid()
    layer_id = context.variable('layer_id')
    crsLayer = getCRSLayer( layer_id )
    crsDest = QgsCoordinateReferenceSystem('EPSG:4326')
    if not crsLayer == crsDest:
        ct = QgsCoordinateTransform( crsLayer, crsDest, QgsCoordinateTransformContext() )
        geom.transform( ct )
    point = geom.asPoint()
    vlong, vlat = point.x(), point.y()
    zone = int( vlong / 6 + 31 )
    # Letter
    wordLat = 'CDEFGHJKLMNPQRSTUVWX'
    lettersLat = { n-10: wordLat[ n ] for n in range( len( wordLat ) ) }
    
    value = int( vlat/8 ) - int( vlat < 0 )
    letter = lettersLat[ value ]

    return f"{zone}{letter}"

@qgsfunction(args='auto', group='Ibama', register=False, usesgeometry=False, referenced_columns=[])
def getDateLandsat(name, feature, parent):
    """
  <h4>Return</h4>QDate from file name of Landsat
  <p><h4>Syntax</h4>getDateLandsat(name_landsat)</p>
  <p><h4>Argument</h4>File name of Landsat</p>
  <p><h4>Example</h4>getDateLandsat('LC81390452014295LGN00.tif')</p>
    """
    msgError = f"Enter with landsat name (ex. 'LC81390452014295LGN00'). Value = '{name}'."
    if not name[3:16].isdigit():
        raise Exception( msgError )
    try:
        julianYear = QDate( int( name[9:13] ), 1, 1 ).toJulianDay() - 1
        julianDays = julianYear + int( name[13:16] )
        v_date = QDate.fromJulianDay ( julianDays )
    except:
        raise Exception( msgError )
    if not v_date.isValid():
        raise Exception( msgError )
    return v_date

@qgsfunction(args='auto', group='Ibama', register=False, usesgeometry=False, referenced_columns=[])
def getDateRapideye(name, feature, parent):
    """
  <h4>Return</h4>QDate from file name of Rapideye
  <p><h4>Syntax</h4>getDateRapideye(name_rapideye)</p>
  <p><h4>Argument</h4>File name of Rapideye</p>
  <p><h4>Example</h4>getDateRapideye('2227625_2012-12-26T142009_RE1_3A-NAC_14473192_171826.tif')</p>
    """
    msgError = f"Enter with Rapideye name (ex. '2227625_2012-12-26T142009_RE1_3A-NAC_14473192_171826'). Value = '{name}'."
    try:
        v_date = QDate.fromString( name.split('_')[1][:10], "yyyy-MM-dd" )
    except:
        raise Exception( msgError )
    if not v_date.isValid():
        raise Exception( msgError )
    return v_date

@qgsfunction(args='auto', group='Ibama', register=False, usesgeometry=False, referenced_columns=[])
def getDateSentinel1(name, feature, parent):
    """
  <h4>Return</h4>QDate from file name of Sentinel1
  <p><h4>Syntax</h4>getDateSentinel1(name_sentinel)</p>
  <p><h4>Argument</h4>File name of Sentinel1</p>
  <p><h4>Example</h4>getDateSentinel1('s1a-ew-grd-hh-20141031t223708-20141031t223811-003079-003869-001.tif')</p>
    """
    msgError = f"Enter with Sentinel1 name (ex. 's1a-ew-grd-hh-20141031t223708-20141031t223811-003079-003869-001'). Value = '{name}'."
    try:
        v_date = QDate.fromString( name.split('-')[5][:8], "yyyyMMdd" )
    except:
        raise Exception( msgError )
    if not v_date.isValid():
        raise Exception( msgError )
    return v_date

@qgsfunction(args='auto', group='Ibama', register=False, usesgeometry=False, referenced_columns=[])
def getDateSentinel2(name, feature, parent):
    """
  <h4>Return</h4>QDate from file name of Sentinel2
  <p><h4>Syntax</h4>getDateSentinel2(name_sentinel)</p>
  <p><h4>Argument</h4>File name of Sentinel2</p>
  <p><h4>Example</h4>getDateSentinel2('S2A_MSIL1C_20170105T013442_N0204_R031_T53NMJ_20170105T013443.tif')</p>
    """
    msgError = f"Enter with Sentinel2 name (ex. 'S2A_MSIL1C_20170105T013442_N0204_R031_T53NMJ_20170105T013443'). Value = '{name}'."
    try:
        v_date = QDate.fromString( name.split('_')[2][:8], "yyyyMMdd" )
    except:
        raise Exception( msgError )
    if not v_date.isValid():
        raise Exception( msgError )
    return v_date

@qgsfunction(args='auto', group='Ibama', register=False, usesgeometry=False, referenced_columns=[])
def getDatePlanetScope(name, feature, parent):
    """
  <h4>Return</h4>QDate from file name of PlanetScope
  <p><h4>Syntax</h4>getDatePlanetScope(name_planetscope)</p>
  <p><h4>Argument</h4>File name of PlanetScope</p>
  <p><h4>Example</h4>getDatePlanetScope('PSScene4Band_20190310_131656_0f4a.tif')</p>
    """
    msgError = f"Enter with PlanetScope name (ex. 'PSScene4Band_20190310_131656_0f4a'). Value = '{name}'."
    try:
        v_date = QDate.fromString( name.split('_')[1], "yyyyMMdd" )
    except:
        raise Exception( msgError )
    if not v_date.isValid():
        raise Exception( msgError )
    return v_date

@qgsfunction(args='auto', group='Ibama', register=False, usesgeometry=True, referenced_columns=[])
def area_crs(crs_id, feature, parent, context):
    """
  <h4>Return</h4>Area using the CRS ID
  <p><h4>Syntax</h4>area_crs(CRS ID)</p>
  <p><h4>Argument</h4>CRS ID</p>
  <p><h4>Example</h4>area_crs('EPSG:5671')</p>
    """
    geom = QgsGeometry( feature.geometry() )
    if not isinstance( crs_id, str):
        raise Exception("Enter with ID CRS with string type(Ex.: 'EPSG:4326')")
    crsDest = QgsCoordinateReferenceSystem( crs_id )
    if not crsDest.isValid():
        msg = "ID EPSG '{}' is not valid".format( crs_id )
        raise Exception(msg)
    if crsDest.isGeographic():
        msg = "ID CRS '{}' is Geographic".format( crs_id )
        raise Exception(msg)
    layer_id = context.variable('layer_id')
    crsLayer = getCRSLayer( layer_id )
    if not crsDest == crsLayer:
        ct = QgsCoordinateTransform( crsLayer, crsDest, QgsCoordinateTransformContext() )
        geom.transform( ct )
    return geom.area()

# //////// Register of Expressions Functions \\\\\\\\
l_functions = (
    getUTMZone,
    getDateLandsat, getDateRapideye,
    getDateSentinel1, getDateSentinel2,
    getDatePlanetScope, 
    area_crs
)
def registerFunctions(isRegister=True):
    if isRegister:
        f_r = QgsExpression.registerFunction
        arg_f = lambda f: f
    else:
        f_r = QgsExpression.unregisterFunction
        arg_f = lambda f: f.name()
    
    for f in l_functions:
        f_r( arg_f( f ) )
# \\\\\\\\ Register of Expressions Functions ////////