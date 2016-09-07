# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Flo2D
                                 A QGIS plugin
 FLO-2D tools for QGIS
                             -------------------
        begin                : 2016-08-28
        copyright            : (C) 2016 by Lutra Consulting for FLO-2D
        email                : info@lutraconsulting.co.uk
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.gui import *
from qgis.core import *
import processing
import logging

from .utils import *
import os.path
import pyspatialite.dbapi2 as db
from .user_communication import UserCommunication
from flo2d_parser import ParseDAT


class Flo2dGeoPackage(object):
    """GeoPackage object class for storing FLO-2D model data"""

    def __init__(self, path, iface):
        self.path = path
        self.iface = iface
        self.uc = UserCommunication(iface, 'FLO-2D')
        self.parser = None
        self.cell_size = None

    def set_parser(self, fname):
        self.parser = ParseDAT(fname)

    def database_connect(self):
        """Connect database with sqlite3"""
        try:
            self.conn = db.connect(self.path)
            return True
        except:
            self.msg = "Couldn't connect to GeoPackage"
            return False

    def create_tables(self):
        # inflow
        sqls= ["""
CREATE TABLE inflow (
    "fid" integer NOT NULL PRIMARY KEY,
    "name" varchar(255), -- name of inflow
    "time_series_fid" integer REFERENCES time_series(fid), -- id of time series used for inflow
    "type" character(1) NOT NULL, -- destination element type Channel, Floodplain (Reservoir data goes into separate table resorvoirs)
    "inoutfc" integer NOT NULL, -- INOUTFC = 0 for inflow and 1 for outflow
    "geom" POLYGON, -- area of inflow/reservoir
    "note" varchar (255)
);
""",
"insert into gpkg_geometry_columns values ('inflow', 'geom', 'POLYGON', {}, 0, 0);",
"insert into gpkg_contents (table_name, data_type, srs_id) values ('inflow', 'features', {});"]

        # spatial index
        slq = 'CREATE VIRTUAL TABLE rtree_{}_geom USING rtree(id, minx, maxx, miny, maxy)'

    def check_gpkg(self):
        """Check if file is GeoPackage """
        try:
            c = self.conn.cursor()
            c.execute('SELECT * FROM gpkg_contents;')
            c.fetchone()
            return True
        except:
            return False

    def execute(self, statement, inputs=None):
        """Execute a prepared SQL statement on this geopackage database."""
        with self.conn as db_con:
            cursor = db_con.cursor()
            if inputs is not None:
                result_cursor = cursor.execute(statement, inputs)
            else:
                result_cursor = cursor.execute(statement)
            return result_cursor

    def import_fplain(self):
        self.cell_size, data = self.parser.parse_fplain_cadpts()
        if self.cell_size == 0:
            self.uc.bar_error("Cell size is 0 - something went wrong!")
        else:
            pass
        # check if a grid exists in the grid table
        if not self.is_table_empty('grid'):
            r = self.uc.question('There is a grid already defined in GeoPackage. Overwrite it?')
            if r == QMessageBox.Yes:
                # delete previous grid
                sql = 'DELETE FROM grid;'
                self.execute(sql)
            else:
                self.uc.bar_info('Import cancelled', dur=3)
                return
        else:
            pass

        # insert grid data into gpkg
        sql = """
INSERT INTO grid
(fid, cell_north, cell_east, cell_south, cell_west, n_value, elevation, geom)
VALUES
    """
        inp = []
        for d in data:
            g = square_from_center_and_size(d[-2], d[-1], self.cell_size)
            inp.append('({0}, {1})'.format(','.join(d[:7]), g))
        sql += '\n{};'.format(',\n'.join(inp))
        self.uc.log_info(sql)
        self.execute(sql)
        self.uc.bar_info('Grid imported', dur=3)

    def import_cont_toler(self):
        if not self.is_table_empty('cont'):
            sql = 'DELETE FROM cont;'
            self.execute(sql)
        else:
            pass
        sql = """
        INSERT INTO cont
        (fid, name, value, note)
        VALUES
        """
        cont = self.parser.parse_cont()
        toler = self.parser.parse_toler()
        cont.update(toler)
        c = 1
        for option in cont:
            sql += '({} {} {} NULL)\n'.format(c, option, cont[option])
            c += 1
        self.uc.log_info(sql)
        self.execute(sql)

    def import_inflow(self):
        if not self.is_table_empty('inflow'):
            sql = 'DELETE FROM inflow;'
            self.execute(sql)
        else:
            pass
        if not self.is_table_empty('reservoirs'):
            sql = 'DELETE FROM reservoirs;'
            self.execute(sql)
        else:
            pass
        inflow = iter(self.parser.parse_inflow())
        head = next(inflow)

    def import_topo(self):
        # in case FPLAIN is missing this require finding each grid cell neighbours
        pass

    def is_table_empty(self, table):
        r = self.execute("SELECT rowid FROM {};".format(table))
        if r.fetchone():
            return False
        else:
            return True
