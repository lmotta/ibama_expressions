# -*- coding: UTF-8 -*-
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

from qgis.PyQt.QtCore import QObject

from .functions import registerFunctions

def classFactory(iface):
    return IbamaExpressionsPlugin( iface )

class IbamaExpressionsPlugin( QObject ):
    def __init__(self, iface):
        super().__init__()

    def initGui(self):
        registerFunctions()

    def unload(self):
        registerFunctions( False )
