# -*- coding: utf-8 -*-

# FLO-2D Preprocessor tools for QGIS

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version


from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QTableWidgetItem, QComboBox, QApplication
from .ui_utils import load_ui, set_icon
from ..geopackage_utils import GeoPackageUtils
from ..user_communication import UserCommunication

uiDialog, qtBaseClass = load_ui("mud_and_sediment")
class MudAndSedimentDialog(qtBaseClass, uiDialog):
    def __init__(self, con,  iface, lyrs):
        qtBaseClass.__init__(self)
        uiDialog.__init__(self)
        self.iface = iface
        self.lyrs = lyrs
        self.setupUi(self)
        self.uc = UserCommunication(iface, "FLO-2D")
        self.con = con
        self.gutils = None
        
        self.equations = ["Zeller and Fullerton", "Yang", "Engelund and Hansen", "Ackers and White", "Laursen",
                          "Tofaletti, MPM-Woo", "MPM-Smart", "Karim-Kennedy", "Parker-Klingeman-McLean", "Van-Rijn" ]
        
        # Icons:
      
        # set_icon(self.create_polygon_sed_btn, "mActionCapturePolygon.svg")
        # set_icon(self.save_changes_sed_btn, "mActionSaveAllEdits.svg")
        set_icon(self.revert_changes_sed_btn, "mActionUndo.svg")
        set_icon(self.delete_sed_btn, "mActionDeleteSelected.svg")
        set_icon(self.sed_add_size_fraction_btn, "add.svg")
        set_icon(self.sed_delete_size_fraction_btn, "remove.svg")
        set_icon(self.sed_add_size_fraction_dp_btn, "add.svg")
        set_icon(self.sed_delete_size_fraction_dp_btn, "remove.svg")
        set_icon(self.sed_add_size_fraction_cell_btn, "add.svg")
        set_icon(self.sed_delete_size_fraction_cell_btn, "remove.svg")
        set_icon(self.sed_add_rating_curve_btn, "add.svg")
        set_icon(self.sed_delete_rating_curve_btn, "remove.svg")
        set_icon(self.sed_add_rating_curve_dp_btn, "add.svg")
        set_icon(self.sed_delete_rating_curve_dp_btn, "remove.svg")
        set_icon(self.add_rigid_bed_btn, "add.svg")
        set_icon(self.delete_rigid_bed_btn, "remove.svg")    
              
        self.revert_changes_sed_btn.setVisible(False)
        self.delete_sed_btn.setVisible(False)
        self.rigid_bed_area_lbl.setVisible(False)
        self.sed_rigid_bed_area_cbo.setVisible(False)
        
        self.sed_size_fraction_tblw.setColumnWidth(0, 170)
        self.sed_size_fraction_tblw.setColumnWidth(1, 90)
        self.sed_size_fraction_tblw.setColumnWidth(2, 90)
        self.sed_rating_curve_tblw.setColumnWidth(1, 80)
        self.sed_rating_curve_tblw.setColumnWidth(2, 80)
        self.sed_rating_curve_tblw.setColumnWidth(3, 80)
        
        self.sed_size_fraction_tblw.setColumnHidden(3,True)
        self.sed_rating_curve_tblw.setColumnHidden(4,True)
        # self.sed_size_fraction_grp.setStyleSheet("border: 2px solid Red")
        
        # Connections:
        
        # self.save_changes_sed_btn.clicked.connect(self.delete_rigit_bed_cell)        
        # self.create_polygon_sed_btn.clicked.connect(self.create_polygon_sed)
        # self.save_changes_sed_btn.clicked.connect(self.save_sed_lyrs_edits)
        # self.revert_changes_sed_btn.clicked.connect(self.cancel_sed_lyrs_edits)
        # self.delete_sed_btn.clicked.connect(self.delete_sed)
        
        # Radio buttons connections:
        self.mud_debris_transport_radio.clicked.connect(self.show_mud)
        self.sediment_transport_radio.clicked.connect(self.show_sediment)
        self.none_transport_radio.clicked.connect(self.show_none)
        
        # Size Fractions connections:
        self.sed_size_fraction_tblw.cellClicked.connect(self.sed_size_fraction_tblw_clicked) 
        self.sed_size_fraction_dp_tblw.cellChanged.connect(self.sed_size_fraction_dp_tblw_cellchanged) 
        self.sed_size_grid_tblw.cellChanged.connect(self.sed_size_grid_tblw_cellchanged) 
        
        self.sed_add_size_fraction_btn.clicked.connect(self.sed_add_size_fraction_btn_clicked)
        self.sed_add_size_fraction_dp_btn.clicked.connect(self.sed_add_size_fraction_dp_btn_clicked)
        self.sed_add_size_fraction_cell_btn.clicked.connect(self.sed_add_size_fraction_cell_btn_clicked)
        
        self.sed_delete_size_fraction_btn.clicked.connect(self.sed_delete_size_fraction_btn_clicked)
        self.sed_delete_size_fraction_dp_btn.clicked.connect(self.sed_delete_size_fraction_dp_btn_clicked)
        
        # Supply Rating Curve connections:
        self.sed_rating_curve_tblw.cellClicked.connect(self.sed_rating_curve_tblw_clicked)
        self.sed_rating_curve_dp_tblw.cellChanged.connect(self.sed_rating_curve_dp_tblw_cellchanged) 
        
        self.sed_add_rating_curve_btn.clicked.connect(self.sed_add_rating_curve_btn_clicked)
        self.sed_add_rating_curve_dp_btn.clicked.connect(self.sed_add_rating_curve_dp_btn_clicked)
        
        self.sed_delete_rating_curve_btn.clicked.connect(self.sed_delete_rating_curve_btn_clicked)
        
        self.sed_delete_rating_curve_dp_btn.clicked.connect(self.sed_delete_rating_curve_dp_btn_clicked)
        self.add_rigid_bed_btn.clicked.connect(self.sed_add_rigid_bed_cell_btn_clicked)
        self.delete_rigid_bed_btn.clicked.connect(self.sed_delete_rigid_bed_btn_clicked)
        
        self.sed_rigid_nodes_tblw.cellChanged.connect(self.sed_rigid_nodes_tblw_cellchanged) 
        self.sed_delete_size_fraction_cell_btn.clicked.connect(self.sed_delete_size_fraction_cell_btn_clicked)
        
        self.setup_connection()
        self.populate_mud_and_sediment()

    def setup_connection(self):
        con = self.iface.f2d["con"]
        if con is None:
            return
        else:
            self.con = con
            self.gutils = GeoPackageUtils(self.con, self.iface)
            
    def populate_mud_and_sediment(self):
        if self.gutils.get_cont_par("MUD") == "1":
            self.mud_debris_transport_radio.click() 
            
            self.mud_basin_grp.setChecked(int(self.gutils.get_cont_par("IDEBRV")))
            
            mud = self.gutils.execute("SELECT va, vb, ysa, ysb, sgsm, xkx FROM mud").fetchone() 
            if mud:
                va, vb, ysa, ysb, sgsm, xkx =  mud
                self.mud_vis_vs_sed_coeff_dbox.setValue(va)
                self.mud_vis_vs_sed_exp_dbox.setValue(vb)
                self.mud_ys_vs_sed_coeff_dbox.setValue(ysa)
                self.mud_ys_vs_sed_exp_dbox.setValue(ysb)
                self.mud_specific_gravity_dbox.setValue(sgsm)
                self.mud_laminar_fr_dbox.setValue(xkx) 
                basin = self.gutils.execute("SELECT grid_fid, area_fid FROM mud_cells").fetchone()
                if basin:
                    volume = self.gutils.execute("SELECT debrisv FROM mud_areas").fetchone()
                    if volume: 
                        self.mud_basin_grid_sbox.setValue(basin[0])
                        self.mud_basin_vol_dbox.setValue(volume[0])                   
                   
        elif self.gutils.get_cont_par("ISED") == "1":
            # Block signals:
            self.sed_size_fraction_tblw.blockSignals(True);
            self.sed_size_fraction_dp_tblw.blockSignals(True)
            self.sed_size_grid_tblw.blockSignals(True)
            self.sed_rigid_nodes_tblw.blockSignals(True)

            self.sed_rating_curve_tblw.blockSignals(True);
            self.sed_rating_curve_dp_tblw.blockSignals(True)  
                      
            self.sediment_transport_radio.click()
            sed = self.gutils.execute("SELECT isedeqg, isedsizefrac, dfifty, sgrad, sgst, dryspwt, cvfg, isedsupply, isedisplay, scourdep  FROM sed").fetchone() 
            if sed:
                isedeqg, isedsizefrac, dfifty, sgrad, sgst, dryspwt, cvfg, isedsupply, isedisplay, scourdep = sed
                self.sed_transp_eq_cbo.setCurrentIndex(isedeqg-1)
                self.sed_specific_gravity_dbox.setValue(sgst)
                self.sed_dry_specific_weight_dbox.setValue(dryspwt) 
                self.sed_D50_dbox.setValue(dfifty)
                self.sed_grad_coeff_dbox.setValue(sgrad)
                self.sed_report_node_dbox.setValue(isedisplay)
                self.sed_max_scour_depth_dbox.setValue(scourdep)  
                self.sed_size_fraction_grp.setChecked(isedsizefrac)
                self.sed_rating_curve_grp.setChecked(isedsupply)
                self.sed_vol_conctr_dbox.setValue(cvfg)
                
                # Load Size Fractions table:
                size_fractions = self.gutils.execute("SELECT isedeqi, bedthick, cvfi, dist_fid FROM sed_groups ORDER BY dist_fid").fetchall()
                if size_fractions:
                    self.sed_size_fraction_tblw.setRowCount(0)
                    for row_number, sf in enumerate(size_fractions):
                        self.sed_size_fraction_tblw.insertRow(row_number)

                        combo = QComboBox()
                        combo.setStyleSheet("QComboBox { border: 1px gray; } QFrame { border: 3px solid blue; }")
                        for e in self.equations:
                            combo.addItem(e)       
                        self.sed_size_fraction_tblw.setCellWidget(row_number,0,combo)                          
                        combo.setCurrentIndex(sf[0]-1)
                                              
                        item = QTableWidgetItem()
                        item.setData(Qt.DisplayRole, sf[1]) 
                        # item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)                           
                        self.sed_size_fraction_tblw.setItem(row_number, 1, item)
                        item = QTableWidgetItem()
                        item.setData(Qt.DisplayRole, sf[2]) 
                        # item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)                             
                        self.sed_size_fraction_tblw.setItem(row_number, 2, item) 
                        item = QTableWidgetItem()
                        item.setData(Qt.DisplayRole, sf[3])                         
                        self.sed_size_fraction_tblw.setItem(row_number, 3, item) 

                        if row_number == 0:                       
                            first_dist = sf[3]         

                    # Load Routimg Fractions for first row of Size Fractions table:
                    self.load_size_routing_fractions_table(first_dist)                   
    
                    # Load Grid Elements for first row of Size Fractions table:
                    self.load_size_fraction_cells_table(0)
                    
                    self.sed_size_fraction_tblw.selectRow(0)
                    
                # Load Supply Rating Curve table:
                rating_curve = self.gutils.execute("SELECT fid, isedcfp, ased, bsed, dist_fid FROM sed_supply_areas ORDER BY dist_fid").fetchall()
                if rating_curve:
                    self.sed_rating_curve_tblw.setRowCount(0)
                    rc_grid = "SELECT grid_fid FROM sed_supply_cells WHERE fid = ?;"
                    for row_number, rc in enumerate(rating_curve):
                        grid = self.gutils.execute(rc_grid, (rc[0],)).fetchone()
                        self.sed_rating_curve_tblw.insertRow(row_number)
                        item = QTableWidgetItem()
                        item.setData(Qt.DisplayRole, grid[0])    
                        # item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)                        
                        self.sed_rating_curve_tblw.setItem(row_number, 0, item)
                        
                        item = QTableWidgetItem()
                        item.setData(Qt.DisplayRole, rc[1])                         
                        self.sed_rating_curve_tblw.setItem(row_number, 1, item)
                        
                        item = QTableWidgetItem()
                        item.setData(Qt.DisplayRole, rc[2])                         
                        self.sed_rating_curve_tblw.setItem(row_number, 2, item) 
                        
                        item = QTableWidgetItem()
                        item.setData(Qt.DisplayRole, rc[3])                         
                        self.sed_rating_curve_tblw.setItem(row_number, 3, item) 
                        
                        item = QTableWidgetItem()
                        item.setData(Qt.DisplayRole, rc[4])                         
                        self.sed_rating_curve_tblw.setItem(row_number, 4, item)  
                         
                        if row_number == 0:                       
                            first_dist = rc[4]

                    # Load Routimg Fractions for first row of Suply Rating Curve table:
                    self.load_rc_routing_fractions(first_dist) 
                    
                    self.sed_rating_curve_tblw.selectRow(0)                 
                
                # Load Rigid cells:
                self.load_rigid_nodes_table()
                # self.sed_rigid_nodes_tblw.setRowCount()
                # rigid_cells = self.gutils.execute("SELECT grid_fid, area_fid FROM sed_rigid_cells ORDER BY grid_fid").fetchall()
                # if rigid_cells:
                #     for rc in rigid_cells:
                #
                #         item = QTableWidgetItem()
                #         item.setData(Qt.DisplayRole, rc[1])                         
                #         self.sed_rating_curve_tblw.setItem(row_number, 1, item)
                        
                    # for index in range(self.sed_rigid_nodes_listw.count()):
                    #     item = self.sed_rigid_nodes_listw.item(index)
                    #     item.setFlags(item.flags() | Qt.ItemIsEditable)
        
            # Unblock signals:
            self.sed_size_fraction_tblw.blockSignals(False);
            self.sed_size_fraction_dp_tblw.blockSignals(False)
            self.sed_size_grid_tblw.blockSignals(False)
            self.sed_rigid_nodes_tblw.blockSignals(False)

            self.sed_rating_curve_tblw.blockSignals(False);
            self.sed_rating_curve_dp_tblw.blockSignals(False)     
                     
        else:
            self.none_transport_radio.click()
            
    def show_mud(self):
        self.mud_sediment_tabWidget.setTabEnabled(1, False) 
        self.mud_sediment_tabWidget.setTabEnabled(2, False) 
        self.mud_sediment_tabWidget.setTabEnabled(0, True)  
        self.mud_sediment_tabWidget.setStyleSheet("QTabBar::tab::disabled {width: 0; height: 0; margin: 0; padding: 0; border: none;} ")        
        self.mud_sediment_tabWidget.setCurrentIndex(0)
        
        
    def show_sediment(self):
        self.mud_sediment_tabWidget.setTabEnabled(0, False) 
        self.mud_sediment_tabWidget.setTabEnabled(2, False)
        self.mud_sediment_tabWidget.setTabEnabled(1, True) 
        self.mud_sediment_tabWidget.setStyleSheet("QTabBar::tab::disabled {width: 0; height: 0; margin: 0; padding: 0; border: none;} ")       
        self.mud_sediment_tabWidget.setCurrentIndex(1) 
        
    def show_none(self):
        self.mud_sediment_tabWidget.setTabEnabled(0, False) 
        # self.mud_sediment_tabWidget.setStyleSheet("QTabBar::tab::disabled {width: 0; height: 0; margin: 0; padding: 0; border: none;} ")   
        self.mud_sediment_tabWidget.setTabEnabled(1, False) 
        self.mud_sediment_tabWidget.setTabEnabled(2, True) 
        self.mud_sediment_tabWidget.setStyleSheet("QTabBar::tab::disabled {width: 0; height: 0; margin: 0; padding: 0; border: none;} ")     
        self.mud_sediment_tabWidget.setCurrentIndex(2) 
                
    def ok_to_save(self): 
        if self.mud_debris_transport_radio.isChecked():
            return True
            
        elif self.sediment_transport_radio.isChecked():
            
            first = "WARNING 281021.0528: Sediment transport data not saved!\n\n" 
            wrng = first
            # Check cell numbers in size fractions nodes table:
            for row in range(0, self.sed_size_grid_tblw.rowCount()):
                item_cell = self.sed_size_grid_tblw.item(row, 0)
                if not item_cell:
                    wrng += "* Assign cell number to all size fraction grid elements.\n\n"
                    break
                elif item_cell.text() == "":
                    wrng += "* Assign cell number to all size fraction grid elements.\n\n" 
                    break                
            
            # Check cell numbers in supply rating curve table:
            for row in range(0, self.sed_rating_curve_tblw.rowCount()):
                item_cell = self.sed_rating_curve_tblw.item(row, 0)
                if not item_cell:
                    wrng += "* Assign cell number to all supply rating curves.\n\n"
                    break
                elif item_cell.text() == "":
                    wrng += "* Assign cell number to all supply rating curves.\n\n"
                    break

            # Check cell numbers in bed rigid nodes:
            for row in range(0, self.sed_rigid_nodes_tblw.rowCount()):
                item_cell = self.sed_rigid_nodes_tblw.item(row, 0)
                if not item_cell: 
                    wrng +=  "* Assign a valid cell number to all rigid bed cells.\n\n" 
                    break             
                elif item_cell.text() == "":
                    wrng += "* Assign a valid cell number to all rigid bed cells.\n\n"
                    break
            
            if wrng == first:  
                return True   
            else:
                self.uc.show_warn(wrng) 
                return False    
            
        elif self.none_transport_radio.isChecked():
            return True                 
                
    def save_mud_sediment(self): 
        try:
            if self.mud_debris_transport_radio.isChecked():
                self.gutils.set_cont_par("ISED", 0)
                self.gutils.set_cont_par("MUD", 1) 
                self.gutils.set_cont_par("IDEBRV", self.mud_basin_grp.isChecked()) 
                
                mud_sql  = "INSERT INTO mud (va, vb, ysa, ysb, sgsm, xkx) VALUES (?,?,?,?,?,?);" 
                va = self.mud_vis_vs_sed_coeff_dbox.value()
                vb = self.mud_vis_vs_sed_exp_dbox.value()
                ysa = self.mud_ys_vs_sed_coeff_dbox.value()
                ysb = self.mud_ys_vs_sed_exp_dbox.value()
                sgsm = self.mud_specific_gravity_dbox.value()
                xhx =  self.mud_laminar_fr_dbox.value()
                self.gutils.clear_tables("mud")
                self.gutils.execute(mud_sql, (va, vb, ysa, ysb, sgsm, xhx))     
                
                debrisv = self.mud_basin_vol_dbox.value()
                self.gutils.clear_tables("mud_areas")
                self.gutils.execute("INSERT INTO mud_areas (debrisv) VALUES (?);", (debrisv,))
    
                grid_fid = self.mud_basin_grid_sbox.value()
                # area_fid = self.mud_basin_vol_dbox.value()
                area_fid = "1"
                self.gutils.clear_tables("mud_cells")
                self.gutils.execute("INSERT INTO mud_cells (grid_fid, area_fid) VALUES (?,?);", (grid_fid, area_fid))             
                
            elif self.sediment_transport_radio.isChecked():              
                    
                self.gutils.set_cont_par("MUD", 0) 
                self.gutils.set_cont_par("ISED", 1) 
                
                # Save global sediment transport parameters:
                isedeqg = self.sed_transp_eq_cbo.currentIndex() + 1
                isedsizefrac = self.sed_size_fraction_grp.isChecked()
                dfifty = self.sed_D50_dbox.value()
                sgrad = self.sed_grad_coeff_dbox.value()
                sgst = self.sed_specific_gravity_dbox.value()
                dryspwt =  self.sed_dry_specific_weight_dbox.value()
                cvfg = self.sed_vol_conctr_dbox.value()
                isedsupply = self.sed_rating_curve_grp.isChecked()
                isedisplay = self.sed_report_node_dbox.value()
                scourdep =  self.sed_max_scour_depth_dbox.value() 
               
                self.gutils.clear_tables("sed")
                sed_sql  = """INSERT INTO sed (isedeqg, isedsizefrac, dfifty, sgrad, sgst, 
                                                dryspwt, cvfg, isedsupply, isedisplay, scourdep) VALUES (?,?,?,?,?,?,?,?,?,?);"""            
                self.gutils.execute(sed_sql, (isedeqg, isedsizefrac, dfifty, sgrad, sgst, 
                                                dryspwt, cvfg, isedsupply, isedisplay, scourdep))              
                
                # Save Size Fractions table:
                sed_sql  = ["""INSERT INTO sed_groups (isedeqi, bedthick, cvfi, dist_fid) VALUES""", 4]
                for row in range(0, self.sed_size_fraction_tblw.rowCount()):
                    combo = self.sed_size_fraction_tblw.cellWidget(row,0)                          
                    isedeqi = combo.currentIndex() + 1
                    bed_thick = self.sed_size_fraction_tblw.item(row, 1).text()
                    conc = self.sed_size_fraction_tblw.item(row, 2).text()
                    dist_fid  = self.sed_size_fraction_tblw.item(row, 3).text()
                    sed_sql += [(isedeqi, bed_thick , conc, dist_fid)]
                self.gutils.clear_tables("sed_groups")
                self.gutils.batch_execute(sed_sql)            
    
                # Save Supply Rating Curve table:
                sr_curve_sql  = ["""INSERT INTO sed_supply_areas (isedcfp, ased, bsed, dist_fid) VALUES""", 4]
                self.gutils.clear_tables("sed_supply_cells")
                for row in range(0, self.sed_rating_curve_tblw.rowCount()):
                    node = self.sed_rating_curve_tblw.item(row, 0).text()
                    self.gutils.execute("INSERT INTO sed_supply_cells (grid_fid, area_fid) VALUES (?, ?);", (node, str(row + 1)))
                    isedcfp = self.sed_rating_curve_tblw.item(row, 1).text()
                    ased = self.sed_rating_curve_tblw.item(row, 2).text()
                    bsed = self.sed_rating_curve_tblw.item(row, 3).text()
                    dist_fid  = self.sed_rating_curve_tblw.item(row, 4).text()
                    sr_curve_sql += [(isedcfp , ased, bsed, dist_fid)]
                self.gutils.clear_tables("sed_supply_areas")
                self.gutils.batch_execute(sr_curve_sql) 
    
            else:
                self.gutils.set_cont_par("MUD", 0) 
                self.gutils.set_cont_par("ISED", 0)              

        except Exception as e:
            QApplication.restoreOverrideCursor()
            self.uc.show_error("ERROR 251021.0916: unable to save mud/sediment data!.\n", e)

                       
    def create_polygon_sed(self):
        self.lyrs.enter_edit_mode("sed_rigid_areas")

    def sed_size_fraction_tblw_clicked(self, row):
        
        # Find sediment size distribution (diameter, %):
        self.load_size_fraction_routing_fractions_table(row)       
        # Find cells with this distribution:
        self.load_size_fraction_cells_table(row)     

    def sed_size_fraction_dp_tblw_cellchanged(self, row, col):
        # Save Size Fractions ratings table:
        current_row = self.sed_size_fraction_tblw.currentRow()
        if current_row != -1:
            current_dist_fid = self.sed_size_fraction_tblw.item(current_row, 3).text()
            if int(current_dist_fid) > 0:
                insert_rt_sql  = ["""INSERT INTO sed_group_frac_data (sediam, sedpercent, dist_fid) VALUES""", 3]
                for rw in range(0, self.sed_size_fraction_dp_tblw.rowCount()):
                    sediam = self.sed_size_fraction_dp_tblw.item(rw, 0).text()
                    sedpercent = self.sed_size_fraction_dp_tblw.item(rw, 1).text()
                    insert_rt_sql += [(sediam, sedpercent, current_dist_fid)]
                self.gutils.execute("DELETE FROM sed_group_frac_data WHERE dist_fid = ?;", (current_dist_fid,))    
                self.gutils.batch_execute(insert_rt_sql) 

    def sed_rating_curve_dp_tblw_cellchanged(self, row, col):
        # Save Supply rating curve ratings table:
        current_row = self.sed_rating_curve_tblw.currentRow()
        if current_row != -1:
            current_dist_fid = self.sed_rating_curve_tblw.item(current_row, 4).text()
            if int(current_dist_fid) > 0:
                insert_rt_sql  = ["""INSERT INTO sed_supply_frac_data (ssediam, ssedpercent, dist_fid) VALUES""", 3]
                for rw in range(0, self.sed_rating_curve_dp_tblw.rowCount()):
                    ssediam = self.sed_rating_curve_dp_tblw.item(rw, 0).text()
                    ssedpercent = self.sed_rating_curve_dp_tblw.item(rw, 1).text()
                    insert_rt_sql += [(ssediam, ssedpercent, current_dist_fid)]
                self.gutils.execute("DELETE FROM sed_supply_frac_data WHERE dist_fid = ?;", (current_dist_fid,))    
                self.gutils.batch_execute(insert_rt_sql) 
                
    def sed_size_grid_tblw_cellchanged(self, row, col):
        # Save Size Fractions cells:
        
        # Check cell numbers in size grid nodes:
        # for row in range(0, self.sed_size_grid_tblw.rowCount()):
        #     item_cell = self.sed_size_grid_tblw.item(row, 0)
        #     if not item_cell:                
        #         self.uc.show_info("Assign a valid cell number to all size fraction grid elements!") 
        #         return  
        #     elif item_cell.text() == "":                
        #         self.uc.show_info("Assign a valid cell number to all size fraction grid elements!") 
        #         return           

        
        # Delete all features in 'sed_group_cells' and 'sed_group_areas' related to current row of Size Fraction table:   
        sed_group_areas_fid_qry = "SELECT fid FROM sed_group_areas WHERE group_fid = ?;"
        current_row = self.sed_size_fraction_tblw.currentRow() + 1
        sed_group_areas_fid = self.gutils.execute(sed_group_areas_fid_qry, (current_row,)).fetchall()
        if sed_group_areas_fid:
            for fid in sed_group_areas_fid:
                self.gutils.execute("DELETE FROM sed_group_cells WHERE area_fid = ?;", (fid[0],))
            self.gutils.execute("DELETE FROM sed_group_areas WHERE group_fid = ?;", (current_row,))    

        # Insert rows from Grid Element widget table into 'sed_group_cells' and 'sed_group_areas': 
        insert_sed_group_areas_sql  = ["""INSERT INTO sed_group_areas (group_fid) VALUES""", 1]  
        for dummy in range(0, self.sed_size_grid_tblw.rowCount()): 
            insert_sed_group_areas_sql +=  [(str(current_row))] 
        self.gutils.batch_execute(insert_sed_group_areas_sql)    

        sed_group_areas_fid = self.gutils.execute(sed_group_areas_fid_qry, (current_row,)).fetchall()
        if sed_group_areas_fid:
            insert_sed_group_cells_sql  = ["""INSERT INTO sed_group_cells (grid_fid, area_fid) VALUES""", 2]  
            for i,fid in enumerate(sed_group_areas_fid):
                cell_item = self.sed_size_grid_tblw.item(i,0)
                if cell_item:
                    cell = cell_item.text()   
                    insert_sed_group_cells_sql +=  [(cell, fid[0])] 
            self.gutils.batch_execute(insert_sed_group_cells_sql)               
        
    def sed_rigid_nodes_tblw_cellchanged(self, row, col):
        # Check cell numbers in bed rigid nodes:
        for row in range(0, self.sed_rigid_nodes_tblw.rowCount()):
            item_cell = self.sed_rigid_nodes_tblw.item(row, 0)
            if not item_cell:                
                self.uc.show_info("Assign a valid cell number to all rigid bed cells!") 
                return  
            elif item_cell.text() == "":                
                self.uc.show_info("Assign a valid cell number to all rigid bed cells!") 
                return        

        # Save Supply rigid nodes table:
        rigid_insert_sql  = ["""INSERT INTO sed_rigid_cells (grid_fid, area_fid) VALUES""", 2]
        for row in range(0, self.sed_rigid_nodes_tblw.rowCount()):
            node = self.sed_rigid_nodes_tblw.item(row, 0).text()
            rigid_insert_sql += [(node, str(row))]
        self.gutils.clear_tables("sed_rigid_cells")
        self.gutils.batch_execute(rigid_insert_sql)
         
    def sed_rating_curve_tblw_clicked(self, row):
        self.load_rating_curve_routing_fractions_table(row)     


    def sed_add_size_fraction_btn_clicked(self):
        max_dist_fid = self.gutils.execute("""SELECT MAX(dist_fid) FROM sed_groups;""").fetchone()[0]
        if not max_dist_fid:
            max_dist_fid = 0
        
        self.sed_size_fraction_tblw.insertRow(self.sed_size_fraction_tblw.rowCount())
        combo = QComboBox()
        combo.setStyleSheet("QComboBox { border: 1px gray; } QFrame { border: 3px solid blue; }")
        for e in self.equations:
            combo.addItem(e)    
        row_number = self.sed_size_fraction_tblw.rowCount() - 1
        self.sed_size_fraction_tblw.setCellWidget(row_number,0,combo)
        
        item = QTableWidgetItem()
        item.setData(Qt.DisplayRole, 10)                         
        self.sed_size_fraction_tblw.setItem(row_number, 1, item)
        
        item = QTableWidgetItem()
        item.setData(Qt.DisplayRole, 0.025)                         
        self.sed_size_fraction_tblw.setItem(row_number, 2, item) 

        item = QTableWidgetItem()
        item.setData(Qt.DisplayRole, str(max_dist_fid + 1))                         
        self.sed_size_fraction_tblw.setItem(row_number, 3, item) 
       
        self.sed_size_fraction_tblw.selectRow(row_number)
        self.sed_size_fraction_tblw.setFocus()
           
        self.sed_size_fraction_dp_tblw.setRowCount(0) 
        self.sed_size_grid_tblw.setRowCount(0)            
 
    def sed_add_rating_curve_btn_clicked(self):
        max_dist_fid = self.gutils.execute("""SELECT MAX(dist_fid) FROM sed_supply_areas;""").fetchone()[0]
        if not max_dist_fid:
            max_dist_fid = 0
            
        self.sed_rating_curve_tblw.insertRow(self.sed_rating_curve_tblw.rowCount())
        row_number = self.sed_rating_curve_tblw.rowCount() - 1
        
        item = QTableWidgetItem()
        item.setData(Qt.DisplayRole, 0)                         
        self.sed_rating_curve_tblw.setItem(row_number, 1, item)
        item = QTableWidgetItem()
        item.setData(Qt.DisplayRole, 1)                         
        self.sed_rating_curve_tblw.setItem(row_number, 2, item) 
        item = QTableWidgetItem()
        item.setData(Qt.DisplayRole, 0)                         
        self.sed_rating_curve_tblw.setItem(row_number, 3, item) 
        
        item = QTableWidgetItem()
        item.setData(Qt.DisplayRole, str(max_dist_fid + 1))                         
        self.sed_rating_curve_tblw.setItem(row_number, 4, item)          
               
        self.sed_rating_curve_tblw.selectRow(row_number)
        self.sed_rating_curve_tblw.setFocus()
               
        self.load_rating_curve_routing_fractions_table(row_number)       
        
    def load_size_fraction_routing_fractions_table(self, row):
        self.sed_size_fraction_dp_tblw.blockSignals(True)          
        self.sed_size_fraction_dp_tblw.setRowCount(0)     
        any_dist = self.sed_size_fraction_tblw.item(row, 3)
        if any_dist:
            dist_fid = self.sed_size_fraction_tblw.item(row, 3).text()
            self.load_size_routing_fractions_table(dist_fid)
        self.sed_size_fraction_dp_tblw.blockSignals(False)        

    def load_rating_curve_routing_fractions_table(self, row): 
        self.sed_rating_curve_dp_tblw.blockSignals(True)              
        self.sed_rating_curve_dp_tblw.setRowCount(0)     
        any_dist = self.sed_rating_curve_tblw.item(row, 4)
        if any_dist:
            dist_fid = self.sed_rating_curve_tblw.item(row, 4).text()
            self.load_rc_routing_fractions(dist_fid)
        self.sed_rating_curve_dp_tblw.blockSignals(False)       


    def load_rc_routing_fractions(self, dist_fid):
        routing_data_qry = "SELECT ssediam, ssedpercent FROM sed_supply_frac_data WHERE dist_fid =? ORDER BY ssediam;"
        routing_fractions = self.gutils.execute(routing_data_qry, (dist_fid,)).fetchall()
        if routing_fractions:
            for row_number, ss_dp in enumerate(routing_fractions):
                self.sed_rating_curve_dp_tblw.insertRow(row_number)
                item = QTableWidgetItem()
                item.setData(Qt.DisplayRole, ss_dp[0])                         
                self.sed_rating_curve_dp_tblw.setItem(row_number, 0, item)
                item = QTableWidgetItem()
                item.setData(Qt.DisplayRole, ss_dp[1])                         
                self.sed_rating_curve_dp_tblw.setItem(row_number, 1, item)        
    
    def load_size_routing_fractions_table(self, dist_fid):
        routing_data_qry = "SELECT sediam, sedpercent FROM sed_group_frac_data WHERE dist_fid =?  ORDER BY sediam;"
        routing_fractions = self.gutils.execute(routing_data_qry, (dist_fid,)).fetchall()
        if routing_fractions:
            self.sed_size_fraction_dp_tblw.setRowCount(0)
            for row_number, sf_dp in enumerate(routing_fractions):
                self.sed_size_fraction_dp_tblw.insertRow(row_number)
                item = QTableWidgetItem()
                item.setData(Qt.DisplayRole, sf_dp[0])                         
                self.sed_size_fraction_dp_tblw.setItem(row_number, 0, item)
                item = QTableWidgetItem()
                item.setData(Qt.DisplayRole, sf_dp[1])                         
                self.sed_size_fraction_dp_tblw.setItem(row_number, 1, item)

    def load_size_fraction_cells_table(self, row):
        self.sed_size_grid_tblw.blockSignals(True) 
        self.sed_size_grid_tblw.setRowCount(0)  
        sed_group_cells_qry = """SELECT grid_fid FROM sed_group_cells WHERE area_fid IN 
                            (SELECT fid FROM sed_group_areas WHERE group_fid = ?) ORDER BY grid_fid"""
        sed_group_cells = self.gutils.execute(sed_group_cells_qry, (row+1,)).fetchall()
        if sed_group_cells:
            for row_number, cell in enumerate(sed_group_cells):
                self.sed_size_grid_tblw.insertRow(row_number)
                item = QTableWidgetItem()
                item.setData(Qt.DisplayRole, cell[0])                         
                self.sed_size_grid_tblw.setItem(row_number, 0, item)        
        self.sed_size_grid_tblw.blockSignals(False)  

    def load_rigid_nodes_table(self):
        self.sed_rigid_nodes_tblw.blockSignals(True) 
        self.sed_rigid_nodes_tblw.setRowCount(0)  
        rigid_cells_qry = """SELECT grid_fid, area_fid FROM sed_rigid_cells ORDER BY grid_fid"""
        # sed_group_cells_qry = """SELECT grid_fid FROM sed_group_cells WHERE area_fid IN 
        #                     (SELECT fid FROM sed_group_areas WHERE group_fid = ?) ORDER BY grid_fid"""
        sed_rigid_cells = self.gutils.execute(rigid_cells_qry).fetchall()
        if sed_rigid_cells:
            for row_number, cell in enumerate(sed_rigid_cells):
                self.sed_rigid_nodes_tblw.insertRow(row_number)
                item = QTableWidgetItem()
                item.setData(Qt.DisplayRole, cell[0])                         
                self.sed_rigid_nodes_tblw.setItem(row_number, 0, item)        
        self.sed_rigid_nodes_tblw.blockSignals(False) 

        
    def sed_add_size_fraction_cell_btn_clicked(self):
        n_rows = self.sed_size_grid_tblw.rowCount()
        self.sed_size_grid_tblw.insertRow(n_rows)
        self.sed_size_grid_tblw.selectRow(n_rows)
        self.sed_size_grid_tblw.setFocus()

    def sed_add_rigid_bed_cell_btn_clicked(self):
        n_rows = self.sed_rigid_nodes_tblw.rowCount()
        self.sed_rigid_nodes_tblw.insertRow(n_rows)
        self.sed_rigid_nodes_tblw.selectRow(n_rows)
        self.sed_rigid_nodes_tblw.setFocus()        

    def sed_add_size_fraction_dp_btn_clicked(self):
        self.sed_size_fraction_dp_tblw.blockSignals(True)
        n_rows = self.sed_size_fraction_dp_tblw.rowCount()
        self.sed_size_fraction_dp_tblw.insertRow(n_rows)
        
        item = QTableWidgetItem()
        item.setData(Qt.DisplayRole, 0)                         
        self.sed_size_fraction_dp_tblw.setItem(n_rows, 0, item)
        item = QTableWidgetItem()
        item.setData(Qt.DisplayRole, 0)                         
        self.sed_size_fraction_dp_tblw.setItem(n_rows, 1, item) 
        
        self.sed_size_fraction_dp_tblw.selectRow(n_rows)
        self.sed_size_fraction_dp_tblw.setFocus()
        self.sed_size_fraction_dp_tblw.blockSignals(False)
        self.sed_size_fraction_dp_tblw_cellchanged(0,0)
          
        self.sed_size_fraction_dp_tblw.selectRow(n_rows+1)
        self.sed_size_fraction_dp_tblw.setFocus()
 
    def sed_add_rating_curve_dp_btn_clicked(self):
        self.sed_rating_curve_dp_tblw.blockSignals(True)
        n_rows = self.sed_rating_curve_dp_tblw.rowCount()
        self.sed_rating_curve_dp_tblw.insertRow(n_rows)
        
        item = QTableWidgetItem()
        item.setData(Qt.DisplayRole, 0)                         
        self.sed_rating_curve_dp_tblw.setItem(n_rows, 0, item)
        item = QTableWidgetItem()
        item.setData(Qt.DisplayRole, 0)                         
        self.sed_rating_curve_dp_tblw.setItem(n_rows, 1, item) 
        
        self.sed_rating_curve_dp_tblw.selectRow(n_rows)
        self.sed_rating_curve_dp_tblw.setFocus()
        self.sed_rating_curve_dp_tblw.blockSignals(False)
        self.sed_rating_curve_dp_tblw_cellchanged(0,0)
          
        self.sed_rating_curve_dp_tblw.selectRow(n_rows+1)
        self.sed_rating_curve_dp_tblw.setFocus()
 
    def sed_delete_size_fraction_btn_clicked(self):  
        self.sed_size_fraction_tblw.removeRow(self.sed_size_fraction_tblw.currentRow())  
        
    def sed_delete_size_fraction_dp_btn_clicked(self):
        self.sed_size_fraction_dp_tblw.removeRow(self.sed_size_fraction_dp_tblw.currentRow()) 
        self.sed_size_fraction_dp_tblw_cellchanged(0,0)       

        
    def sed_delete_rating_curve_dp_btn_clicked(self):
        self.sed_rating_curve_dp_tblw.removeRow(self.sed_rating_curve_dp_tblw.currentRow()) 
        self.sed_rating_curve_dp_tblw_cellchanged(0,0)

    def sed_delete_rating_curve_btn_clicked(self):  
        self.sed_rating_curve_tblw.removeRow(self.sed_rating_curve_tblw.currentRow()) 

    def sed_delete_size_fraction_cell_btn_clicked(self):
        self.sed_size_grid_tblw.removeRow(self.sed_size_grid_tblw.currentRow()) 
        # self.sed_size_grid_tblw.blockSignals(True)
        self.sed_size_grid_tblw_cellchanged(0,0)
        # self.sed_size_grid_tblw.blockSignals(False)
        
    def sed_delete_rigid_bed_btn_clicked(self):
        self.sed_rigid_nodes_tblw.removeRow(self.sed_rigid_nodes_tblw.currentRow()) 
        self.sed_rigid_nodes_tblw_cellchanged(0,0)
                   
    def save_sed_lyrs_edits(self):
        """
        Save changes of sed_rigid_areas layer.
        """
        if not self.gutils or not self.lyrs.any_lyr_in_edit("sed_rigid_areas"):
            return
        self.lyrs.save_lyrs_edits("sed_rigid_areas")
        self.lyrs.lyrs_to_repaint = [self.lyrs.data["sed_rigid_areas"]["qlyr"]]
        self.lyrs.repaint_layers()                 