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
"""
import os
from itertools import izip, izip_longest


class ParseDAT(object):
    dat_files = {
        'CONT.DAT': None,
        'TOLER.DAT': None,
        'FPLAIN.DAT': None,
        'CADPTS.DAT': None,
        'MANNINGS_N.DAT': None,
        'TOPO.DAT': None,
        'INFLOW.DAT': None,
        'OUTFLOW.DAT': None
    }

    def __init__(self, fpath):
        self.project_dir = os.path.dirname(fpath)
        for f in os.listdir(self.project_dir):
            if f in self.dat_files:
                self.dat_files[f] = os.path.join(self.project_dir, f)
            else:
                pass

    def parse_cont(self):
        results = {}
        lines = [
            ['SIMULT', 'TOUT', 'LGPLOT', 'METRIC', 'IBACKUPrescont'],
            ['ICHANNEL', 'MSTREET', 'LEVEE', 'IWRFS', 'IMULTC'],
            ['IRAIN', 'INFIL', 'IEVAP', 'MUD', 'ISED', 'IMODFLOW', 'SWMM'],
            ['IHYDRSTRUCT', 'IFLOODWAY', 'IDEBRV'],
            ['AMANN', 'DEPTHDUR', 'XCONC', 'XARF', 'FROUDL', 'SHALLOWN', 'ENCROACH'],
            ['NOPRTFP', 'SUPER'],
            ['NOPRTC'],
            ['ITIMTEP', 'TIMTEP'],
            ['GRAPTIM']
        ]
        cont = self.dat_files['CONT.DAT']
        with open(cont, 'r') as f:
            c = 1
            for l in lines:
                if c == 1:
                    results.update(dict(izip_longest(l, f.readline().split()[:5])))
                elif c == 7 and results['ICHANNEL'] == '0':
                    results['NOPRTC'] = None
                elif c == 9 and results['LGPLOT'] == '0':
                    results['GRAPTIM'] = None
                else:
                    results.update(dict(izip_longest(l, f.readline().split())))
                c += 1
        return results

    def parse_toler(self):
        results = {}
        lines = [
            ['TOLGLOBAL', 'DEPTOL', 'WAVEMAX'],
            ['COURCHAR_C', 'COURANTFP', 'COURANTC', 'COURANTST'],
            ['COURCHAR_T', 'TIME_ACCEL']
        ]
        toler = self.dat_files['TOLER.DAT']
        with open(toler, 'r') as f:
            for l in lines:
                results.update(dict(izip_longest(l, f.readline().split())))
        return results

    @staticmethod
    def single_parser(file1):
        with open(file1, 'r') as f1:
            for line in f1:
                row = line.split()
                yield row

    @staticmethod
    def double_parser(file1, file2):
        with open(file1, 'r') as f1, open(file2, 'r') as f2:
            for line1, line2 in izip(f1, f2):
                row = line1.split() + line2.split()
                yield row

    def parse_fplain_cadpts(self):
        fplain = self.dat_files['FPLAIN.DAT']
        cadpts = self.dat_files['CADPTS.DAT']
        neighbour = None
        side = 0

        with open(fplain) as fpl:
            for n in fpl.readline().split()[1:5]:
                if n != '0':
                    neighbour = int(n)
                    break
                else:
                    pass
                side += 1

        with open(cadpts) as cad:
            x1, y1 = cad.readline().split()[1:]
            for l in xrange(neighbour-2):
                cad.readline()
            x2, y2 = cad.readline().split()[1:]

        dtx = abs(float(x1) - float(x2))
        dty = abs(float(y1) - float(y2))
        cell_size = dty if side % 2 == 0 else dtx
        results = self.double_parser(fplain, cadpts)
        return cell_size, results

    def parse_mannings_n_topo(self):
        mannings_n = self.dat_files['MANNINGS_N.DAT']
        topo = self.dat_files['TOPO.DAT']
        results = self.double_parser(mannings_n, topo)
        return results

    def parse_inflow(self):
        inflow = self.dat_files['INFLOW.DAT']
        par = self.single_parser(inflow)
        head = dict(zip(['IHOURDAILY', 'IDEPLT'], next(par)))
        inf = {}
        res = {}
        gid = None
        for row in par:
            char = row[0]
            if char == 'C' or char == 'F':
                gid = row[-1]
                inf[gid] = {'row': row, 'nodes': []}
            elif char == 'H':
                inf[gid]['nodes'].append(row)
            elif char == 'R':
                gid = row[1]
                res[gid] = {'row': row}
            else:
                pass
        return head, inf, res

    def parse_outflow(self):
        outflow = self.dat_files['OUTFLOW.DAT']
        par = self.single_parser(outflow)
        channel = {}
        time_stage = {}
        floodplain = {}
        gid = None
        for row in par:
            char = row[0]
            if char == 'K':
                gid = row[-1]
                channel[gid] = {'row': row, 'nodes': []}
            elif char == 'H' or char == 'T':
                channel[gid]['nodes'].append(row)
            elif char == 'N':
                gid = row[-1]
                time_stage[gid] = {'row': row, 'nodes': []}
            elif char == 'S':
                time_stage[gid]['nodes'].append(row)
            elif char.startswith('O'):
                gid = row[-1]
                floodplain[gid] = {'row': row}
            else:
                pass
        return channel, time_stage, floodplain


if __name__ == '__main__':
    x = ParseDAT(r'D:\GIS_DATA\FLO-2D PRO Documentation\Example Projects\Alawai\FPLAIN.DAT')
    c, t, f = x.parse_outflow()
    print(c)
    print(t)
    print(f)
