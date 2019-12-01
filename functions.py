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
"""
__author__ = 'Luiz Motta'
__date__ = '2015-01-01'
__copyright__ = '(C) 2015, Luiz Motta'
__revision__ = '$Format:%H$'

from enum import Enum

from qgis.PyQt.QtCore import (
    QDate, QFileInfo, QDir
)
from qgis.core import (
    QgsProject,
    QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsCoordinateTransformContext,
    QgsGeometry, QgsFeature, QgsFeatureRequest,
    QgsExpression
)
from qgis.utils import qgsfunction

class TypeCoordinates(Enum):
    Latitude = 1
    Longitude = 2

def getDMS(geom, crs_id, layer_id, typeCoordinates):
    def dms_format(dd, direction):
        def decdeg2dms(dd):
            minutes, seconds = divmod( abs( dd ) * 3600, 60 )
            degrees, minutes = divmod( minutes, 60 )
            return { 'direction': dd >= 0.0, 'degrees': degrees, 'minutes': minutes, 'seconds': seconds }

        def formatDMS(dms):
            ( d, m ) = tuple( map( lambda v: "{:02.0f}".format( v ), ( dms['degrees'], dms['minutes'] ) ) )
            s = "{:05.2f}".format( dms['seconds'] )
            o = direction[ dms['direction'] ]
            return "{}° {}' {}\" {}".format( d, m, s, o )

        return formatDMS( decdeg2dms( dd ) )

    def checkRange(coord, limits, typeCoord):
        if not ( limits[0] <= coord <= limits[1] ):
            data = ( coord, limits[0], typeCoord, limits[1] )
            msg = "Coordinate '{}' out of range({} <= {} <= {})".format( *data )
            return {
                'isOk': False,
                'message': msg
            }
        return { 'isOk': True }

    if not isinstance( crs_id, str):
        raise Exception("Enter with ID CRS with string type(Ex.: 'EPSG:4326')")
    crsDest = QgsCoordinateReferenceSystem( crs_id )
    if not crsDest.isValid():
        msg = "ID EPSG '{}' is not valid".format( crs_id )
        raise Exception(msg)
    if not crsDest.isGeographic():
        msg = "ID CRS '{}' is not Geographic".format( crs_id  )
        raise Exception(msg)
    project = QgsProject.instance()
    layer = project.mapLayer( layer_id )
    crsLayer = layer.crs()
    if not crsDest == crsLayer:
        ct = QgsCoordinateTransform( crsLayer, crsDest, QgsCoordinateTransformContext() )
        geom.transform( ct )
    point = geom.centroid().asPoint()
    if typeCoordinates == TypeCoordinates.Latitude:
        coord = point.y()
        r = checkRange( coord, ( -90.0, 90.0 ), 'Latitude' )
        if not r['isOk']:
            raise Exception( r['message'] )
        direction = {True: 'N', False: 'S'}
    elif typeCoordinates == TypeCoordinates.Longitude:
        coord = point.x()
        r = checkRange( coord, ( -180.0, 180.0 ), 'Longitude' )
        if not r['isOk']:
            raise Exception( r['message'] )
        direction = {True: 'E', False: 'W'}
    else:
        msg = "Error expression in define type coordinates"
        raise Exception(msg)
    return dms_format( coord, direction )

@qgsfunction(args='auto', group='Ibama', register=False, usesgeometry=True, referenced_columns=[])
def dms_x(value, feature, parent, context):
    """
  <h4>Return</h4>X coordinate of geometry formatted with: DD° MM' SS.SS" Q(W or E)
    <p> Point: The coordinate itself</p>
    <p> Line: The coordinate of center</p>
    <p> Polygon: The coordinate of centroid</p>
  <p><h4>Syntax</h4>dms_x(CRS ID)</p>
  <p><h4>Argument</h4>CRS ID</p>
  <p><h4>Example</h4>dms_x('EPSG:4326')</p>
    """
    geom = QgsGeometry( feature.geometry() )
    crs_id = value
    layer_id = context.variable('layer_id') 
    return getDMS( geom, crs_id, layer_id, TypeCoordinates.Longitude )

@qgsfunction(args='auto', group='Ibama', register=False, usesgeometry=True, referenced_columns=[])
def dms_y(value, feature, parent, context):
    """
  <h4>Return</h4>Y coordinate of geometry formatted with:  DD° MM' SS.SS" Q(N or S)
    <p> Point: The coordinate itself</p>
    <p> Line: The coordinate of center</p>
    <p> Polygon: The coordinate of centroid</p>
  <p><h4>Syntax</h4>dms_y(CRS ID)</p>
  <p><h4>Argument</h4>CRS ID</p>
  <p><h4>Example</h4>dms_y('EPSG:4326')</p>
    """
    geom = QgsGeometry( feature.geometry() )
    crs_id = value
    layer_id = context.variable('layer_id') 
    return getDMS( geom, crs_id, layer_id, TypeCoordinates.Latitude )

@qgsfunction(args='auto', group='Ibama', register=False, usesgeometry=False, referenced_columns=[])
def getFileName(value, feature, parent):
    """
  <h4>Return</h4>Only file name whithout extension
  <p><h4>Syntax</h4>getFileName(file_path)</p>
  <p><h4>Argument</h4>File name with path</p>
  <p><h4>Example</h4>getFileName('/home/user/readme.txt')</p>
    """
    try:
        info = QFileInfo( value )
        name = info.completeBaseName()
    except:
        msg = "Enter with File name. Value = '{}'.".format( value )
        raise Exception( msg )
    return name

@qgsfunction(args='auto', group='Ibama', register=False, usesgeometry=False, referenced_columns=[])
def existsFile(value, feature, parent):
    """
  <h4>Return</h4>True if exists and False otherwise
  <p><h4>Syntax</h4>existFile(file_path)</p>
  <p><h4>Argument</h4>File name with path</p>
  <p><h4>Example</h4>existsFile('/home/not_exist.txt')</p>
    """
    try:
        info = QFileInfo( value )
        exists = info.isFile()
    except:
        msg = "Enter with File name. Value = '{}'.".format( value )
        raise Exception( msg )
    return exists

@qgsfunction(args='auto', group='Ibama', register=False, usesgeometry=False, referenced_columns=[])
def getDateLandsat(value, feature, parent):
    """
  <h4>Return</h4>QDate from file name of Landsat
  <p><h4>Syntax</h4>getDateLandsat(name_landsat)</p>
  <p><h4>Argument</h4>File name of Landsat</p>
  <p><h4>Example</h4>getDateLandsat('LC81390452014295LGN00.tif')</p>
    """
    msgError = "Enter with landsat name (ex. 'LC81390452014295LGN00'). Value = '{}'.".format( value )
    if not value[3:16].isdigit():
        raise Exception( msgError )
    try:
        julianYear = QDate( int( value[9:13] ), 1, 1 ).toJulianDay() - 1
        julianDays = julianYear + int( value[13:16] )
        v_date = QDate.fromJulianDay ( julianDays )
    except:
        raise Exception( msgError )
    if not v_date.isValid():
        raise Exception( msgError )
    return v_date

@qgsfunction(args='auto', group='Ibama', register=False, usesgeometry=False, referenced_columns=[])
def getDateRapideye(value, feature, parent):
    """
  <h4>Return</h4>QDate from file name of Rapideye
  <p><h4>Syntax</h4>getDateRapideye(name_rapideye)</p>
  <p><h4>Argument</h4>File name of Rapideye</p>
  <p><h4>Example</h4>getDateRapideye('2227625_2012-12-26T142009_RE1_3A-NAC_14473192_171826.tif')</p>
    """
    msgError = "Enter with Rapideye name (ex. '2227625_2012-12-26T142009_RE1_3A-NAC_14473192_171826'). Value = '{}'.".format( value )
    try:
        v_date = QDate.fromString( value.split('_')[1][:10], "yyyy-MM-dd" )
    except:
        raise Exception( msgError )
    if not v_date.isValid():
        raise Exception( msgError )
    return v_date

@qgsfunction(args='auto', group='Ibama', register=False, usesgeometry=False, referenced_columns=[])
def getDateSentinel(value, feature, parent):
    """
  <h4>Return</h4>QDate from file name of Sentinel
  <p><h4>Syntax</h4>getDateSentinel(name_sentinel)</p>
  <p><h4>Argument</h4>File name of Sentinel</p>
  <p><h4>Example</h4>getDateSentinel('s1a-ew-grd-hh-20141031t223708-20141031t223811-003079-003869-001.tif')</p>
    """
    msgError = "Enter with Sentinel name (ex. 's1a-ew-grd-hh-20141031t223708-20141031t223811-003079-003869-001'). Value = '{}'.".format( value )
    try:
        v_date = QDate.fromString( value.split('-')[5][:8], "yyyyMMdd" )
    except:
        raise Exception( msgError )
    if not v_date.isValid():
        raise Exception( msgError )
    return v_date

@qgsfunction(args='auto', group='Ibama', register=False, usesgeometry=False, referenced_columns=[])
def getDatePlanetScope(value, feature, parent):
    """
  <h4>Return</h4>QDate from file name of PlanetScope
  <p><h4>Syntax</h4>getDatePlanetScope(name_planetscope)</p>
  <p><h4>Argument</h4>File name of PlanetScope</p>
  <p><h4>Example</h4>getDatePlanetScope('PSScene4Band_20190310_131656_0f4a.tif')</p>
    """
    msgError = "Enter with PlanetScope name (ex. 'PSScene4Band_20190310_131656_0f4a'). Value = '{}'.".format( value )
    try:
        v_date = QDate.fromString( value.split('_')[1], "yyyyMMdd" )
    except:
        raise Exception( msgError )
    if not v_date.isValid():
        raise Exception( msgError )
    return v_date

@qgsfunction(args='auto', group='Ibama', register=False, usesgeometry=True, referenced_columns=[])
def area_crs(value, feature, parent, context):
    """
  <h4>Return</h4>Area using the CRS ID
  <p><h4>Syntax</h4>area_crs(CRS ID)</p>
  <p><h4>Argument</h4>CRS ID</p>
  <p><h4>Example</h4>area_crs('EPSG:5671')</p>
    """
    geom = QgsGeometry( feature.geometry() )
    crs_id = value
    layer_id = context.variable('layer_id') 
    if not isinstance( crs_id, str):
        raise Exception("Enter with ID CRS with string type(Ex.: 'EPSG:4326')")
    crsDest = QgsCoordinateReferenceSystem( crs_id )
    if not crsDest.isValid():
        msg = "ID EPSG '{}' is not valid".format( crs_id )
        raise Exception(msg)
    if crsDest.isGeographic():
        msg = "ID CRS '{}' is Geographic".format( crs_id )
        raise Exception(msg)
    project = QgsProject.instance()
    layer = project.mapLayer( layer_id )
    crsLayer = layer.crs()
    if not crsDest == crsLayer:
        ct = QgsCoordinateTransform( crsLayer, crsDest, QgsCoordinateTransformContext() )
        geom.transform( ct )
    return geom.area()

@qgsfunction(args='auto', group='Ibama', register=False, usesgeometry=False, referenced_columns=[])
def is_selected(value, feature, parent, context):
    """
  <h4>Return</h4>True if selected and False otherwise
  <p><h4>Syntax</h4>is_selected()</p>
  <p><h4>Argument</h4>None</p>
    """
    layer_id = context.variable('layer_id') 
    project = QgsProject.instance()
    layer = project.mapLayer( layer_id )
    feat = QgsFeature()
    iter = layer.getSelectedFeatures( QgsFeatureRequest( feature.id() ) )
    return iter.nextFeature( feat )

# //////// Register of Expressions Functions \\\\\\\\
l_functions = (
    dms_x, dms_y,
    getFileName, existsFile,
    getDateLandsat, getDateRapideye, getDateSentinel, getDatePlanetScope, 
    area_crs,
    is_selected
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