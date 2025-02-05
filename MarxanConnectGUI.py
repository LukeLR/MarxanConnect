# importing wx files
import wx
import wx.lib.agw.aui as aui
import wx.adv
import wx.html2


# import matplotlib
import matplotlib

matplotlib.use('WXAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.collections import PatchCollection

# import spatial modules
import geopandas as gpd
from descartes import PolygonPatch
import shapely
import cartopy

# import system helper modules
import os
import sys
import pandas
import numpy
import json
import platform
import subprocess

# import gui template made by wxformbuilder
import gui

from collections import defaultdict

os.environ["UBUNTU_MENUPROXY"]="0"
if platform.system() == 'Darwin':
    import pexpect
    wx.SystemOptions.SetOption(u"osx.openfiledialog.always-show-types","1")

if platform.system() == 'Linux':
    import pexpect

# define wildcards
wc_MarCon = "Marxan Connect Project (*.MarCon)|*.MarCon|" \
            "All files (*.*)|*.*"


if getattr(sys, 'frozen', False):
    MCPATH = sys._MEIPASS
else:
    MCPATH = os.path.dirname(os.path.abspath(__file__))

sys.path.append(MCPATH)

# import MarxanConnect python module
import marxanconpy

with open(os.path.join(MCPATH, 'VERSION')) as version_file:
    MarxanConnectVersion = version_file.read().strip()

class MarxanConnectGUI(gui.MarxanConnectGUI):
    def __init__(self, parent):
        """
        initialize parent class (the entire GUI)
        """
        os.chdir(MCPATH)
        gui.MarxanConnectGUI.__init__(self, parent)
        # set the icon
        self.set_icon(frame=self, rootpath=MCPATH)

        # start up log
        self.log = LogForm(parent=self)
        print(MCPATH)

        # set opening tab to Spatial Input (0)
        self.auinotebook.ChangeSelection(0)

        # # set posthoc page off by default
        # self.posthocdefault = False
        # self.on_posthoc(event=None)

        # set MwZ option off by default
        self.mwzdefault = False
        self.on_mwz(event=None)

        # set help page
        # self.on_metric_definition_choice(event=None) #currently disabled so that help appears blank/less intimidating

        self.demo_matrixTypeRadioBox.SetItemToolTip(0, "In a probability matrix, each cell represents the probability of movement from site A (row) to site B (column). May or may not account for mortality. If there is no mortality, rows sum to 1")
        self.demo_matrixTypeRadioBox.SetItemToolTip(1, "In a migration matrix, each cell represents the probability of a successful migrant in site B (column) originated in site A (row). Columns sum to 1.")
        self.demo_matrixTypeRadioBox.SetItemToolTip(2, "In a flow matrix (often mislabeled as a flux matrix), each cell represents the number of elements/individuals moving from site A (row) to site B (column) per unit time.")

        self.demo_matrixFormatRadioBox.SetItemToolTip(0,"Matrix format data has the connectivity values arranged is a square format (i.e.the same number of rows and columns). The row names are the donor sites and the column names are the recipient sites ")
        self.demo_matrixFormatRadioBox.SetItemToolTip(1,"An Edge List has 3 columns: the donor sites ('id1'), the recipient sites ('id2'), and the connectivity values ('value')")
        self.demo_matrixFormatRadioBox.SetItemToolTip(2,"An Edge List with Time has 4 columns: time ('time'), the donor sites ('id1'), the recipient sites ('id2'), and the connectivity values ('value')")
        self.demo_matrixFormatRadioBox.SetItemToolTip(3,"An Edge List with Type has 4 columns: type ('type'), the donor sites ('id1'), the recipient sites ('id2'), and the connectivity values ('value')")

        self.demo_rescale_edgeRadioBox.SetItemToolTip(0,"Rescales the connectivity matrix using a spatially weighted average where there is overlap. In areas with partial overlap, connectivity is assumed to be proportional to the overlap. For example, if a planning unit has a 50% overlap with connectivity data (i.e. half of the planning unit has connectivity data, and the other half does not), and the connectivity value is 10, the connectivity value is taken from a spatial average across that planning unit (i.e. a final connectivity value of 5).")
        self.demo_rescale_edgeRadioBox.SetItemToolTip(1,"Rescales the connectivity matrix using a spatially weighted average where there is overlap. In areas with partial overlap, connectivity is assumed to be homogeneous. For example, if a planning unit has a 50% overlap with connectivity data (i.e. half of the planning unit has connectivity data, and the other half does not), and the connectivity value is 10, the connectivity value is considered homogenous across the planning unit (i.e. a final connectivity value of 10).")

        self.demo_rescale_edgeRadioBox.GetItemToolTip(0).SetAutoPop(30000)
        self.demo_rescale_edgeRadioBox.GetItemToolTip(1).SetAutoPop(30000)

        # Either load or launch new project
        if len(sys.argv) > 1:
            self.spatial = {}
            self.project = {}
            self.project['version'] = {}
            self.project['version']['marxanconpy'] = marxanconpy.__version__
            self.project['version']['MarxanConnect'] = MarxanConnectVersion
            self.project['filepaths'] = defaultdict(str)
            self.project['filepaths']['projfile'] = str(sys.argv[1])
            self.workingdirectory = os.path.dirname(self.project['filepaths']['projfile'])
            os.chdir(self.workingdirectory)
            self.load_project_function(launch=True)
        else:
            # launch a blank new project
            self.on_new_project(event=None, rootpath=MCPATH, launch=True)

            # launch Getting started window
            GettingStartedframe = GettingStarted(parent=self)
            GettingStartedframe.Show()
            # self.project['filepaths'] = defaultdict(str)
            # self.project['filepaths']['projfile'] =r"C:\Users\daigl\Documents\GitHub\MarxanConnect\docs\tutorial\CF_demographic\tutorial.MarCon"
            # self.workingdirectory = os.path.dirname(self.project['filepaths']['projfile'])
            # self.load_project_function(launch=True)

    def set_icon(self, frame, rootpath):
        # set the icon
        icons = wx.IconBundle()
        for sz in [16, 32, 48, 96, 256]:
            try:
                icon = wx.Icon(os.path.join(rootpath, 'docs' , 'images' , 'icon_bundle.ico'),
                               wx.BITMAP_TYPE_ICO,
                               desiredWidth=sz,
                               desiredHeight=sz)
                icons.AddIcon(icon)
            except:
                pass
                frame.SetIcons(icons)
                
    def on_posthoc(self, event):
        for i in range(self.auinotebook.GetPageCount()):
            if self.auinotebook.GetPageText(i) == "7) Post-Hoc Evaluation":
                posthocpage = i
            if self.auinotebook.GetPageText(i) == "8) Plotting Options" or self.auinotebook.GetPageText(i) == "7) Plotting Options":
                plottingpage = i
            if self.auinotebook.GetPageText(i) == "9) Plot" or self.auinotebook.GetPageText(i) == "8) Plot":
                plotpage = i

        if not self.posthocdefault:
            self.auinotebook.SetPageText(plottingpage, u"7) Plotting Options")
            if hasattr(self, 'plot'):
                self.auinotebook.SetPageText(plotpage, u"8) Plot")
                print(plotpage)
            self.auinotebook.RemovePage(posthocpage)
            self.posthocdefault = True
        else:
            if hasattr(self, 'plot'):
                self.auinotebook.RemovePage(plotpage)
            self.auinotebook.RemovePage(plottingpage)
            self.auinotebook.AddPage(self.postHocEvaluation, u"7) Post-Hoc Evaluation", False, wx.NullBitmap)
            self.auinotebook.AddPage(self.plottingOptions, u"8) Plotting Options", False, wx.NullBitmap)
            if hasattr(self, 'plot'):
                self.auinotebook.AddPage(self.plot, u"9) Plot", False, wx.NullBitmap)
            self.posthocdefault = False

    def on_mwz( self, event ):
        if not self.mwzdefault:
            self.marxan_Radio.Hide()
            self.marxanAnalysis.Layout()
            self.mwzdefault = True
        else:
            self.marxan_Radio.Show()
            self.marxanAnalysis.Layout()
            self.mwzdefault = False

# ##########################  project managment functions ##############################################################

    def on_new_project(self, event, rootpath=MCPATH, launch=False):
        """
        open a new project and name/save a new project file
        """
        # create project list to store project specific data
        self.spatial = {}
        self.project = marxanconpy.marcon.new_project(rootpath)
        self.project['version']['MarxanConnect'] = MarxanConnectVersion
        self.workingdirectory = MCPATH

        # if called at launch time, no need to ask users to create a new project file right away
        if not launch:
            dlg = wx.FileDialog(self, "Create a new project file:", style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT, wildcard=wc_MarCon)
            if dlg.ShowModal() == wx.ID_OK:
                self.project['filepaths']['projfile'] = dlg.GetPath()
                self.project['filepaths']['projfilename'] = dlg.GetFilename()
                self.workingdirectory = dlg.GetDirectory()
                with open(self.project['filepaths']['projfile'], 'w') as fp:
                    json.dump(self.project, fp, indent=4, sort_keys=True)
                frame.SetTitle('Marxan Connect (Project: ' + self.project['filepaths']['projfilename'] + ')')
            dlg.Destroy()

        # set default file paths in GUI
        os.chdir(self.workingdirectory)
        self.project = marxanconpy.marcon.edit_working_directory(self.project,self.workingdirectory,'absolute')
        self.set_GUI_options()
        self.set_GUI_filepaths()


        # trigger functions which enable/disable options
        self.on_demo_matrixFormatRadioBox(event=None)
        self.on_demo_rescaleRadioBox(event=None)
        self.on_land_type_choice(event=None)
        self.enable_metrics()
        self.enable_discrete()
        self.enable_postHoc()
        self.outline_shapefile_choices()
        self.colormap_shapefile_choices()
        self.colormap_metric_choices(1)
        self.colormap_metric_choices(2)
        self.colormap_metric_choices("pre-eval")

    def on_load_project(self, event):
        """
        Create and show the Open FileDialog to load a project
        """
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultFile="",
            wildcard=wc_MarCon,
            style=wx.FD_OPEN | wx.FD_CHANGE_DIR
        )
        if dlg.ShowModal() == wx.ID_OK:
            self.project = {}
            self.project['version'] = {}
            self.project['version']['marxanconpy'] = marxanconpy.__version__
            self.project['version']['MarxanConnect'] = MarxanConnectVersion
            self.project['filepaths'] = defaultdict(str)
            self.project['filepaths']['projfile'] = dlg.GetPath()
            self.workingdirectory = dlg.GetDirectory()
            os.chdir(self.workingdirectory)
        dlg.Destroy()
        self.load_project_function()

    def load_project_function(self,launch=False):
        self.spatial = {}
        self.project = marxanconpy.marcon.load_project(self.project['filepaths']['projfile'])
        marxanconpy.marcon.validate_project(self.project)
        if not launch:
            frame.SetTitle('Marxan Connect (Project: ' + self.project['filepaths']['projfilename'] + ')')
        else:
            self.SetTitle('Marxan Connect (Project: ' + self.project['filepaths']['projfilename'] + ')')

        if 'MarxanConnect' in self.project['version']:
            if self.project['version']['MarxanConnect'] != MarxanConnectVersion:
                print("Warning: This project file was created with a different version of Marxan Connect. Attempting to "
                      "update for compatibility")
                self.project['version']['MarxanConnect'] = MarxanConnectVersion
        else:
            print("Warning: This project file was created with a different version of Marxan Connect. Attempting to "
                  "update for compatibility")
            self.project['version'] = {}
            self.project['version']['marxanconpy'] = marxanconpy.__version__
            self.project['version']['MarxanConnect'] = MarxanConnectVersion

        self.project = marxanconpy.marcon.edit_working_directory(self.project,
                                                                 self.workingdirectory,
                                                                 "absolute")

        self.set_GUI_options()

        # set default file paths in GUI
        self.set_GUI_filepaths()

        # trigger functions which enable/disable options
        self.on_PU_file(event=None)
        self.on_FA_file(event=None)
        self.on_AA_file(event=None)
        self.on_demo_matrixFormatRadioBox(event=None)
        self.on_demo_rescaleRadioBox(event=None)
        if self.project['options']['metricsCalculated']:
            self.customize_spec.Enable(enable=True)
            self.export_CF_files.Enable(enable=True)
            self.export_BD_file.Enable(enable=True)
            self.export_pudat.Enable(enable=True)
            self.export_metrics.Enable(enable=True)
            self.custom_spec_panel.SetToolTip(None)
        self.enable_metrics()
        self.enable_discrete()
        self.enable_postHoc()
        self.outline_shapefile_choices()
        self.colormap_shapefile_choices()
        self.colormap_metric_choices(1)
        self.colormap_metric_choices(2)
        self.colormap_metric_choices("pre-eval")
        self.on_new_spec()
        self.update_discrete_grid()

    def set_GUI_options(self):
        # set default options
        self.fa_status_radioBox.SetStringSelection(self.project['options']['fa_status'])
        self.aa_status_radioBox.SetStringSelection(self.project['options']['aa_status'])

        self.demo_PU_CM_progress.SetValue(self.project['options']['demo_pu_cm_progress'])
        self.demo_matrixTypeRadioBox.SetStringSelection(self.project['options']['demo_conmat_type'])
        self.demo_matrixFormatRadioBox.SetStringSelection(self.project['options']['demo_conmat_format'])
        self.demo_rescaleRadioBox.SetStringSelection(self.project['options']['demo_conmat_rescale'])
        self.demo_rescale_edgeRadioBox.SetStringSelection(self.project['options']['demo_conmat_rescale_edge'])

        self.land_HAB_buff.SetValue(self.project['options']['land_hab_buff'])
        self.land_HAB_thresh.SetValue(self.project['options']['land_hab_thresh'])
        self.land_PU_CM_progress.SetValue(self.project['options']['land_pu_cm_progress'])
        for i in range(self.land_type_choice.GetPageCount()):
            if self.land_type_choice.GetPageText(i) == self.project['options']['land_conmat_type']:
                self.land_type_choice.SetSelection(i)
        self.land_res_matrixTypeRadioBox.SetStringSelection(self.project['options']['land_res_matrixType'])

        self.cf_demo_in_degree.SetValue(self.project['options']['demo_metrics']['in_degree'])
        self.cf_demo_out_degree.SetValue(self.project['options']['demo_metrics']['out_degree'])
        self.cf_demo_between_cent.SetValue(self.project['options']['demo_metrics']['between_cent'])
        self.cf_demo_eig_vect_cent.SetValue(self.project['options']['demo_metrics']['eig_vect_cent'])
        self.cf_demo_google.SetValue(self.project['options']['demo_metrics']['google'])
        self.cf_demo_self_recruit.SetValue(self.project['options']['demo_metrics']['self_recruit'])
        self.cf_demo_local_retention.SetValue(self.project['options']['demo_metrics']['local_retention'])
        self.cf_demo_outflow.SetValue(self.project['options']['demo_metrics']['outflow'])
        self.cf_demo_inflow.SetValue(self.project['options']['demo_metrics']['inflow'])
        self.cf_demo_stochasticity.SetValue(self.project['options']['demo_metrics']['stochasticity'])
        self.cf_demo_fa_recipients.SetValue(self.project['options']['demo_metrics']['fa_recipients'])
        self.cf_demo_fa_donors.SetValue(self.project['options']['demo_metrics']['fa_donors'])
        self.cf_demo_aa_recipients.SetValue(self.project['options']['demo_metrics']['aa_recipients'])
        self.cf_demo_aa_donors.SetValue(self.project['options']['demo_metrics']['aa_donors'])

        self.bd_demo_conn_boundary.SetValue(self.project['options']['demo_metrics']['conn_boundary'])

        self.cf_land_in_degree.SetValue(self.project['options']['land_metrics']['in_degree'])
        self.cf_land_out_degree.SetValue(self.project['options']['land_metrics']['out_degree'])
        self.cf_land_between_cent.SetValue(self.project['options']['land_metrics']['between_cent'])
        self.cf_land_eig_vect_cent.SetValue(self.project['options']['land_metrics']['eig_vect_cent'])
        self.cf_land_google.SetValue(self.project['options']['land_metrics']['google'])
        self.cf_land_fa_recipients.SetValue(self.project['options']['land_metrics']['fa_recipients'])
        self.cf_land_fa_donors.SetValue(self.project['options']['land_metrics']['fa_donors'])
        self.cf_land_aa_recipients.SetValue(self.project['options']['land_metrics']['aa_recipients'])
        self.cf_land_aa_donors.SetValue(self.project['options']['land_metrics']['aa_donors'])

        self.bd_land_conn_boundary.SetValue(self.project['options']['land_metrics']['conn_boundary'])

        self.calc_metrics_pu.SetValue(self.project['options']['calc_metrics_pu'])
        self.calc_metrics_cu.SetValue(self.project['options']['calc_metrics_cu'])

        self.cf_export_radioBox.SetStringSelection(self.project['options']['cf_export'])
        self.spec_radio.SetStringSelection(self.project['options']['spec_set'])
        self.targets.SetValue(self.project['options']['targets'])
        self.BD_filecheck.SetValue(self.project['options']['bd_filecheck'])
        self.PUDAT_filecheck.SetValue(self.project['options']['pudat_filecheck'])

        self.NUMREPS.SetValue(self.project['options']['NUMREPS'])
        self.SCENNAME.SetValue(self.project['options']['SCENNAME'])
        self.NUMITNS.SetValue(self.project['options']['NUMITNS'])
        self.marxan_CF.SetStringSelection(self.project['options']['marxan_CF'])
        self.marxan_bound.SetStringSelection(self.project['options']['marxan_bound'])
        self.inputdat_symmRadio.SetStringSelection(self.project['options']['inputdat_boundary'])
        self.on_marxan_bound(event=None)
        self.CSM.SetValue(self.project['options']['CSM'])
        self.marxan_PU.SetStringSelection(self.project['options']['marxan_PU'])
        self.marxanBit_Radio.SetStringSelection(self.project['options']['marxan_bit'])
        self.marxan_Radio.SetStringSelection(self.project['options']['marxan'])


        self.PUSHP_filecheck.SetValue(self.project['options']['pushp_filecheck'])
        self.PUCSV_filecheck.SetValue(self.project['options']['pucsv_filecheck'])
        self.MAP_filecheck.SetValue(self.project['options']['map_filecheck'])

    def set_GUI_filepaths(self):
        # set default file paths
        # spatial input
        self.PU_file.SetPath(self.project['filepaths']['pu_filepath'])
        self.set_GUI_id_selection(self.PU_file_pu_id, self.project['filepaths']['pu_filepath'],
                                  self.project['filepaths']['pu_file_pu_id'])
        self.FA_file.SetPath(self.project['filepaths']['fa_filepath'])
        self.AA_file.SetPath(self.project['filepaths']['aa_filepath'])

        # connectivity input
        self.demo_CU_file.SetPath(self.project['filepaths']['demo_cu_filepath'])
        self.set_GUI_id_selection(self.demo_CU_file_pu_id, self.project['filepaths']['demo_cu_filepath'],
                                  self.project['filepaths']['demo_cu_file_pu_id'])
        self.demo_CU_CM_file.SetPath(self.project['filepaths']['demo_cu_cm_filepath'])
        self.demo_PU_CM_file.SetPath(self.project['filepaths']['demo_pu_cm_filepath'])

        self.land_HAB_file.SetPath(self.project['filepaths']['land_cu_filepath'])
        self.set_GUI_id_selection(self.land_HAB_file_hab_id, self.project['filepaths']['land_cu_filepath'],
                                  self.project['filepaths']['land_cu_file_hab_id'])
        self.land_RES_mat_file.SetPath(self.project['filepaths']['land_res_mat_filepath'])
        self.land_RES_file.SetPath(self.project['filepaths']['land_res_filepath'])
        self.set_GUI_id_selection(self.land_RES_file_res_id, self.project['filepaths']['land_res_filepath'],
                                  self.project['filepaths']['land_res_file_hab_id'])
        self.land_PU_CM_file.SetPath(self.project['filepaths']['land_pu_cm_filepath'])

        self.LP_file.SetPath(self.project['filepaths']['lp_filepath'])

        # Marxan metrics files
        self.orig_CF_file.SetPath(self.project['filepaths']['orig_cf_filepath'])
        self.CF_file.SetPath(self.project['filepaths']['cf_filepath'])
        self.orig_SPEC_file.SetPath(self.project['filepaths']['orig_spec_filepath'])
        self.SPEC_file.SetPath(self.project['filepaths']['spec_filepath'])
        self.orig_BD_file.SetPath(self.project['filepaths']['orig_bd_filepath'])
        self.BD_file.SetPath(self.project['filepaths']['bd_filepath'])
        self.orig_PUDAT_file.SetPath(self.project['filepaths']['orig_pudat_filepath'])
        self.PUDAT_file.SetPath(self.project['filepaths']['pudat_filepath'])

        # Marxan analysis
        self.inputdat_template_file.SetPath(self.project['filepaths']['marxan_template_input'])
        self.inputdat_file.SetPath(self.project['filepaths']['marxan_input'])

        # Post-Hoc
        self.postHoc_file.SetPath(self.project['filepaths']['posthoc'])
        self.postHoc_shp_file.SetPath(self.project['filepaths']['posthoc_shp'])

        # Export plot data
        self.PUSHP_file.SetPath(self.project['filepaths']['pushp'])
        self.PUCSV_file.SetPath(self.project['filepaths']['pucsv'])
        self.MAP_file.SetPath(self.project['filepaths']['map'])

    def set_GUI_id_selection(self,choice,filepath,id):
        if(os.path.isfile(filepath)):
            choice.SetItems(list(gpd.GeoDataFrame.from_file(filepath)))
            choice.SetStringSelection(id)

    def set_metric_options(self):
        self.project['options']['demo_metrics'] = {}
        self.project['options']['demo_metrics']['in_degree'] = self.cf_demo_in_degree.GetValue()
        self.project['options']['demo_metrics']['out_degree'] = self.cf_demo_out_degree.GetValue()
        self.project['options']['demo_metrics']['between_cent'] = self.cf_demo_between_cent.GetValue()
        self.project['options']['demo_metrics']['eig_vect_cent'] = self.cf_demo_eig_vect_cent.GetValue()
        self.project['options']['demo_metrics']['google'] = self.cf_demo_google.GetValue()
        self.project['options']['demo_metrics']['self_recruit'] = self.cf_demo_self_recruit.GetValue()
        self.project['options']['demo_metrics']['local_retention'] = self.cf_demo_local_retention.GetValue()
        self.project['options']['demo_metrics']['outflow'] = self.cf_demo_outflow.GetValue()
        self.project['options']['demo_metrics']['inflow'] = self.cf_demo_inflow.GetValue()
        self.project['options']['demo_metrics']['stochasticity'] = self.cf_demo_stochasticity.GetValue()
        self.project['options']['demo_metrics']['fa_recipients'] = self.cf_demo_fa_recipients.GetValue()
        self.project['options']['demo_metrics']['fa_donors'] = self.cf_demo_fa_donors.GetValue()
        self.project['options']['demo_metrics']['aa_recipients'] = self.cf_demo_aa_recipients.GetValue()
        self.project['options']['demo_metrics']['aa_donors'] = self.cf_demo_aa_donors.GetValue()

        self.project['options']['demo_metrics']['conn_boundary'] = self.bd_demo_conn_boundary.GetValue()
        self.project['options']['demo_metrics']['min_plan_graph'] = self.bd_demo_min_plan_graph.GetValue()

        self.project['options']['land_metrics'] = {}
        self.project['options']['land_metrics']['in_degree'] = self.cf_land_in_degree.GetValue()
        self.project['options']['land_metrics']['out_degree'] = self.cf_land_out_degree.GetValue()
        self.project['options']['land_metrics']['between_cent'] = self.cf_land_between_cent.GetValue()
        self.project['options']['land_metrics']['eig_vect_cent'] = self.cf_land_eig_vect_cent.GetValue()
        self.project['options']['land_metrics']['google'] = self.cf_land_google.GetValue()
        self.project['options']['land_metrics']['fa_recipients'] = self.cf_land_fa_recipients.GetValue()
        self.project['options']['land_metrics']['fa_donors'] = self.cf_land_fa_donors.GetValue()
        self.project['options']['land_metrics']['aa_recipients'] = self.cf_land_aa_recipients.GetValue()
        self.project['options']['land_metrics']['aa_donors'] = self.cf_land_aa_donors.GetValue()

        self.project['options']['land_metrics']['conn_boundary'] = self.bd_land_conn_boundary.GetValue()
        self.project['options']['land_metrics']['min_plan_graph'] = self.bd_land_min_plan_graph.GetValue()

    def on_save_project(self, event):
        """
        save a project, but call 'on_save_project_as' if project file has not previously been defined
        """
        if 'projfile' in self.project['filepaths']:
            self.set_metric_options()
            self.save_project_gui()
        else:
            self.on_save_project_as(event=None)

    def on_save_project_as(self, event):
        """
        Create and show the Open FileDialog to save a project
        """
        dlg = wx.FileDialog(
            self, message="Save file as ...",
            defaultDir=self.workingdirectory,
            defaultFile="", wildcard=wc_MarCon, style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT
        )
        if dlg.ShowModal() == wx.ID_OK:
            self.project['filepaths']['projfile'] = dlg.GetPath()
            self.project['filepaths']['projfilename'] = dlg.GetFilename()
            self.workingdirectory = dlg.GetDirectory()
            os.chdir(self.workingdirectory)
            self.set_metric_options()
            self.save_project_gui()
        dlg.Destroy()
        frame.SetTitle('Marxan Connect (Project: ' + self.project['filepaths']['projfilename'] + ')')

    def save_project_gui(self):
        projfile = self.project['filepaths']['projfile']
        self.project = marxanconpy.marcon.edit_working_directory(self.project,
                                                                              self.workingdirectory,
                                                                              "relative")
        marxanconpy.marcon.save_project(project=self.project,projfile=projfile)
        self.project = marxanconpy.marcon.edit_working_directory(self.project,
                                                                              self.workingdirectory,
                                                                              "absolute")

# ########################## html pop-up functions #####################################################################

    def openhtml(self, html):
        if os.name == 'nt':
            wx.LaunchDefaultBrowser(html)
        else:
            os.system("open " + html)

    def on_glossary(self, event):
        self.openhtml(os.path.join("docs" , "glossary.html"))

    def on_tutorial(self, event):
        self.openhtml(os.path.join("docs" , "tutorial.html"))

    def on_github(self, event):
        self.openhtml("https://github.com/remi-daigle/MarxanConnect/issues")

    def on_contributing(self, event):
        self.openhtml(os.path.join("docs" , "contributing.html"))

    def on_license(self, event):
        with open('LICENSE', 'r', encoding="utf8") as file:
            filedata = file.read()
        dlg = wx.MessageBox(message=filedata,
                            caption="Marxan Connect License",
                            style=wx.OK)

    def on_about(self, event):
        dlg = wx.MessageBox(message="Marxan Connect: " +
                                    MarxanConnectVersion +
                                    "\n Running marxanconpy: " +
                                    marxanconpy.__version__ +
                                    "\n(C) 2019 Remi Daigle\n",
                            caption="About Marxan Connect",
                            style=wx.OK)

    def on_getting_started (self, event):
        # insert getting started tab and hyperlinks (wxFormBuilder can't handle hyperlinks)
        GettingStartedframe = GettingStarted(parent=self)
        GettingStartedframe.Show()

    def on_metric_definition_choice(self,event):
        self.metric_definition_html.LoadURL(os.path.join(os.path.dirname(sys.argv[0]),'docs','glossary_webtex.html#'+
                           self.metric_definition_choice.GetStringSelection().lower().replace(" ", "-")))

# ##########################  map plotting functions ###################################################################
    def on_plot_map_button(self, event):
        """
        Initiates map plotting. Creates a 'Plot' tab, plots the basemap (if desired) and calls 'draw_shapefiles' to plot
         up to 2 other shapefiles
        """
        # warn if no connectivity metrics
        if not 'connectivityMetrics' in self.project:
            marxanconpy.warn_dialog(
                message="No connectivity metrics have been calculated yet, please return to the 'Connectivity "
                        "Metrics' tab to calculate metrics before attempting to plot.")
            return  # end plotting

        # prepare plotting window
        if not hasattr(self, 'plot'):
            self.plot = wx.Panel(self.auinotebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
            for i in range(self.auinotebook.GetPageCount()):
                if self.auinotebook.GetPageText(i) == "7) Plotting Options":
                    self.auinotebook.AddPage(self.plot, u"8) Plot", False, wx.NullBitmap)
                elif self.auinotebook.GetPageText(i) == "8) Plotting Options":
                    self.auinotebook.AddPage(self.plot, u"9) Plot", False, wx.NullBitmap)
        self.plot.figure = plt.figure(figsize=self.plot.GetClientSize()/wx.ScreenDC().GetPPI()[0])


        # load lyr1 shapefile and data
        sf1, colour1, trans1, metric1, lowcol1, hicol1, legend1 = [None for i in range(7)]
        if self.lyr1_plot_check.GetValue():
            if self.lyr1_choice.GetChoiceCtrl().GetStringSelection() == "Colormap of connectivity metrics":
                lowcol1 = self.metric_lowcol.GetColour()
                hicol1 = self.metric_hicol.GetColour()
                trans1 = self.metric_alpha.GetValue() / 100
                legend1 = self.metric_legend.GetCurrentSelection()
                type1 = self.get_plot_type(selection=self.metric_shp_choice.GetStringSelection())
                metric_type1 = self.get_metric_type(selection=self.metric_choice.GetStringSelection(),type=type1)
                if type1 == "pu":
                    metric1 = self.project['connectivityMetrics'][metric_type1]
                else:
                    metric1 = self.project['connectivityMetrics']['spec_' + type1][metric_type1]

            elif self.lyr1_choice.GetChoiceCtrl().GetStringSelection() == "Outline of shapefile":
                colour1 = self.poly_col.GetColour()
                trans1 = self.poly_alpha.GetValue() / 100
                type1 = self.get_plot_type(selection=self.poly_shp_choice.GetStringSelection())

            if type1[-2:] == "pu":
                sf1 = gpd.GeoDataFrame.from_file(self.project['filepaths']['pu_filepath']).to_crs(crs="+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")
            else:
                sf1 = gpd.GeoDataFrame.from_file(self.project['filepaths'][type1 + '_filepath']).to_crs(crs="+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")

            # warn and break if shapefile not the same size as metrics
            if self.lyr1_choice.GetChoiceCtrl().GetStringSelection() == "Colormap of connectivity metrics":
                if not sf1.shape[0] == len(metric1):
                    marxanconpy.warn_dialog(message="The selected shapefile does not have the expected number of rows. There "
                                             "are " + str(len(metric1)) + " rows in the selected metric and " + str(
                        sf1.shape[0]) +
                                             " rows in the shapefile")
                    return

        # load lyr2 shapefile and data
        sf2, colour2, trans2, metric2, lowcol2, hicol2, legend2 = [None for i in range(7)]
        if self.lyr2_plot_check.GetValue():
            if self.lyr2_choice.GetChoiceCtrl().GetStringSelection() == "Colormap of connectivity metrics":
                lowcol2 = self.metric_lowcol1.GetColour()
                hicol2 = self.metric_hicol1.GetColour()
                trans2 = self.metric_alpha1.GetValue() / 100
                legend2 = self.metric_legend1.GetCurrentSelection()
                type2 = self.get_plot_type(selection=self.metric_shp_choice1.GetStringSelection())
                metric_type2 = self.get_metric_type(selection=self.metric_choice1.GetStringSelection(),type=type1)
                if type2 == "pu":
                    metric2 = self.project['connectivityMetrics'][metric_type2]
                else:
                    metric2 = self.project['connectivityMetrics']['spec_' + type2][metric_type2]

            elif self.lyr2_choice.GetChoiceCtrl().GetStringSelection() == "Outline of shapefile":
                colour2 = self.poly_col1.GetColour()
                trans2 = self.poly_alpha1.GetValue() / 100
                type2 = self.get_plot_type(selection=self.poly_shp_choice1.GetStringSelection())

            if type2[-2:] == "pu":
                sf2 = gpd.GeoDataFrame.from_file(self.project['filepaths']['pu_filepath']).to_crs(crs='+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
            else:
                sf2 = gpd.GeoDataFrame.from_file(self.project['filepaths'][type2 + '_filepath']).to_crs(crs='+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')

            # warn and break if shapefile not the same size as metrics
            if self.lyr2_choice.GetChoiceCtrl().GetStringSelection() == "Colormap of connectivity metrics":
                if not sf2.shape[0] == len(metric2):
                    marxanconpy.warn_dialog(message="The selected shapefile does not have the expected number of rows. There "
                                             "are " + str(len(metric2)) + " rows in the selected metric and " + str(
                        sf2.shape[0]) +
                                             " rows in the shapefile")
                    return

        if self.lyr1_plot_check.GetValue() and self.lyr2_plot_check.GetValue():
            gdf_list = [sf1, sf2]
        elif self.lyr1_plot_check.GetValue():
            gdf_list = [sf1]
        elif self.lyr2_plot_check.GetValue():
            gdf_list = [sf2]
        else:
            marxanconpy.warn_dialog(message="No data layers were selected")
            lonmin, lonmax, latmin, latmax = -180, 180, -90, -90

        lonmin, lonmax, latmin, latmax = marxanconpy.spatial.buffer_shp_corners(gdf_list, float(self.bmap_buffer.GetValue()))

        crs = cartopy.crs.PlateCarree(central_longitude=(lonmin+lonmax)/2)
        self.plot.axes = self.plot.figure.gca(projection=crs)
        self.plot.axes.set_extent([lonmin, lonmax, latmin, latmax])
        self.plot.canvas = FigureCanvas(self.plot, -1, self.plot.figure)
        self.plot.sizer = wx.BoxSizer(wx.VERTICAL)
        self.plot.sizer.Add(self.plot.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.plot.SetSizer(self.plot.sizer)
        self.plot.Fit()

        # plot basemap
        if self.bmap_plot_check.GetValue():
            self.plot.axes.add_feature(cartopy.feature.GSHHSFeature(levels=[1,3],
                                                                    facecolor=tuple(c / 255 for c in self.bmap_landcol.GetColour()))
                                       )
            self.plot.axes.add_feature(cartopy.feature.GSHHSFeature(levels=[2],
                                                                    facecolor=tuple(
                                                                        c / 255 for c in self.bmap_lakecol.GetColour()))
                                       )
            self.plot.axes.background_patch.set_facecolor(tuple(c / 255 for c in self.bmap_oceancol.GetColour()))


        # plot first layer
        if self.lyr1_plot_check.GetValue():
            self.draw_shapefiles(sf=sf1,
                                 crs=crs,
                                 colour=colour1,
                                 trans=trans1,
                                 metric=metric1,
                                 lowcol=lowcol1,
                                 hicol=hicol1,
                                 legend=legend1)
        
        # plot second layer
        if self.lyr2_plot_check.GetValue():
            self.draw_shapefiles(sf=sf2,
                                 crs=crs,
                                 colour=colour2,
                                 trans=trans2,
                                 metric=metric2,
                                 lowcol=lowcol2,
                                 hicol=hicol2,
                                 legend=legend2)

        # change selection to plot tab
        for i in range(self.auinotebook.GetPageCount()):
            if self.auinotebook.GetPageText(i) == "8) Plot" or self.auinotebook.GetPageText(i) == "9) Plot":
                self.auinotebook.ChangeSelection(i)

    def draw_shapefiles(self, sf, crs, colour=None, trans=None, metric=None, lowcol=None, hicol=None, legend=None):
        """
        Draws the desired shapefile on the plot created by 'on_plot_map_button'
        """
        if type(metric) == 'Nonetype':
            patches = []
            colour = tuple(c / 255 for c in colour)
            self.plot.axes.add_geometries(sf.geometry.to_crs(crs.proj4_init),
                crs=crs,
                facecolor=colour,
                alpha=trans)
        else:
            patches = []
            # define colormap
            c1 = tuple(c / 255 for c in lowcol)
            c2 = tuple(c / 255 for c in hicol)

            seq = [(None,) * 4, 0.0] + list((c1, c2)) + [1.0, (None,) * 4]
            cdict = {'red': [], 'green': [], 'blue': []}
            for i, item in enumerate(seq):
                if isinstance(item, float):
                    r1, g1, b1, a = seq[i - 1]
                    r2, g2, b2, a = seq[i + 1]
                    cdict['red'].append([item, r1, r2])
                    cdict['green'].append([item, g1, g2])
                    cdict['blue'].append([item, b1, b2])
            cmap = matplotlib.colors.LinearSegmentedColormap('CustomMap', cdict)

            norm = matplotlib.colors.Normalize(min(metric), max(metric))
            bins = numpy.linspace(min(metric), max(metric), 10)
            color_producer = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
            for poly, val in zip(sf.geometry.to_crs(crs.proj4_init), metric):
                rgba = color_producer.to_rgba(val)
                self.plot.axes.add_geometries(list([poly]),
                    crs=crs,
                    facecolor=rgba,
                    alpha=trans)
            
            if legend == 0:
                self.plot.ax_legend = self.plot.figure.add_axes([0.415, 0.8, 0.2, 0.04], zorder=3)
                self.plot.cb = matplotlib.colorbar.ColorbarBase(self.plot.ax_legend,
                                                                cmap=cmap,
                                                                ticks=bins,
                                                                boundaries=bins,
                                                                orientation='horizontal')
                self.plot.cb.ax.set_xticklabels([str("{:.1e}".format(i)) for i in bins],
                                                                rotation = 30,
                                                                ha='right')
            elif legend == 1:
                self.plot.ax_legend = self.plot.figure.add_axes([0.415, 0.2, 0.2, 0.04], zorder=3)
                self.plot.cb = matplotlib.colorbar.ColorbarBase(self.plot.ax_legend,
                                                                cmap=cmap,
                                                                ticks=bins,
                                                                boundaries=bins,
                                                                orientation='horizontal')
                self.plot.cb.ax.set_xticklabels([str("{:.1e}".format(i)) for i in bins],
                                                                rotation = 30,
                                                                ha='right')

    def outline_shapefile_choices(self):
        choices = []
        if self.project['filepaths']['pu_filepath'] != "":
            choices.append("Planning Units")
        if self.project['filepaths']['fa_filepath'] != "":
            choices.append("Focus Areas")
        if self.project['filepaths']['aa_filepath'] != "":
            choices.append("Avoidance Areas")
        if self.project['filepaths']['demo_cu_filepath'] != "":
            if self.demo_rescaleRadioBox.GetStringSelection() != "Identical Grids":
                choices.append("Demographic Units")
        if self.project['filepaths']['land_cu_filepath'] != "":
            choices.append("Landscape Units")

        self.poly_shp_choice.SetItems(choices)
        self.poly_shp_choice.SetSelection(0)
        self.poly_shp_choice1.SetItems(choices)
        self.poly_shp_choice1.SetSelection(0)

    def colormap_shapefile_choices(self):
        choices = []
        if 'connectivityMetrics' in self.project:
            if 'best_solution' in self.project['connectivityMetrics'] or 'status' in self.project['connectivityMetrics']:
                choices.append("Planning Units (Marxan Data)")
            if 'spec_demo_pu' in self.project['connectivityMetrics']:
                choices.append("Planning Units (Demographic Data)")
            if 'spec_land_pu' in self.project['connectivityMetrics']:
                choices.append("Planning Units (Landscape Data)")
            if 'spec_demo_cu' in self.project['connectivityMetrics']:
                choices.append("Demographic Units")

        self.metric_shp_choice.SetItems(choices)
        self.metric_shp_choice.SetSelection(0)
        self.metric_shp_choice1.SetItems(choices)
        self.metric_shp_choice1.SetSelection(0)

        choices = []

        if 'connectivityMetrics' in self.project:
            if 'spec_demo_pu' in self.project['connectivityMetrics']:
                choices.append("Planning Units (Demographic Data)")
            if 'spec_land_pu' in self.project['connectivityMetrics']:
                choices.append("Planning Units (Landscape Data)")
        self.preEval_metric_shp_choice.SetItems(choices)
        self.preEval_metric_shp_choice.SetSelection(0)

    def on_metric_shp_choice(self, event=None):
        self.colormap_metric_choices(1)

    def on_metric_shp_choice1(self, event=None):
        self.colormap_metric_choices(2)

    def colormap_metric_choices(self, lyr):
        choices = []
        if lyr == 1:
            shapefile = self.metric_shp_choice.GetStringSelection()
        elif lyr == 2:
            shapefile = self.metric_shp_choice1.GetStringSelection()
        else:
            shapefile = self.preEval_metric_shp_choice.GetStringSelection()

        if 'connectivityMetrics' in self.project:
            if shapefile == "Planning Units (Marxan Data)":
                if 'best_solution' in self.project['connectivityMetrics']:
                    choices.append("Selection Frequency")
                    choices.append("Best Solution")
                if 'status' in self.project['connectivityMetrics']:
                    choices.append("Status")
            else:
                plot_type = self.get_plot_type(shapefile)
                if 'spec_' + plot_type in self.project['connectivityMetrics']:
                    self.spec_resolve_metric_choice('in_degree_', "In Degree", plot_type, choices)
                    self.spec_resolve_metric_choice('out_degree_', "Out Degree", plot_type, choices)
                    self.spec_resolve_metric_choice('between_cent_', "Betweenness Centrality", plot_type, choices)
                    self.spec_resolve_metric_choice('eig_vect_cent_', "Eigenvector Centrality", plot_type, choices)
                    self.spec_resolve_metric_choice('google_', "Google PageRank", plot_type, choices)
                    self.spec_resolve_metric_choice('self_recruit_', "Self Recruitment", plot_type, choices)
                    self.spec_resolve_metric_choice('outflow_', "Out-Flow", plot_type, choices)
                    self.spec_resolve_metric_choice('inflow_', "In-Flow", plot_type, choices)
                    self.spec_resolve_metric_choice('temp_conn_cov_', "Temporal Connectivity Covariance", plot_type, choices)
                    self.spec_resolve_metric_choice('fa_recipients_', "Focus Area Recipients", plot_type, choices)
                    self.spec_resolve_metric_choice('fa_donors_', "Focus Area Donors", plot_type, choices)
                    self.spec_resolve_metric_choice('aa_recipients_', "Avoidance Area Recipients", plot_type, choices)
                    self.spec_resolve_metric_choice('aa_donors_', "Avoidance Area Donors", plot_type, choices)
        if lyr == 1:
            self.metric_choice.SetItems(choices)
            self.metric_choice.SetSelection(0)
        elif lyr == 2:
            self.metric_choice1.SetItems(choices)
            self.metric_choice1.SetSelection(0)
        else:
            self.preEval_metric_choice.SetItems(choices)
            self.preEval_metric_choice.SetSelection(0)
            if 'connectivityMetrics' in self.project:
                self.on_preEval_metric_choice(event=None)

    def spec_resolve_metric_choice(self, prefix, text = None, type = None, choices=None, gettext = True):
        if gettext:
            for k in self.project['connectivityMetrics']['spec_' + type].keys():
                if k.startswith(prefix+type):
                    if len(k)==len(prefix+type):
                        choices.append(text)
                    else:
                        choices.append(text+' ('+k.replace(prefix+type+'_','')+')')
        else:
            if text.startswith(type):
                if len(type) == len(text):
                    return str(prefix)
                else:
                    return str(prefix+'_'+str.replace(text,type+' (','')[:-1])

    def on_plot_export_button( self, event ):
        self.temp = {}
        self.temp['pu'] = self.spatial['pu_shp'].to_crs("+proj=longlat +datum=WGS84")
        if 'spec_demo_pu' in self.project['connectivityMetrics']:
            self.temp['pu'] = pandas.concat(
                [self.temp['pu'], pandas.DataFrame.from_dict(self.project['connectivityMetrics']['spec_demo_pu'])],
                axis=1)
        if 'spec_land_pu' in self.project['connectivityMetrics']:
            self.temp['pu'] = pandas.concat(
                [self.temp['pu'], pandas.DataFrame.from_dict(self.project['connectivityMetrics']['spec_land_pu'])],
                axis=1)
        if 'best_solution' in self.project['connectivityMetrics']:
            self.temp['pu'] = pandas.concat([self.temp['pu'], pandas.DataFrame.from_dict(
                {'best_solution': self.project['connectivityMetrics']['best_solution'],
                 'select_freq': self.project['connectivityMetrics']['select_freq']})],
                                            axis=1)
        if 'status' in self.project['connectivityMetrics']:
            self.temp['pu'] = pandas.concat([self.temp['pu'], pandas.DataFrame.from_dict(
                {'status': self.project['connectivityMetrics']['status']})],
                                            axis=1)

        if self.PUSHP_filecheck.GetValue():
            self.temp['pu'].to_file(self.project['filepaths']['pushp'])
        if self.PUCSV_filecheck.GetValue():
            self.temp['pu'].to_csv(self.project['filepaths']['pucsv'])
        if self.MAP_filecheck.GetValue():
            self.plot.figure.savefig(self.project['filepaths']['map'])

    def get_plot_type(self, selection):
        if selection == "Planning Units":
            type = 'pu'
        elif selection == "Planning Units (Marxan Results)":
            type = 'pu'
        elif selection == "Planning Units (Demographic Data)":
            type = 'demo_pu'
        elif selection == "Planning Units (Landscape Data)":
            type = 'land_pu'
        elif selection == "Demographic Units":
            type = 'demo_cu'
        elif selection == "Landscape Units":
            type = 'land_cu'
        elif selection == "Focus Areas":
            type = 'fa'
        elif selection == "Avoidance Areas":
            type = 'aa'
        else:
            type = 'pu'
        return type

    def get_metric_type(self, selection, type):

        metric_type = None

        metric_type = self.spec_resolve_metric_choice('select_freq', selection, "Selection Frequency", type,
                                                      gettext=False)
        metric_type = self.spec_resolve_metric_choice('best_solution', selection, "Best Solution", type,
                                                      gettext=False) or metric_type
        metric_type = self.spec_resolve_metric_choice('status', selection, "Status", type,
                                                      gettext=False) or metric_type
        metric_type = self.spec_resolve_metric_choice('in_degree_' + type, selection, "In Degree", type,
                                                      gettext=False) or metric_type
        metric_type = self.spec_resolve_metric_choice('out_degree_' + type, selection, "Out Degree", type,
                                                      gettext=False) or metric_type
        metric_type = self.spec_resolve_metric_choice('between_cent_' + type, selection, "Betweenness Centrality", type,
                                                      gettext=False) or metric_type
        metric_type = self.spec_resolve_metric_choice('eig_vect_cent_' + type, selection, "Eigenvector Centrality", type,
                                                      gettext=False) or metric_type
        metric_type = self.spec_resolve_metric_choice('google_' + type, selection, "Google PageRank", type,
                                                      gettext=False) or metric_type
        metric_type = self.spec_resolve_metric_choice('self_recruit_' + type, selection, "Self Recruitment", type,
                                                      gettext=False) or metric_type
        metric_type = self.spec_resolve_metric_choice('local_retention_' + type, selection, "Local Retention", type,
                                                      gettext=False) or metric_type
        metric_type = self.spec_resolve_metric_choice('outflow_' + type, selection, "Out-Flow", type,
                                                      gettext=False) or metric_type
        metric_type = self.spec_resolve_metric_choice('inflow_' + type, selection, "In-Flow", type,
                                                      gettext=False) or metric_type
        metric_type = self.spec_resolve_metric_choice('temp_conn_cov_' + type, selection, "Temporal Connectivity Covariance", type,
                                                      gettext=False) or metric_type
        metric_type = self.spec_resolve_metric_choice('fa_recipients_' + type, selection, "Focus Area Recipients", type,
                                                      gettext=False) or metric_type
        metric_type = self.spec_resolve_metric_choice('fa_donors_' + type, selection, "Focus Area Donors", type,
                                                      gettext=False) or metric_type
        metric_type = self.spec_resolve_metric_choice('aa_recipients_' + type, selection, "Avoidance Area Recipients", type,
                                                      gettext=False) or metric_type
        metric_type = self.spec_resolve_metric_choice('aa_donors_' + type, selection, "Avoidance Area Donors", type,
                                                      gettext=False) or metric_type
        return metric_type

# ###########################  file management functions ###############################################################
    def on_PU_file(self, event):
        """
        Defines Planning Unit file path
        """
        self.temp = {}
        self.project['filepaths']['pu_filepath'] = self.PU_file.GetPath()
        if os.path.isfile(self.project['filepaths']['pu_filepath']):
            self.spatial['pu_shp'] = gpd.GeoDataFrame.from_file(self.project['filepaths']['pu_filepath']).to_crs('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
            self.spatial['pu_proj'] = marxanconpy.spatial.get_appropriate_projection(self.spatial['pu_shp'], 'area')
            self.spatial['pu_shp'] = self.spatial['pu_shp'].to_crs(self.spatial['pu_proj'])
            self.temp['items'] = list(gpd.GeoDataFrame.from_file(self.project['filepaths']['pu_filepath']))
            self.PU_file_pu_id.SetItems(self.temp['items'])
            if self.project['filepaths']['pu_file_pu_id'] in self.temp['items']:
                self.PU_file_pu_id.SetStringSelection(self.project['filepaths']['pu_file_pu_id'])
            else:
                self.PU_file_pu_id.SetSelection(0)
        self.on_PU_file_pu_id(event=None)
        self.outline_shapefile_choices()
        self.colormap_shapefile_choices()
        self.on_FA_file(event=None)
        self.on_AA_file(event=None)

    def on_PU_file_pu_id(self, event):
        """
        Defines ID column label for the Planning Unit file
        """
        self.project['filepaths']['pu_file_pu_id'] = self.PU_file_pu_id.GetStringSelection()

    def on_FA_file(self, event):
        """
        Defines Focus Areas file path
        """
        self.project['filepaths']['fa_filepath'] = self.FA_file.GetPath()
        if os.path.isfile(self.project['filepaths']['fa_filepath']):
            if 'pu_shp' in self.spatial:
                self.spatial['fa_shp'] = gpd.GeoDataFrame.from_file(self.project['filepaths']['fa_filepath']).to_crs(self.spatial['pu_proj'])
                self.spatial['fa_shp']['diss'] = 1
                self.spatial['fa_shp'] = self.spatial['fa_shp'].dissolve(by='diss')
                self.spatial['pu_shp']['fa_included'] = 0
                for index, purow in self.spatial['pu_shp'].iterrows():
                    self.spatial['pu_shp'].loc[index,'fa_included'] = self.spatial[
                        'fa_shp'].geometry.intersects(purow.geometry).bool()
        # enable metrics
        self.lock_pudat(self.project['filepaths']['orig_pudat_filepath'])
        self.enable_metrics()

    def on_AA_file(self, event):
        """
        Defines Avoidance Areas file path
        """
        self.project['filepaths']['aa_filepath'] = self.AA_file.GetPath()
        if os.path.isfile(self.project['filepaths']['aa_filepath']):
            if 'pu_shp' in self.spatial:
                self.spatial['aa_shp'] = gpd.GeoDataFrame.from_file(self.project['filepaths']['aa_filepath']).to_crs(self.spatial['pu_proj'])
                self.spatial['aa_shp']['diss'] = 1
                self.spatial['aa_shp'] = self.spatial['aa_shp'].dissolve(by='diss')
                self.spatial['pu_shp']['aa_included'] = 0
                for index, purow in self.spatial['pu_shp'].iterrows():
                    self.spatial['pu_shp'].loc[index,'aa_included'] = self.spatial['aa_shp'].geometry.intersects(purow.geometry).bool()
        # enable metrics
        self.lock_pudat(self.project['filepaths']['orig_pudat_filepath'])
        self.enable_metrics()


    def on_demo_CU_file(self, event):
        """
        Defines Connectivity Unit file path
        """
        self.temp = {}
        self.project['filepaths']['demo_cu_filepath'] = self.demo_CU_file.GetPath()
        self.temp['items'] = list(gpd.GeoDataFrame.from_file(self.project['filepaths']['demo_cu_filepath']))
        self.demo_CU_file_pu_id.SetItems(self.temp['items'])
        if self.project['filepaths']['demo_cu_file_pu_id'] in self.temp['items']:
            self.demo_CU_file_pu_id.SetStringSelection(self.project['filepaths']['demo_cu_file_pu_id'])
        else:
            self.demo_CU_file_pu_id.SetSelection(0)
        self.on_demo_CU_file_pu_id(event=None)
        self.outline_shapefile_choices()
        self.colormap_shapefile_choices()

    def on_demo_CU_file_pu_id(self, event):
        """
        Defines ID column label for the demographic connectivity unit file
        """
        self.project['filepaths']['demo_cu_file_pu_id'] = self.demo_CU_file_pu_id.GetStringSelection()

    def on_demo_CU_CM_file(self, event):
        """
        Defines demographic Connectivity Matrix file path
        """
        self.project['filepaths']['demo_cu_cm_filepath'] = self.demo_CU_CM_file.GetPath()

        # reset filepaths
        self.on_demo_rescaleRadioBox(event=None)

        # check format
        self.check_matrix_list_format(format=self.demo_matrixFormatRadioBox.GetStringSelection(),
                                      filepath=self.demo_CU_CM_file.GetPath())

    def on_demo_PU_CM_file(self, event):
        """
        Defines Planning Unit scaled demographic Connectivity Matrix file path
        """
        self.project['filepaths']['demo_pu_cm_filepath'] = self.demo_PU_CM_file.GetPath()
        # enable metrics
        self.enable_metrics()
        self.enable_postHoc()

    def on_land_HAB_file(self, event):
        """
        Defines landscape habitat type file path
        """
        self.temp = {}
        self.project['filepaths']['land_cu_filepath'] = self.land_HAB_file.GetPath()
        self.temp['items'] = list(gpd.GeoDataFrame.from_file(self.project['filepaths']['land_cu_filepath']))
        self.land_HAB_file_hab_id.SetItems(self.temp['items'])
        if self.project['filepaths']['land_cu_file_hab_id'] in self.temp['items']:
            self.land_HAB_file_hab_id.SetStringSelection(self.project['filepaths']['land_cu_file_hab_id'])
        else:
            self.land_HAB_file_hab_id.SetSelection(0)
        self.on_land_HAB_file_hab_id(event=None)
        self.outline_shapefile_choices()
        self.colormap_shapefile_choices()

    def on_land_HAB_file_hab_id(self, event):
        """
        Defines landscape Connectivity Unit file path
        """
        self.project['filepaths']['land_cu_file_hab_id'] = self.land_HAB_file_hab_id.GetStringSelection()

    def on_land_RES_mat_file(self, event):
        """
        Defines landscape habitat resistance matrix file path
        """
        self.project['filepaths']['land_res_mat_filepath'] = self.land_RES_mat_file.GetPath()

    def on_land_RES_file(self, event):
        """
        Defines landscape resistance surface file path
        """
        self.temp = {}
        self.project['filepaths']['land_res_filepath'] = self.land_RES_file.GetPath()
        self.temp['items'] = list(gpd.GeoDataFrame.from_file(self.project['filepaths']['land_res_file_hab_id']))
        self.land_RES_file_res_id.SetItems(self.temp['items'])
        if self.project['filepaths']['land_res_file_hab_id'] in self.temp['items']:
            self.land_RES_file_res_id.SetStringSelection(self.project['filepaths']['land_res_file_hab_id'])
        else:
            self.land_RES_file_res_id.SetSelection(0)

        self.land_RES_file_res_id.SetItems(
            list(gpd.GeoDataFrame.from_file(self.project['filepaths']['land_res_filepath'])))
        self.land_RES_file_res_id.SetSelection(0)
        self.on_land_RES_file_hab_id(event=None)
        self.outline_shapefile_choices()
        self.colormap_shapefile_choices()

    def on_land_RES_file_hab_id(self, event):
        """
        Defines landscape Connectivity Unit file path
        """
        self.project['filepaths']['land_res_file_hab_id'] = self.land_RES_file_res_id.GetStringSelection()

    def on_land_CU_CM_file(self, event):
        """
        Defines landscape Connectivity Matrix file path
        """
        self.project['filepaths']['land_cu_cm_filepath'] = self.land_CU_CM_file.GetPath()

        # reset filepaths
        self.on_land_rescaleRadioBox(event=None)

        # # check format
        # self.check_matrix_list_format(format=self.land_matrixFormatRadioBox.GetStringSelection(),
        #                               filepath=self.land_CU_CM_file.GetPath())

    def on_land_PU_CM_file(self, event):
        """
        Defines landscape Planning Unit scaled Connectivity Matrix file path
        """
        self.project['filepaths']['land_pu_cm_filepath'] = self.land_PU_CM_file.GetPath()
        # enable metrics
        self.enable_metrics()
        self.enable_postHoc()

    def on_LP_file(self, event):
        self.project['filepaths']['lp_filepath'] = self.LP_file.GetPath()
        self.enable_metrics()


    def on_CF_file(self, event):
        """
        Defines conservation features (i.e. puvspr2.dat) file path
        """
        self.project['filepaths']['cf_filepath'] = self.CF_file.GetPath()

    def on_orig_CF_file(self, event):
        """
        Defines conservation features (i.e. puvspr2.dat) file path
        """
        self.project['filepaths']['orig_cf_filepath'] = self.orig_CF_file.GetPath()

    def on_SPEC_file(self, event):
        """
        Defines spec.dat file path
        """
        self.project['filepaths']['spec_filepath'] = self.SPEC_file.GetPath()

    def on_orig_SPEC_file(self, event):
        """
        Defines spec.dat file path
        """
        self.project['filepaths']['orig_spec_filepath'] = self.orig_SPEC_file.GetPath()

    def on_BD_file(self, event):
        """
        Defines boundary definition file path
        """
        self.project['filepaths']['bd_filepath'] = self.BD_file.GetPath()

    def on_orig_BD_file(self, event):
        """
        Defines boundary definition file path
        """
        self.project['filepaths']['orig_bd_filepath'] = self.orig_BD_file.GetPath()

    def on_PUDAT_file(self, event):
        """
        Defines planning unit data file path
        """
        self.project['filepaths']['pudat_filepath'] = self.PUDAT_file.GetPath()

    def on_orig_PUDAT_file(self, event):
        """
        Defines planning unit data file path
        """
        self.project['filepaths']['orig_pudat_filepath'] = self.orig_PUDAT_file.GetPath()
        self.lock_pudat(self.project['filepaths']['orig_pudat_filepath'])


    def on_inputdat_file(self, event):
        """
        Defines the input file for Marxan
        """
        self.project['filepaths']['marxan_input'] = self.inputdat_file.GetPath()
        self.enable_postHoc()
        self.load_marxan_output()


    def on_inputdat_template_file(self, event):
        """
        Defines the template input file for before input file creation
        """
        self.project['filepaths']['marxan_template_input'] = self.inputdat_template_file.GetPath()


    def on_PUSHP_file( self, event ):
        """
        Defines planning unit (with metrics) export shapefile file path
        """
        self.project['filepaths']['pushp'] = self.PUSHP_file.GetPath()

    def on_PUCSV_file( self, event ):
        """
        Defines planning unit (with metrics) export csv file path
        """
        self.project['filepaths']['pucsv'] = self.PUCSV_file.GetPath()

    def on_MAP_file( self, event ):
        """
        Defines map image file path
        """
        self.project['filepaths']['map'] = self.MAP_file.GetPath()

# ###########################  option setting functions ################################################################

    def on_fa_status_radioBox(self, event):
        self.project['options']['fa_status'] = self.fa_status_radioBox.GetStringSelection()
        self.lock_pudat(self.project['filepaths']['orig_pudat_filepath'])

    def on_aa_status_radioBox(self, event):
        self.project['options']['aa_status'] = self.aa_status_radioBox.GetStringSelection()
        self.lock_pudat(self.project['filepaths']['orig_pudat_filepath'])

    def on_demo_matrixTypeRadioBox(self, event):
        self.project['options']['demo_conmat_type'] = self.demo_matrixTypeRadioBox.GetStringSelection()
        self.enable_metrics()

    def on_demo_matrixFormatRadioBox(self, event):
        self.project['options']['demo_conmat_format'] = self.demo_matrixFormatRadioBox.GetStringSelection()
        self.enable_metrics()

    def on_demo_rescaleRadioBox(self, event):
        """
        Hides unnecessary options if rescaling is not necessary
        """
        # hide or unhide
        self.project['options']['demo_conmat_rescale'] = self.demo_rescaleRadioBox.GetStringSelection()
        if self.demo_rescaleRadioBox.GetStringSelection() == "Identical Grids":
            enable = False
        else:
            enable = True

        self.demo_rescale_edgeRadioBox.Enable(enable)
        self.demo_CU_filetext.Enable(enable)
        self.demo_CU_file_pu_id.Enable(enable)
        self.demo_CU_file_pu_id_txt.Enable(enable)
        self.demo_CU_file.Enable(enable)
        self.demo_PU_CM_outputtext.Enable(enable)
        self.demo_PU_CM_def.Enable(enable)
        self.demo_PU_CM_progress.Enable(enable)
        self.demo_PU_CM_filetext.Enable(enable)
        self.demo_PU_CM_file.Enable(enable)
        self.demo_rescale_button.Enable(enable)

        # reset filepaths
        # connectivity units planning unit matrix
        if self.demo_rescaleRadioBox.GetStringSelection() == "Identical Grids":
            self.project['filepaths']['demo_pu_cm_filepath'] = self.demo_CU_CM_file.GetPath()
            self.demo_PU_CM_file.SetPath(self.project['filepaths']['demo_pu_cm_filepath'])
            self.project['filepaths']['demo_cu_filepath'] = self.PU_file.GetPath()
            self.demo_CU_file.SetPath(self.project['filepaths']['demo_cu_filepath'])
        else:
            self.project['filepaths']['demo_pu_cm_filepath'] = self.demo_PU_CM_file.GetPath()
            self.project['filepaths']['demo_cu_filepath'] = self.demo_CU_file.GetPath()

        # enable metrics
        self.enable_metrics()

    def on_demo_rescale_edgeRadioBox(self, event):
        self.project['options']['demo_conmat_rescale_edge'] = self.demo_rescale_edgeRadioBox.GetStringSelection()

    def on_land_type_choice(self, event):
        """
        Hides unnecessary options if rescaling is not necessary
        """
        # hide or unhide
        self.project['options']['land_conmat_type'] = self.land_type_choice.GetPageText(self.land_type_choice.GetSelection())
        if self.project['options']['land_conmat_type'] == "Resistance Surface":
            enable_hab = False
            enable_surface = True
            marxanconpy.warn_dialog(message="This feature is not yet operational, please check back in the next version!")
        elif self.project['options']['land_conmat_type'] == "Connectivity Edge List with Habitat":
            enable_hab = False
            enable_surface = False
        elif self.project['options']['land_conmat_type'] == "Habitat Type + Isolation":
            enable_hab = True
            enable_surface = False

        self.land_HAB_filetext.Enable(enable_hab)
        self.land_HAB_file.Enable(enable_hab)
        self.land_HAB_file_hab_id_txt.Enable(enable_hab)
        self.land_HAB_file_hab_id.Enable(enable_hab)
        self.land_RES_mat_filetext.Enable(enable_hab)
        self.land_RES_mat_file.Enable(enable_hab)
        self.resistance_mat_customize.Enable(enable_hab)
        self.land_HAB_buff.Enable(enable_hab)
        self.land_HAB_buff_txt.Enable(enable_hab)
        self.land_HAB_thresh.Enable(enable_hab)
        self.land_HAB_thresh_txt.Enable(enable_hab)
        self.land_res_matrixTypeRadioBox.Enable(enable_hab)

        self.land_RES_filetext.Enable(enable_surface)
        self.land_RES_file.Enable(enable_surface)
        self.land_RES_def.Enable(enable_surface)
        self.land_res_file_res_id_txt.Enable(enable_surface)
        self.land_RES_file_res_id.Enable(enable_surface)
        self.land_generate_button.Enable(enable_surface or enable_hab)
        self.land_PU_CM_progress.Enable(enable_surface or enable_hab)

        # enable metrics
        self.enable_metrics()

    def on_land_res_matrixTypeRadioBox(self, event):
        self.project['options']['land_res_matrixType'] = self.land_res_matrixTypeRadioBox.GetStringSelection()
        if self.project['options']['land_res_matrixType'] == "Least-Cost Path":
            enable_hab = False
        elif self.project['options']['land_res_matrixType'] == "Euclidean Distance":
            enable_hab = False
        self.land_RES_mat_filetext.Enable(enable_hab)
        self.land_RES_mat_file.Enable(enable_hab)
        self.resistance_mat_customize.Enable(enable_hab)

    def on_land_HAB_buff(self, event):
        """
        Defines landscape type connectivity buffer (i.e. the distance between neighbouring planning units at which they
        will be connected for the least cost path analysis.)
        """
        self.project['options']['land_hab_buff'] = self.land_HAB_buff.GetValue()

    def on_land_HAB_thresh(self, event):
        """
        Threshold under which habitat connectivity values is considered null. Ranges from 0 to 1. Without a threshold,
         values for in/out degrees, and betweenness centrality will be homogeneous throughout each habitat type.
        """
        self.project['options']['land_hab_thresh'] = self.land_HAB_thresh.GetValue()

    def on_demo_PU_CM_progress(self, event):
        """
        Checks if the planning unit connectivity matrix progress bar should be activated. (It freezes up the GUI)
        """
        self.project['options']['demo_pu_cm_progress'] = self.demo_PU_CM_progress.GetValue()

    def on_BD_filecheck(self, event):
        """
        Option to export boundary.dat
        """
        self.project['options']['bd_filecheck'] = self.BD_filecheck.GetValue()

    def on_PUDAT_filecheck(self, event):
        """
        Option to export pu.dat
        """
        self.project['options']['pudat_filecheck'] = self.PUDAT_filecheck.GetValue()

    def on_debug_mode(self, event):
        """
        Shows/Hides the debug window.
        """
        if self.log.IsShown():
            self.log.Hide()
        else:
            self.log.Show()
        return

    def enable_metrics(self):
        if self.project['filepaths']['demo_pu_cm_filepath'] != "":
            demo_enable = True
            if self.project['filepaths']['fa_filepath'] != "":
                demo_fa_enable = True
                if self.demo_matrixFormatRadioBox.GetStringSelection() == "Edge List with Time":
                    demo_fa_time_enable = True
                else:
                    demo_fa_time_enable = False
            else:
                demo_fa_enable = False
                demo_fa_time_enable = False

            if self.demo_matrixTypeRadioBox.GetStringSelection() == "Probability":
                demo_prob_enable = True
            else:
                demo_prob_enable = False
            if self.demo_matrixTypeRadioBox.GetStringSelection() == "Migration":
                demo_mig_enable = True
            else:
                demo_mig_enable = False
            if self.demo_matrixTypeRadioBox.GetStringSelection() == "Flow":
                demo_ind_enable = True
            else:
                demo_ind_enable = False
            if self.project['filepaths']['aa_filepath'] != "":
                demo_aa_enable = True
            else:
                demo_aa_enable = False

            if self.project['filepaths']['lp_filepath'] != "":
                lp_enable = True
            else:
                lp_enable = False

        else:
            demo_enable = False
            demo_fa_enable = False
            demo_fa_time_enable = False
            demo_prob_enable = False
            demo_mig_enable = False
            demo_ind_enable = False
            demo_aa_enable = False
            lp_enable = False


        if self.project['filepaths']['land_pu_cm_filepath'] != "":
            land_enable = True
            if self.project['filepaths']['fa_filepath'] != "":
                land_fa_enable = True
            else:
                land_fa_enable = False

            if self.project['filepaths']['aa_filepath'] != "":
                land_aa_enable = True
            else:
                land_aa_enable = False

        else:
            land_enable = False
            land_fa_enable = False
            land_aa_enable = False

        self.cf_demo_in_degree.Enable(enable=demo_enable)
        self.cf_demo_out_degree.Enable(enable=demo_enable)
        self.cf_demo_between_cent.Enable(enable=demo_enable)
        self.cf_demo_eig_vect_cent.Enable(enable=demo_mig_enable or demo_ind_enable or lp_enable)
        self.cf_demo_google.Enable(enable=demo_enable)
        self.cf_demo_self_recruit.Enable(enable=demo_mig_enable or demo_ind_enable or lp_enable)
        self.cf_demo_local_retention.Enable(enable=demo_prob_enable or demo_ind_enable)
        self.cf_demo_outflow.Enable(enable=demo_ind_enable or lp_enable and demo_prob_enable)
        self.cf_demo_inflow.Enable(enable=demo_ind_enable or lp_enable and demo_prob_enable)
        self.cf_demo_stochasticity.Enable(enable=demo_fa_time_enable)
        self.cf_demo_fa_recipients.Enable(enable=demo_fa_enable and (demo_ind_enable or demo_mig_enable or lp_enable))
        self.cf_demo_fa_donors.Enable(enable=demo_fa_enable and (demo_ind_enable or lp_enable and not demo_mig_enable))
        self.cf_demo_aa_recipients.Enable(enable=demo_aa_enable and (demo_ind_enable or demo_mig_enable or lp_enable))
        self.cf_demo_aa_donors.Enable(enable=demo_aa_enable and (demo_ind_enable or lp_enable and not demo_mig_enable))


        self.bd_demo_conn_boundary.Enable(enable=demo_enable)
        self.bd_demo_min_plan_graph.Enable(enable=demo_enable)

        self.cf_land_in_degree.Enable(enable=land_enable)
        self.cf_land_out_degree.Enable(enable=land_enable)
        self.cf_land_between_cent.Enable(enable=land_enable)
        self.cf_land_eig_vect_cent.Enable(enable=land_enable)
        self.cf_land_google.Enable(enable=land_enable)
        self.cf_land_fa_recipients.Enable(enable=land_fa_enable)
        self.cf_land_fa_donors.Enable(enable=land_fa_enable)
        self.cf_land_aa_recipients.Enable(enable=land_aa_enable)
        self.cf_land_aa_donors.Enable(enable=land_aa_enable)

        self.bd_land_conn_boundary.Enable(enable=land_enable)
        self.bd_land_min_plan_graph.Enable(enable=land_enable)
        self.enable_calc_metrics()

    def enable_calc_metrics(self, event=None):
        self.set_metric_options()
        if any(self.project['options']['land_metrics'].values()) or any(self.project['options']['demo_metrics'].values()):
            self.calc_metrics.Enable(True)
        else:
            self.calc_metrics.Enable(False)

    def on_bd_land_conn_boundary(self, event):
        self.enable_calc_metrics()
        if self.bd_land_conn_boundary.GetValue():
            self.bd_demo_conn_boundary.SetValue(False)

    def on_bd_demo_conn_boundary(self, event):
        self.enable_calc_metrics()
        if self.bd_demo_conn_boundary.GetValue():
            self.bd_land_conn_boundary.SetValue(False)

    def on_NUMREPS( self, event ):
        """
        define NUMREPS
        :param event:
        :return:
        """
        self.project['options']['NUMREPS'] = self.NUMREPS.GetValue()

    def on_SCENNAME( self, event ):
        """
        define SCENNAME
        :param event:
        :return:
        """
        self.project['options']['SCENNAME'] = self.SCENNAME.GetValue()

    def on_NUMITNS( self, event ):
        """
        define NUMITNS
        :param event:
        :return:
        """
        self.project['options']['NUMITNS'] = self.NUMITNS.GetValue()

    def on_marxan_CF( self, event ):
        """
        define whether to use original or new conservation features in Marxan
        :param event:
        :return:
        """
        self.project['options']['marxan_CF'] = self.marxan_CF.GetStringSelection()

    def on_marxan_bound( self, event ):
        """
        define whether to use original or new spatial dependencies in Marxan
        :param event:
        :return:
        """
        self.project['options']['marxan_bound'] = self.marxan_bound.GetStringSelection()
        if not self.marxan_bound.GetStringSelection() == 'New':
            self.inputdat_symmRadio.Enable(False)
            self.csm_txt.SetLabel('Boundary Length Modifier')
            if self.marxan_bound.GetStringSelection() == 'None':
                self.CSM.Enable(False)
        else:
            self.inputdat_symmRadio.Enable(True)
            self.CSM.Enable(True)
            self.csm_txt.SetLabel('Connectivity Strength Modifier')

    def on_CSM( self, event ):
        """
        define CSM
        :param event:
        :return:
        """
        self.project['options']['CSM'] = self.CSM.GetValue()

    def on_marxan_PU( self, event ):
        """
        define whether to use original or new planning unit (status) file in Marxan
        :param event:
        :return:
        """
        self.project['options']['marxan_PU'] = self.marxan_PU.GetStringSelection()

    def on_marxanBit_Radio( self, event ):
        """
        Option for Marxan bit version
        """
        self.project['options']['marxan_bit'] = self.marxanBit_Radio.GetStringSelection()

    def on_marxan_Radio( self, event ):
        """
        Option for Marxan version
        """
        self.project['options']['marxan'] = self.marxan_Radio.GetStringSelection()
        if self.project['options']['marxan'] == "Marxan":
            if not os.path.isfile(os.path.join(MCPATH, 'Marxan243',"Marxan.exe")) or\
                    not os.path.isfile(os.path.join(MCPATH, 'Marxan243',"Marxan_x64.exe")):
                marxanconpy.warn_dialog(message="Marxan executables (Marxan.exe or Marxan_x64.exe) not found in Marxan Directory")
        else:
            if not os.path.isfile(os.path.join(MCPATH, 'Marxan243', "MarZone.exe")) or \
                    not os.path.isfile(os.path.join(MCPATH, 'Marxan243', "MarZone_x64.exe")):
                marxanconpy.warn_dialog(message="Marxan executables (MarZone.exe or MarZone_x64.exe) not found in Marxan Directory")

    def on_inputdat_symmRadio(self, event):
        self.project['options']['inputdat_boundary'] = self.inputdat_symmRadio.GetStringSelection()

    def on_cf_export_radioBox( self, event ):
        self.project['options']['cf_export'] = self.cf_export_radioBox.GetStringSelection()

    def on_spec_radio( self, event ):
        self.project['options']['spec_set'] = self.spec_radio.GetStringSelection()
        self.targets_txt.SetLabel(self.project['options']['spec_set']+'s')

    def on_targets( self, event ):
        self.project['options']['targets'] = self.targets.GetValue()
        self.on_new_spec()

    def on_PUSHP_filecheck(self, event):
        """
        Option to export pu.shp
        """
        self.project['options']['pushp_filecheck'] = self.PUSHP_filecheck.GetValue()

    def on_PUCSV_filecheck(self, event):
        """
        Option to export pu.csv
        """
        self.project['options']['pucsv_filecheck'] = self.PUCSV_filecheck.GetValue()

    def on_MAP_filecheck(self, event):
        """
        Option to export pu.png
        """
        self.project['options']['map_filecheck'] = self.PUSHP_filecheck.GetValue()

# ########################## rescaling and matrix generation ###########################################################
    def on_demo_rescale_button(self, event):
        """
        Rescales the connectivity matrix to match the scale of the planning units
        """
        try:
            marxanconpy.warn_dialog(message="Rescaling of matrices is offered as a convenience function. It it up to the user to determine"
                             " if the rescaling is ecologically valid. We recommend acquiring connectivity data at the same"
                             " scale as the planning unit")

            self.check_matrix_list_format(format=self.demo_matrixFormatRadioBox.GetStringSelection(),
                                          filepath=self.project['filepaths']['demo_cu_cm_filepath'])
            self.temp = {}
            # create dict entry for connectivityMetrics

            if 'connectivityMetrics' not in self.project:

                self.project['connectivityMetrics'] = {}

            self.temp['demo_pu_conmat'] = marxanconpy.spatial.rescale_matrix(
                self.project['filepaths']['pu_filepath'],
                self.project['filepaths']['pu_file_pu_id'],
                self.project['filepaths']['demo_cu_filepath'],
                self.project['filepaths']['demo_cu_file_pu_id'],
                self.project['filepaths']['demo_cu_cm_filepath'],
                matrixformat=self.project['options']['demo_conmat_format'],
                edge=self.project['options']['demo_conmat_rescale_edge'],
                progressbar=self.project['options']['demo_pu_cm_progress'])

            if self.demo_matrixFormatRadioBox.GetStringSelection() == "Edge List with Time":
                self.temp['demo_pu_conmat_time'] = self.temp['demo_pu_conmat'][
                    self.temp['demo_pu_conmat']['time'] != 'mean'].copy().melt(id_vars=['time', 'id1'],
                                                                               var_name='id2',
                                                                               value_name='value').to_json(
                    orient='split')
                self.temp['demo_pu_conmat'] = self.temp['demo_pu_conmat'][
                    self.temp['demo_pu_conmat']['time'] == 'mean'].drop(['id1', 'time'], axis=1).to_json(
                    orient='split')
                pandas.read_json(self.temp['demo_pu_conmat_time'],
                                 orient='split').to_csv(
                    self.project['filepaths']['demo_pu_cm_filepath'],
                    index=False, header=True, sep=",")
                pandas.read_json(self.temp['demo_pu_conmat'], orient='split').to_csv(
                    str.replace(self.project['filepaths']['demo_pu_cm_filepath'], '.csv',
                                '_mean_of_times.csv'),
                    index=True, header=True, sep=",")

            else:
                self.temp['demo_pu_conmat'] = self.temp['demo_pu_conmat'].to_json(orient='split')
                pandas.read_json(self.temp['demo_pu_conmat'],
                                 orient='split').to_csv(
                    self.project['filepaths']['demo_pu_cm_filepath'], index=True, header=True, sep=",")
        except:
            self.log.Show()
            raise

    def on_land_generate_button(self, event):
        try:
            self.temp = {}
            self.temp['land_pu_conmat'] = marxanconpy.spatial.habitatresistance2conmats(
                buff=float(self.project['options']['land_hab_buff']),
                hab_filepath=self.project['filepaths']['land_cu_filepath'],
                hab_id=self.project['filepaths']['land_cu_file_hab_id'],
                res_mat_filepath=self.project['filepaths']['land_res_mat_filepath'],
                pu_filepath=self.project['filepaths']['pu_filepath'],
                pu_id=self.project['filepaths']['pu_file_pu_id'],
                res_type=self.project['options']['land_res_matrixType'],
                progressbar=self.land_PU_CM_progress.GetValue())

            pandas.read_json(self.temp['land_pu_conmat'], orient='split').to_csv(
                self.project['filepaths']['land_pu_cm_filepath'], index=0, header=True, sep=",")
        except:
            self.log.Show()
            raise

    def on_resistance_mat_customize(self, event):
        file_viewer(parent=self, file=self.project['filepaths']['land_res_mat_filepath'],
                    title='Resistance Matrix - WARNING CHANGES WILL NOT BE SAVED, check back in the next version!')

    def check_matrix_list_format(self, format, filepath):
        # warn if matrix is wrong format
        if format == "Matrix":
            self.conmat = pandas.read_csv(filepath, index_col=0)
        else:
            if format == "Edge List":
                self.ncol = 3
                self.expected = numpy.array(['id1', 'id2', 'value'])
            elif format == "Edge List with Type":
                self.ncol = 4
                self.expected = numpy.array(['type', 'id1', 'id2', 'value'])
            elif format == "Edge List with Time":
                self.ncol = 4
                self.expected = numpy.array(['time', 'id1', 'id2', 'value'])
            self.conmat = pandas.read_csv(filepath)
            self.message = "See the Glossary for 'Data Formats' under 'Connectivity'."
            self.warn = False
            if not self.conmat.shape[1] == self.ncol:
                self.message = self.message + " The " + format + " Data Format expects exactly " + str(self.ncol) + " columns, not " + \
                               str(self.conmat.shape[1]) + " in the file."
                self.warn = True

            self.missing = [c not in self.conmat.columns for c in self.expected]
            if any(self.missing):
                self.message = self.message + " The " + format + " Data Format expects column header(s) '" + \
                               str(self.expected[self.missing]) + \
                               "' which may be missing in the file."
                self.warn = True
            if self.warn:
                marxanconpy.warn_dialog(message=self.message)
        return

# ##########################  metric related functions ################################################################

    def on_calc_metrics(self, event):
        """
        calculates the selected metrics
        """
        try:
            print("Calculating Metrics")

            self.set_metric_options()

            if not any(self.project['options']['land_metrics'].values()) and not any(
                    self.project['options']['demo_metrics'].values()):
                marxanconpy.warn_dialog(message="No metrics selected")
                raise Exception("No metrics selected")

            if not self.calc_metrics_pu.GetValue() and not self.calc_metrics_cu.GetValue():
                marxanconpy.warn_dialog(message="No 'Units' selected for metric calculations.")
                raise Exception("No 'Units' selected for metric calculations.")

            marxanconpy.manipulation.calc_metrics(project=self.project,
                                                  progressbar=True,
                                                  calc_metrics_pu=self.calc_metrics_pu.GetValue(),
                                                  calc_metrics_cu=self.calc_metrics_cu.GetValue())








            # create initial spec
            self.project['options']['metricsCalculated'] = True
            self.on_new_spec()
            self.customize_spec.Enable(enable=True)
            self.export_CF_files.Enable(enable=True)
            self.export_BD_file.Enable(enable=True)
            self.export_pudat.Enable(enable=True)
            self.export_metrics.Enable(enable=True)
            self.custom_spec_panel.SetToolTip(None)
            self.colormap_shapefile_choices()
            self.colormap_metric_choices(1)
            self.colormap_metric_choices(2)
            self.colormap_metric_choices("pre-eval")
            self.update_discrete_grid()

        except:
            print("Warning: Error in metrics calculation")
            self.log.Show()
            raise
        marxanconpy.warn_dialog("All calculations completed successfully.",
                                "Calculations Successful")

    def on_export_metrics(self, event):
        self.on_export_CF_files(event=None, mute=True)
        self.on_export_BD_file(event=None, mute=True)
        self.on_export_PUDAT(event=None, mute=True)
        marxanconpy.warn_dialog("All files exported successfully.",
                                "Export Successful")

    def on_export_CF_files( self, event, mute=False ):
        cf = {}
        spec = {}
        for type in ['spec_demo_pu', 'spec_land_pu']:
            if type in self.project['connectivityMetrics']:
                metrics = list(self.project['connectivityMetrics'][type])
                approved = ['discrete']
                metrics[:] = [m for m in metrics if any(a in m for a in approved)]
                for k in metrics:
                    cf[k] = self.project['connectivityMetrics'][type].copy().pop(k)

        spec = pandas.read_json(self.project['spec_dat'], orient='split')
        if len(cf) == 0:
            marxanconpy.warn_dialog(message="No conservation features associated with planning units were calculated.")
        else:
            # Export or append feature files
            if self.cf_export_radioBox.GetStringSelection() == "Export":
                # export spec

                spec.to_csv(self.project['filepaths']['spec_filepath'], index=0)
                # export conservation features
                cf['pu'] = gpd.GeoDataFrame.from_file(self.project['filepaths']['pu_filepath'])[self.project['filepaths']['pu_file_pu_id']]
                try:
                    cf['pu'] = cf['pu'].astype('int').astype('str')
                except:
                    cf['pu'] = cf['pu'].astype('str')
                cf = pandas.DataFrame(cf).melt(id_vars=['pu'], var_name='name', value_name='amount')
                cf = pandas.merge(cf, spec, how='outer', on='name')
                cf = cf.rename(columns={'id': 'species'}).sort_values(['pu', 'species'])
                cf = cf[cf['amount'] > 0]
                cf = cf.sort_values(by=['pu'])
                cf[['species', 'pu', 'amount']].to_csv(self.project['filepaths']['cf_filepath'], index=0)

            elif self.cf_export_radioBox.GetStringSelection() == "Append":
                # append
                if os.path.isfile(self.project['filepaths']['orig_spec_filepath']):
                    old_spec = marxanconpy.read_csv_tsv(self.project['filepaths']['orig_spec_filepath'])
                else:
                    marxanconpy.warn_dialog("Warning! File: " +
                                            self.project['filepaths']['orig_spec_filepath'] +
                                            " does not exist.")

                if os.path.isfile(self.project['filepaths']['orig_cf_filepath']):
                    old_cf = marxanconpy.read_csv_tsv(self.project['filepaths']['orig_cf_filepath'])
                    try:
                        old_cf['pu'] = old_cf['pu'].astype('int').astype('str')
                    except:
                        old_cf['pu'] = old_cf['pu'].astype('str')
                else:
                    marxanconpy.warn_dialog("Warning! File: " +
                                            self.project['filepaths']['orig_cf_filepath'] +
                                            " does not exist.")



                # append spec
                new_spec = spec.copy()
                new_spec['id'] = new_spec['id'] + max(old_spec['id'])
                pandas.concat([old_spec, new_spec],sort=False).fillna(0.0).to_csv(
                    self.project['filepaths']['spec_filepath']
                    , index=0)
                # append conservation features
                new_cf = cf.copy()
                new_cf['pu'] = gpd.GeoDataFrame.from_file(self.project['filepaths']['pu_filepath'])[self.project['filepaths']['pu_file_pu_id']]
                try:
                    new_cf['pu'] = new_cf['pu'].astype('int').astype('str')
                except:
                    new_cf['pu'] = new_cf['pu'].astype('str')

                new_cf = pandas.DataFrame(new_cf).melt(id_vars=['pu'], var_name='name', value_name='amount')
                new_cf = pandas.merge(new_cf, new_spec, how='outer', on='name')
                new_cf = new_cf.rename(columns={'id': 'species'})
                new_cf = new_cf[new_cf['amount']>0]
                pandas.concat([old_cf, new_cf[['species', 'pu', 'amount']]],sort=False).sort_values(['pu','species']).to_csv(
                    self.project['filepaths']['cf_filepath'], index=0)

        if not mute:
            marxanconpy.warn_dialog("Planning Unit versus Conservation Feature (i.e. puvspr.dat) and Conservation Feature (i.e. spec.dat) files exported successfully.",
                                    "Export Successful")

    def on_export_BD_file( self, event, mute=False):
        if self.BD_filecheck.GetValue():
            self.export_boundary_file(BD_filepath=self.project['filepaths']['bd_filepath'])
        if not mute:
            marxanconpy.warn_dialog("Spatial Dependencies (i.e. boundary.dat) file exported successfully.",
                                    "Export Successful")

    def on_export_PUDAT( self, event, mute=False):
        if self.PUDAT_filecheck.GetValue():
            if os.path.isfile(self.project['filepaths']['orig_pudat_filepath']):
                self.temp = {}
                self.lock_pudat(self.project['filepaths']['orig_pudat_filepath'])
                self.temp['pudat'] = marxanconpy.read_csv_tsv(self.project['filepaths']['orig_pudat_filepath'])
                self.temp['pudat']['status'] = self.project['connectivityMetrics']['status']
                self.temp['pudat'].to_csv(self.project['filepaths']['pudat_filepath'], index=0)
            else:
                marxanconpy.warn_dialog("Warning! File: " +
                                        self.project['filepaths']['orig_pudat_filepath'] +
                                        " does not exist.")

        if not mute:
            marxanconpy.warn_dialog("Planning Unit (i.e. pu.dat) file exported successfully.",
                                    "Export Successful")

    def export_boundary_file(self, BD_filepath):
        multiple = len(self.project['connectivityMetrics']['boundary'].keys()) > 1

        for k in self.project['connectivityMetrics']['boundary']:
            # Export each selected boundary definition
            if multiple:
                pandas.read_json(self.project['connectivityMetrics']['boundary'][k],
                                 orient='split').to_csv(str.replace(BD_filepath,
                                                                    ".dat",
                                                                    "_" + k + ".dat"),
                                                        index=False)
            else:
                pandas.read_json(self.project['connectivityMetrics']['boundary'][k],
                                 orient='split').to_csv(BD_filepath, index=False)

        # warn when multiple boundary definitions
        if multiple:
            marxanconpy.warn_dialog(message="Multiple Boundary Definitions were selected. Boundary file names have been"
                                     " edited to include type.", caption="Warning!")

    def lock_pudat(self, pudat_filepath):
        if os.path.isfile(pudat_filepath):
            self.temp = {}
            self.temp['pudat'] = marxanconpy.read_csv_tsv(pudat_filepath)
            if os.path.isfile(self.project['filepaths']['fa_filepath']):
                if self.fa_status_radioBox.GetStringSelection() == "Locked out":
                    self.temp['pudat'].loc[numpy.array(self.spatial['pu_shp']['fa_included']), 'status'] = 3
                if self.fa_status_radioBox.GetStringSelection() == "Locked in":
                    self.temp['pudat'].loc[numpy.array(self.spatial['pu_shp']['fa_included']), 'status'] = 2

            if os.path.isfile(self.project['filepaths']['aa_filepath']):
                if self.aa_status_radioBox.GetStringSelection() == "Locked out":
                    self.temp['pudat'].loc[numpy.array(self.spatial['pu_shp']['aa_included']), 'status'] = 3
                if self.aa_status_radioBox.GetStringSelection() == "Locked in":
                    self.temp['pudat'].loc[numpy.array(self.spatial['pu_shp']['aa_included']), 'status'] = 2

            self.temp['all_metrics'] = []
            if 'connectivityMetrics' in self.project:
                if 'spec_demo_pu' in self.project['connectivityMetrics']:
                    self.temp['all_metrics'] += self.project['connectivityMetrics']['spec_demo_pu']
                if 'spec_land_pu' in self.project['connectivityMetrics']:
                    self.temp['all_metrics'] += self.project['connectivityMetrics']['spec_land_pu']

            for self.temp['metric'] in self.temp['all_metrics']:
                if 'demo_pu' in self.temp['metric']:
                    self.temp['metric_values'] = self.project['connectivityMetrics']['spec_demo_pu'][self.temp['metric']]
                if 'land_pu' in self.temp['metric']:
                    self.temp['metric_values'] = self.project['connectivityMetrics']['spec_land_pu'][self.temp['metric']]

                if self.temp['metric'].endswith('lockout'):
                    self.temp['pudat'].loc[numpy.array(self.temp['metric_values']) != 0, 'status'] = 3
                if self.temp['metric'].endswith('lockin'):
                    self.temp['pudat'].loc[numpy.array(self.temp['metric_values']) != 0, 'status'] = 2

                self.project['connectivityMetrics']['status'] = self.temp['pudat']['status'].tolist()
                self.colormap_shapefile_choices()
                self.colormap_metric_choices(1)
                self.colormap_metric_choices(2)

# ########################## pre-evaluation functions ##################################################################
    def on_preEval_metric_shp_choice(self,event):
        self.colormap_metric_choices("pre-eval")
        self.on_preEval_metric_choice(event=None)

    def on_preEval_metric_choice(self, event):
        self.temp = {}
        type = self.get_plot_type(selection=self.preEval_metric_shp_choice.GetStringSelection())
        metric_type = self.get_metric_type(selection=self.preEval_metric_choice.GetStringSelection(),
                                                     type=self.get_plot_type(
                                                         selection=self.preEval_metric_shp_choice.GetStringSelection()))
        if not metric_type == None:
            if 'spec_' + type in self.project['connectivityMetrics']:
                self.temp['metric'] = self.project['connectivityMetrics']['spec_' + type][metric_type]

                self.preEval_grid.SetCellValue(0, 0, str(sum(self.temp['metric'])))
                self.preEval_grid.SetCellValue(1, 0, str(numpy.mean(self.temp['metric'])))
                self.preEval_grid.SetCellValue(2, 0, str(numpy.std(self.temp['metric'])))
                self.preEval_grid.SetCellValue(3, 0, str(min(self.temp['metric'])))
                self.preEval_grid.SetCellValue(4, 0, str(numpy.percentile(self.temp['metric'], 25)))
                self.preEval_grid.SetCellValue(5, 0, str(numpy.percentile(self.temp['metric'], 50)))
                self.preEval_grid.SetCellValue(6, 0, str(numpy.percentile(self.temp['metric'], 75)))
                self.preEval_grid.SetCellValue(7, 0, str(max(self.temp['metric'])))
                if 'aa_included' in self.spatial:
                    self.preEval_grid.SetCellValue(8, 0, str((sum(
                        self.spatial['pu_shp']['aa_included'].multiply(self.temp['metric'])) / sum(
                        self.temp['metric']) * 100)))
                else:
                    self.preEval_grid.SetCellValue(8, 0, 'NA')
                if 'fa_included' in self.spatial:
                    self.preEval_grid.SetCellValue(9, 0, str((sum(
                        self.spatial['pu_shp']['fa_included'].multiply(self.temp['metric'])) / sum(
                        self.temp['metric']) * 100)))
                else:
                    self.preEval_grid.SetCellValue(9, 0, 'NA')

    def on_plot_freq_metric( self, event ):
        self.temp = {}
        type = self.get_plot_type(selection=self.preEval_metric_shp_choice.GetStringSelection())
        metric_type = self.get_metric_type(selection=self.preEval_metric_choice.GetStringSelection(),
                                           type=self.get_plot_type(
                                               selection=self.preEval_metric_shp_choice.GetStringSelection()))

        # get the 'from' for discretization
        if 'spec_' + type in self.project['connectivityMetrics']:
            self.temp['metric'] = numpy.array(self.project['connectivityMetrics']['spec_' + type][metric_type])
            
        self.on_plot_freq(self.temp['metric'],metric_type)
            
    def on_plot_freq(self,metric,metric_type):
        # prepare plotting window
        if not hasattr(self, 'plot'):
            self.plot = wx.Panel(self.auinotebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
            for i in range(self.auinotebook.GetPageCount()):
                if self.auinotebook.GetPageText(i) == "7) Plotting Options":
                    self.auinotebook.AddPage(self.plot, u"8) Plot", False, wx.NullBitmap)
                elif self.auinotebook.GetPageText(i) == "8) Plotting Options":
                    self.auinotebook.AddPage(self.plot, u"9) Plot", False, wx.NullBitmap)
        self.plot.figure = plt.figure(figsize=self.plot.GetClientSize() / wx.ScreenDC().GetPPI()[0])
        self.plot.axes = self.plot.figure.gca()
        self.plot.canvas = FigureCanvas(self.plot, -1, self.plot.figure)
        self.plot.sizer = wx.BoxSizer(wx.VERTICAL)
        self.plot.sizer.Add(self.plot.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.plot.SetSizer(self.plot.sizer)
        self.plot.Fit()

        if int(len(metric)/15) > 100:
            b=100
        else:
            b=int(len(metric)/15)

        self.plot.hist = plt.hist(metric,bins=b)
        self.plot.xlabel = plt.xlabel(metric_type)
        self.plot.ylabel = plt.ylabel("Frequency")
        self.plot.axvline = plt.axvline(numpy.percentile(metric, 25), label='test',color='k',linestyle='--')
        self.plot.text = plt.text(numpy.percentile(metric, 20),sum(self.plot.axes.get_ylim())/2,'Lower Quartile',rotation=90,verticalalignment='center')
        self.plot.axvline = plt.axvline(numpy.percentile(metric, 50), label='test',color='k',linestyle='--')
        self.plot.text = plt.text(numpy.percentile(metric, 45), sum(self.plot.axes.get_ylim()) / 2, 'Median', rotation=90,verticalalignment='center')
        self.plot.axvline = plt.axvline(numpy.percentile(metric, 75), label='test',color='k',linestyle='--')
        self.plot.text = plt.text(numpy.percentile(metric, 70), sum(self.plot.axes.get_ylim()) / 2, 'Upper Quartile', rotation=90,verticalalignment='center')
        # change selection to plot tab
        for i in range(self.auinotebook.GetPageCount()):
            if self.auinotebook.GetPageText(i) == "8) Plot" or self.auinotebook.GetPageText(i) == "9) Plot":
                self.auinotebook.ChangeSelection(i)

    def on_remove_metric(self,event):
        type = self.get_plot_type(selection=self.preEval_metric_shp_choice.GetStringSelection())
        metric_type = self.get_metric_type(selection=self.preEval_metric_choice.GetStringSelection(),
                                           type=self.get_plot_type(
                                               selection=self.preEval_metric_shp_choice.GetStringSelection()))
        if 'spec_' + type in self.project['connectivityMetrics']:
            del self.project['connectivityMetrics']['spec_' + type][metric_type]
            if len(self.project['connectivityMetrics']['spec_' + type])==0:
                del self.project['connectivityMetrics']['spec_' + type]
        self.colormap_shapefile_choices()
        self.colormap_metric_choices("pre-eval")
        self.on_preEval_metric_choice(event=None)
        self.on_new_spec()
        self.update_discrete_grid()

    def on_preEval_create_new(self, event):
        self.temp = {}
        type = self.get_plot_type(selection=self.preEval_metric_shp_choice.GetStringSelection())
        metric_type = self.get_metric_type(selection=self.preEval_metric_choice.GetStringSelection(),
                                           type=self.get_plot_type(
                                               selection=self.preEval_metric_shp_choice.GetStringSelection()))

        # get the 'from' for discretization
        if 'spec_' + type in self.project['connectivityMetrics']:
            self.temp['metric'] = numpy.array(self.project['connectivityMetrics']['spec_' + type][metric_type])

        if self.preEval_discrete_from_quartile.GetValue():
            if self.preEval_discrete_from_quartile_radio.GetStringSelection()== "Minimum":
                self.temp['from_type'] = 'minimum'
                self.temp['from'] = min(self.temp['metric'])
            if self.preEval_discrete_from_quartile_radio.GetStringSelection()== "Lower Quartile":
                self.temp['from_type'] = 'lower_quartile'
                self.temp['from'] = numpy.percentile(self.temp['metric'], 25)
            if self.preEval_discrete_from_quartile_radio.GetStringSelection()== "Median":
                self.temp['from_type'] = 'median'
                self.temp['from'] = numpy.percentile(self.temp['metric'], 50)
            if self.preEval_discrete_from_quartile_radio.GetStringSelection()== "Upper Quartile":
                self.temp['from_type'] = 'upper_quartile'
                self.temp['from'] = numpy.percentile(self.temp['metric'], 75)
            if self.preEval_discrete_from_quartile_radio.GetStringSelection()== "Maximum":
                self.temp['from_type'] = 'maximum'
                self.temp['from'] = max(self.temp['metric'])

        if self.preEval_discrete_from_percentile.GetValue():
            self.temp['from'] = numpy.percentile(self.temp['metric'],
                                                 self.preEval_discrete_from_percentile_slider.GetValue())
            self.temp['from_type'] = str(self.preEval_discrete_from_percentile_slider.GetValue()) + 'th_percentile'

        if self.preEval_discrete_from_value.GetValue():
            self.temp['from'] = float(self.preEval_discrete_from_value_txtctrl.GetValue())
            self.temp['from_type'] = str(self.temp['from'])

        # get the 'to' for discretization
        if self.preEval_discrete_to_quartile.GetValue():
            if self.preEval_discrete_to_quartile_radio.GetStringSelection() == "Minimum":
                self.temp['to_type'] = 'minimum'
                self.temp['to'] = min(self.temp['metric'])
            if self.preEval_discrete_to_quartile_radio.GetStringSelection() == "Lower Quartile":
                self.temp['to_type'] = 'lower_quartile'
                self.temp['to'] = numpy.percentile(self.temp['metric'], 25)
            if self.preEval_discrete_to_quartile_radio.GetStringSelection() == "Median":
                self.temp['to_type'] = 'median'
                self.temp['to'] = numpy.percentile(self.temp['metric'], 50)
            if self.preEval_discrete_to_quartile_radio.GetStringSelection() == "Upper Quartile":
                self.temp['to_type'] = 'upper_quartile'
                self.temp['to'] = numpy.percentile(self.temp['metric'], 75)
            if self.preEval_discrete_to_quartile_radio.GetStringSelection() == "Maximum":
                self.temp['to_type'] = 'maximum'
                self.temp['to'] = max(self.temp['metric'])

        if self.preEval_discrete_to_percentile.GetValue():
            self.temp['to'] = numpy.percentile(self.temp['metric'],
                                                 self.preEval_discrete_to_percentile_slider.GetValue())
            self.temp['to_type'] = str(self.preEval_discrete_to_percentile_slider.GetValue()) + 'th_percentile'

        if self.preEval_discrete_to_value.GetValue():
            self.temp['to'] = float(self.preEval_discrete_to_value_txtctrl.GetValue())
            self.temp['to_type'] = str(self.temp['to'])


        # create new metric
        self.temp['new_metric'] = (self.temp['metric']>=self.temp['from']) & (self.temp['metric']<=self.temp['to']).astype(int)
        if self.preEval_status_radio.GetStringSelection() == "Status-quo":
            self.project['connectivityMetrics']['spec_' + type][
            metric_type + '_discrete_' + self.temp['from_type'] + '_to_' + self.temp['to_type']] = self.temp[
            'new_metric'].tolist()
        if self.preEval_status_radio.GetStringSelection() == "Locked out":
            self.project['connectivityMetrics']['spec_' + type][
            metric_type + '_discrete_' + self.temp['from_type'] + '_to_' + self.temp['to_type'] + '_lockout'] = self.temp[
            'new_metric'].tolist()
        if self.preEval_status_radio.GetStringSelection() == "Locked in":
            self.project['connectivityMetrics']['spec_' + type][
            metric_type + '_discrete_' + self.temp['from_type'] + '_to_' + self.temp['to_type'] + '_lockin'] = self.temp[
            'new_metric'].tolist()

        # reset choices
        self.lock_pudat(self.project['filepaths']['orig_pudat_filepath'])
        self.colormap_shapefile_choices()
        self.colormap_metric_choices("pre-eval")
        self.on_preEval_metric_choice(event=None)
        self.on_new_spec()
        self.update_discrete_grid()

    def on_from_check( self, event ):
        self.preEval_discrete_from_quartile.SetValue(False)
        self.preEval_discrete_from_percentile.SetValue(False)
        self.preEval_discrete_from_value.SetValue(False)
        event.GetEventObject().SetValue(True)
        self.enable_discrete()

    def on_to_check(self, event):
        self.preEval_discrete_to_quartile.SetValue(False)
        self.preEval_discrete_to_percentile.SetValue(False)
        self.preEval_discrete_to_value.SetValue(False)
        event.GetEventObject().SetValue(True)
        self.enable_discrete()

    def enable_discrete(self):
        if self.preEval_discrete_from_quartile.GetValue():
            self.preEval_discrete_from_quartile_radio.Enable(True)
        else:
            self.preEval_discrete_from_quartile_radio.Enable(False)

        if self.preEval_discrete_from_percentile.GetValue():
            self.preEval_discrete_from_percentile_slider.Enable(True)
        else:
            self.preEval_discrete_from_percentile_slider.Enable(False)

        if self.preEval_discrete_from_value.GetValue():
            self.preEval_discrete_from_value_txtctrl.Enable(True)
        else:
            self.preEval_discrete_from_value_txtctrl.Enable(False)

        if self.preEval_discrete_to_quartile.GetValue():
            self.preEval_discrete_to_quartile_radio.Enable(True)
        else:
            self.preEval_discrete_to_quartile_radio.Enable(False)

        if self.preEval_discrete_to_percentile.GetValue():
            self.preEval_discrete_to_percentile_slider.Enable(True)
        else:
            self.preEval_discrete_to_percentile_slider.Enable(False)

        if self.preEval_discrete_to_value.GetValue():
            self.preEval_discrete_to_value_txtctrl.Enable(True)
        else:
            self.preEval_discrete_to_value_txtctrl.Enable(False)

    def update_discrete_grid(self):
        self.all_types = []
        if self.calc_metrics_pu.GetValue():
            if os.path.isfile(self.project['filepaths']['demo_pu_cm_filepath']):
                self.all_types += ['demo_pu']
            if os.path.isfile(self.project['filepaths']['land_pu_cm_filepath']):
                self.all_types += ['land_pu']
        else:
            marxanconpy.warn_dialog(message="'Planning Units' not selected for metric calculations.")
            return

        for self.type in self.all_types:
            metrics = list(self.project['connectivityMetrics']['spec_' + self.type])
            approved = ['discrete']
            metrics[:] = [m for m in metrics if any(a in m for a in approved)]

            Rows = self.discrete_grid.GetNumberRows()
            if Rows > 0:
                self.discrete_grid.DeleteRows(0, Rows, True)
            for j in range(len(metrics)):
                if j != self.discrete_grid.GetNumberRows():
                    i = self.discrete_grid.GetNumberRows()
                else:
                    i = j
                self.discrete_grid.InsertRows(i)
                self.discrete_grid.SetCellValue(i, 0, str(metrics[i]))
                if metrics[i].endswith('lockout'):
                    self.discrete_grid.SetCellValue(i, 1, str("Locked Out"))
                elif metrics[i].endswith('lockin'):
                    self.discrete_grid.SetCellValue(i, 1, str("Locked In"))
                else:
                    self.discrete_grid.SetCellValue(i, 1, str("Status Quo"))

                if 'spec_demo_pu' in self.project['connectivityMetrics'] and 'spec_land_pu' in self.project['connectivityMetrics']:
                    spec = {**self.project['connectivityMetrics']['spec_demo_pu'], **self.project['connectivityMetrics']['spec_land_pu']}
                elif 'spec_demo_pu' in self.project['connectivityMetrics']:
                    spec = self.project['connectivityMetrics']['spec_demo_pu']
                elif 'spec_land_pu' in self.project['connectivityMetrics']:
                    spec = self.project['connectivityMetrics']['spec_land_pu']

                self.discrete_grid.SetCellValue(i,2,str(100*(numpy.mean(spec[metrics[i]])).round(2))+'%')

        self.discrete_grid.AutoSize()

# ########################## marxan functions ##########################################################################

    def on_generate_inputdat( self, event ):
        """
        Generate the Marxan input file from the template
        :param event:
        :return:
        """
        if self.project['filepaths']['marxan_template_input'] == 'Default':
            with open(os.path.join(MCPATH, 'Marxan243','input_template.dat'), 'r', encoding="utf8") as file:
                filedata = file.readlines()
        else:
            with open(self.project['filepaths']['marxan_template_input'], 'r', encoding="utf8") as file:
                filedata = file.readlines()

        if self.project['options']['inputdat_boundary'] == 'Asymmetric':
            if not 'ASYMMETRICCONNECTIVITY  1\n' in filedata:
                filedata.insert([index for index, line in enumerate(filedata) if line.startswith('NUMREPS')][0] + 1,
                            'ASYMMETRICCONNECTIVITY  1\n')
        else:
            if 'ASYMMETRICCONNECTIVITY  1\n' in filedata:
                filedata.remove('ASYMMETRICCONNECTIVITY  1\n')

        # Replace the target string
        pudat = []
        for index, line in enumerate(filedata):
            if line.startswith("INPUTDIR"):
                inputdir = os.path.join(os.path.dirname(self.project['filepaths']['marxan_input']),
                                        line.replace('INPUTDIR ', '').replace('\n', ''))

            if line.startswith("NUMREPS"):
                line = 'NUMREPS ' + self.project['options']['NUMREPS'] + '\n'


            if line.startswith("SCENNAME"):
                line = 'SCENNAME ' + self.project['options']['SCENNAME'] + '\n'

            if line.startswith("NUMITNS"):
                line = 'NUMITNS ' + self.project['options']['NUMITNS'] + '\n'

            if line.startswith("BLM"):
                line = 'BLM ' + self.project['options']['CSM'] + '\n'

            if line.startswith("PUVSPRNAME"):
                if self.project['options']['marxan_CF'] == 'New':
                    line = 'PUVSPRNAME ' + os.path.relpath(self.project['filepaths']['cf_filepath'],inputdir) + '\n'
                else:
                    line = 'PUVSPRNAME ' + os.path.relpath(self.project['filepaths']['orig_cf_filepath'],inputdir) + '\n'

            if line.startswith("SPECNAME"):
                if self.project['options']['marxan_CF'] == 'New':
                    line = 'SPECNAME ' + os.path.relpath(self.project['filepaths']['spec_filepath'],inputdir) + '\n'
                else:
                    line = 'SPECNAME ' + os.path.relpath(self.project['filepaths']['orig_spec_filepath'],inputdir) + '\n'

            if line.startswith("PUNAME"):
                if self.project['options']['marxan_PU'] == 'New':
                    line = 'PUNAME ' + os.path.relpath(self.project['filepaths']['pudat_filepath'],inputdir) + '\n'
                else:
                    line = 'PUNAME ' + os.path.relpath(self.project['filepaths']['orig_pudat_filepath'],inputdir) + '\n'

            if line.startswith("BOUNDNAME"):
                if self.project['options']['marxan_bound'] == 'New':
                    line = 'BOUNDNAME ' + os.path.relpath(self.project['filepaths']['bd_filepath'],inputdir) + '\n'
                elif self.project['options']['marxan_bound'] == 'Original':
                    line = 'BOUNDNAME ' + os.path.relpath(self.project['filepaths']['orig_bd_filepath'],inputdir) + '\n'
                else:
                    line = '\n'


            pudat.append(line)

        with open(self.project['filepaths']['marxan_input'], 'w', encoding="utf8") as file:
            file.writelines(pudat)

        marxanconpy.warn_dialog("The Marxan input file (i.e. input.dat) has been generated successfully.",
                                "Operation Successful")

    def on_default_input_template(self, event):
        self.project['filepaths']['marxan_template_input'] = 'Default'
        self.inputdat_template_file.SetPath('Default')

    def on_customize_inpudat( self, event ):
        """
        Customize the Marxan input file
        :param event:
        :return:
        """
        if platform.system() == 'Windows':
            test=os.system("start "+self.project['filepaths']['marxan_input'])
            if test==1:
                marxanconpy.warn_dialog(
                    "Your computer does not have a default editor for the select file. In Windows File Explorer, double click on a the selected file, You will be asked to set the default program (notepad, notepad++, etc). After that MC will be able to open the file in the default editor")
        elif platform.system() == "Darwin":
            os.system("open -t " + self.project['filepaths']['marxan_input'])


    def on_run_marxan(self, event):
        """
        Starts Marxan
        """
        print(f"Running Marxan from path: {MCPATH}");
        if self.project['options']['marxan'] == "Marxan":
            if not os.path.isfile(os.path.join(MCPATH, 'Marxan243',"Marxan.exe")) or\
                    not os.path.isfile(os.path.join(MCPATH, 'Marxan243',"Marxan_x64.exe")):
                marxanconpy.warn_dialog(message="Marxan executables (Marxan.exe or Marxan_x64.exe) not found in Marxan Directory")
        else:
            if not os.path.isfile(os.path.join(MCPATH, 'Marxan243', "MarZone.exe")) or \
                    not os.path.isfile(os.path.join(MCPATH, 'Marxan243', "MarZone_x64.exe")):
                marxanconpy.warn_dialog(message="Marxan executables (MarZone.exe or MarZone_x64.exe) not found in Marxan Directory")

        if not 'connectivityMetrics' in self.project:
            self.project['connectivityMetrics'] = {}
        self.temp = {}

        print("Reading the input file")
        # edit input file
        # Read in the file
        with open(self.project['filepaths']['marxan_input'], 'r', encoding="utf8") as file:
            filedata = file.readlines()

        for index, line in enumerate(filedata):
            if line.startswith("INPUTDIR"):
                inputdir = line.replace("INPUTDIR ", "").strip('\n')
                inputdatdir = os.path.join(os.path.dirname(self.project['filepaths']['marxan_input']), inputdir)
                if not os.path.isdir(inputdir) and not os.path.isdir(inputdatdir):
                    marxanconpy.warn_dialog(message="Warning: Marxan Input File has an invalid input directory " + line)
            if line.startswith("OUTPUTDIR"):
                inputdir = line.replace("OUTPUTDIR ", "").strip('\n')
                inputdatdir = os.path.join(os.path.dirname(self.project['filepaths']['marxan_input']), inputdir)
                if not os.path.isdir(inputdir) and not os.path.isdir(inputdatdir):
                    marxanconpy.warn_dialog(message="Warning: Marxan Input File has an invalid input directory " + line)

        inputpath = os.path.dirname(self.project['filepaths']['marxan_input'])
        marxanpath = MCPATH
        if os.path.dirname(self.project['filepaths']['marxan_input']).startswith("\\"):
            inputpath = inputpath.replace(inputpath[0:2], "C:\\")
            marxanpath = marxanpath.replace(marxanpath[0:2], "C:\\")

        print("Input file modifications done, starting Marxan execution for {}".format(platform.system()))

        if platform.system() == 'Windows':
            print("Running Marxan for Windows")
            marxanconpy.warn_dialog(
                "Please note: Marxan Connect will be unresponsive until the Marxan pop-up window has finished and has been closed.")
            if self.project['options']['marxan'] == "Marxan":
                if self.project['options']['marxan_bit']=="64-bit":
                    marxan_exec = 'Marxan_x64.exe'
                else:
                    marxan_exec = 'Marxan.exe'
            else:
                if self.project['options']['marxan_bit']=="64-bit":
                    marxan_exec = 'MarZone_x64.exe'
                else:
                    marxan_exec = 'MarZone.exe'

            if " " in self.project['filepaths']['marxan_input']:
                marxanconpy.warn_dialog("Marxan will likely fail to find the input file because the filepath contains "
                                        "spaces. Please move your project folder or rename the offending directory")

            subprocess.call(os.path.join(marxanpath, 'Marxan243', marxan_exec) + ' ' +
                            self.project['filepaths']['marxan_input'],
                            creationflags=subprocess.CREATE_NEW_CONSOLE,
                            cwd=inputpath)

        elif platform.system() == 'Darwin':
            print("Running Marxan for macOS")
            self.log.Show()
            marxanconpy.warn_dialog(
                "Please note: Marxan Connect will be unresponsive until the Marxan pop-up window has finished. On macOS,"
                "Marxan Connect does not provide 'live' updates on Marxan's progress. See the 'macOS Marxan feedback' "
                "issue on our github page")
            if self.project['options']['marxan'] == "Marxan":
                if self.project['options']['marxan_bit']=="64-bit":
                    marxan_exec = 'MarOpt_v243_Mac64'
                else:
                    marxan_exec = 'MarOpt_v243_Mac32'
            else:
                marxanconpy.warn_dialog('Sorry, this experimental feature is only available for Windows at the monment')

            if " " in self.project['filepaths']['marxan_input']:
                marxanconpy.warn_dialog("Marxan will likely fail to find the input file because the filepath contains "
                                        "spaces. Please move your project folder or rename the offending directory")
                
            proc = pexpect.spawnu(os.path.join(marxanpath, 'Marxan243', marxan_exec)+' '+os.path.relpath(self.project['filepaths']['marxan_input'],inputpath),cwd=inputpath)
            proc.logfile = sys.stdout
            proc.expect('.*Press return to exit.*')
            proc.close()
        
        elif platform.system() == 'Linux':
            print("Running Marxan for Windows")
            self.log.Show()
            marxanconpy.warn_dialog(
                "Please note: Marxan Connect will be unresponsive until the Marxan pop-up window has finished. On macOS,"
                "Marxan Connect does not provide 'live' updates on Marxan's progress. See the 'macOS Marxan feedback' "
                "issue on our github page")
            if self.project['options']['marxan'] == "Marxan":
                if self.project['options']['marxan_bit']=="64-bit":
                    marxan_exec = 'MarOpt_v243_Linux64'
                else:
                    marxan_exec = 'MarOpt_v243_Linux32'
            else:
                marxanconpy.warn_dialog('Sorry, this experimental feature is only available for Windows at the monment')

            if " " in self.project['filepaths']['marxan_input']:
                marxanconpy.warn_dialog("Marxan will likely fail to find the input file because the filepath contains "
                                        "spaces. Please move your project folder or rename the offending directory")
                
            proc = pexpect.spawnu(os.path.join(marxanpath, 'Marxan243', marxan_exec)+' '+os.path.relpath(self.project['filepaths']['marxan_input'],inputpath),cwd=inputpath)
            proc.logfile = sys.stdout
            proc.expect('.*Press return to exit.*')
            proc.close()
            
        self.load_marxan_output()

    def load_marxan_output(self):
        if not('connectivityMetrics' in self.project):
            self.project['connectivityMetrics'] = {}
        
        self.project['connectivityMetrics']['select_freq'] = marxanconpy.manipulation.get_marxan_output(self.project['filepaths']['marxan_input'],
                                                              'Selection Frequency').iloc[:,1].tolist()
        
        self.project['connectivityMetrics']['best_solution'] = marxanconpy.manipulation.get_marxan_output(self.project['filepaths']['marxan_input'],
                                                              'Best Solution').iloc[:,1].tolist()

        # update plotting options
        self.colormap_shapefile_choices()
        self.colormap_metric_choices(1)
        self.colormap_metric_choices(2)
        self.enable_postHoc()

    def on_view_mvbest(self,event):
        self.temp = {}
        for line in open(self.project['filepaths']['marxan_input']):
            if line.startswith('SCENNAME'):
                self.temp['SCENNAME'] = line.replace('SCENNAME ', '').replace('\n', '')
            elif line.startswith('OUTPUTDIR'):
                self.temp['OUTPUTDIR'] = line.replace('OUTPUTDIR ', '').replace('\n', '')
        mvbest = os.path.join(self.temp['OUTPUTDIR'],self.temp['SCENNAME']+'_mvbest')
        if os.path.isfile(mvbest+".txt"):
            file_viewer(parent=self, file=mvbest+".txt",title='mvbest')
        elif os.path.isfile(mvbest+".csv"):
            file_viewer(parent=self, file=mvbest+".csv",title='mvbest')
        elif os.path.isfile(os.path.join(os.path.dirname(self.project['filepaths']['marxan_input']),mvbest)+".txt"):
            file_viewer(parent=self,
                        file=os.path.join(os.path.dirname(self.project['filepaths']['marxan_input']),mvbest)+".txt",
            title='mvbest')
        elif os.path.isfile(os.path.join(os.path.dirname(self.project['filepaths']['marxan_input']),mvbest)+".csv"):
            file_viewer(parent=self,
                        file=os.path.join(os.path.dirname(self.project['filepaths']['marxan_input']),mvbest)+".csv",
                        title='mvbest')
        else:
            print("file not found")

    def on_view_sum(self,event):
        self.temp = {}
        for line in open(self.project['filepaths']['marxan_input']):
            if line.startswith('SCENNAME'):
                self.temp['SCENNAME'] = line.replace('SCENNAME ', '').replace('\n', '')
            elif line.startswith('OUTPUTDIR'):
                self.temp['OUTPUTDIR'] = line.replace('OUTPUTDIR ', '').replace('\n', '')
        sumtxt = os.path.join(self.temp['OUTPUTDIR'], self.temp['SCENNAME'] + '_sum')
        if os.path.isfile(sumtxt+".txt"):
            file_viewer(parent=self, file=sumtxt+".txt", title='sum')
        elif os.path.isfile(sumtxt+".csv"):
            file_viewer(parent=self, file=sumtxt+".csv", title='sum')
        elif os.path.isfile(os.path.join(os.path.dirname(self.project['filepaths']['marxan_input']), sumtxt)+".txt"):
            file_viewer(parent=self,
                        file=os.path.join(os.path.dirname(self.project['filepaths']['marxan_input']), sumtxt)+".txt",
                        title='sum')
        elif os.path.isfile(os.path.join(os.path.dirname(self.project['filepaths']['marxan_input']), sumtxt)+".csv"):
            file_viewer(parent=self,
                        file=os.path.join(os.path.dirname(self.project['filepaths']['marxan_input']), sumtxt)+".csv",
                        title='sum')
        else:
            print("file not found")

# ########################## postHoc functions ##########################################################################

    def enable_postHoc(self):
        self.set_postHoc_category_choice()
        if 'connectivityMetrics' in self.project:
            if 'best_solution' in self.project['connectivityMetrics']:
                self.calc_postHoc.Enable(True)
            else:
                self.calc_postHoc.Enable(False)
                
        if os.path.isfile(self.project['filepaths']['marxan_input']) & os.path.isfile(self.project['filepaths']['pu_filepath']):
            self.calc_postHoc.Enable(True)
        else:
            self.calc_postHoc.Enable(False)
            
            
        if 'postHoc' in self.project:
            if 'areas' in self.project['postHoc']:
                self.export_postHoc.Enable(True)
                self.export_postHoc_shp.Enable(True)
                self.plot_postHoc_spacing.Enable(True)
                self.plot_postHoc_sizes.Enable(True)
            else:
                self.export_postHoc.Enable(False)
                self.export_postHoc_shp.Enable(False)
                self.plot_postHoc_spacing.Enable(False)
                self.plot_postHoc_sizes.Enable(False)
        else:
            self.export_postHoc.Enable(False)
            self.export_postHoc_shp.Enable(False)
            self.plot_postHoc_spacing.Enable(False)
            self.plot_postHoc_sizes.Enable(False)
        
        if self.postHoc_output_choice.GetStringSelection() == "Selection Frequency":
            self.postHoc_percentage_slider.Enable(True)
        else:
            self.postHoc_percentage_slider.Enable(False)
        
        self.postHoc_enable_custom()


    def set_postHoc_category_choice(self):
        if self.postHoc_output_choice.GetSelection()==-1:
            selection=0
        else:
            selection=self.postHoc_output_choice.GetSelection()
        choices = []
        if os.path.isfile(self.project['filepaths']['land_pu_cm_filepath']):
            choices.append("Landscape Data")
        if os.path.isfile(self.project['filepaths']['demo_pu_cm_filepath']):
            choices.append("Demographic Data")
        self.postHoc_category_choice.SetItems(choices)
        self.postHoc_category_choice.SetSelection(selection)
        self.set_postHoc_output_choice()

    def on_postHoc_category_choice(self, event):
        Cols = self.postHoc_grid.GetNumberCols()
        Rows = self.postHoc_grid.GetNumberRows()
        if Cols > 0 or Rows > 0:
            self.postHoc_grid.DeleteCols(0, Cols, True)
            self.postHoc_grid.DeleteRows(0, Rows, True)
            
        if self.postHoc_output_choice.GetStringSelection() == "Selection Frequency":
            self.postHoc_percentage_slider.Enable(True)
        else:
            self.postHoc_percentage_slider.Enable(False)

    def on_postHoc_output_choice(self, event):
        Cols = self.postHoc_grid.GetNumberCols()
        Rows = self.postHoc_grid.GetNumberRows()
        if Cols > 0 or Rows > 0:
            self.postHoc_grid.DeleteCols(0, Cols, True)
            self.postHoc_grid.DeleteRows(0, Rows, True)
            
        if self.postHoc_output_choice.GetStringSelection() == "Selection Frequency":
            self.postHoc_percentage_slider.Enable(True)
        else:
            self.postHoc_percentage_slider.Enable(False)

    def on_calc_postHoc(self, event):
        self.project["postHoc"] = {}
        if self.postHoc_category_choice.GetStringSelection() == "Landscape Data":
            format = "Edge List with Habitat"
            filename = self.project['filepaths']['land_pu_cm_filepath']
        elif self.postHoc_category_choice.GetStringSelection() == "Demographic Data":
            format = self.demo_matrixFormatRadioBox.GetStringSelection()
            filename = self.project['filepaths']['demo_pu_cm_filepath']
        else:
            format = None
            filename = "notarealfilename"

        if self.postHoc_custom_choice.GetValue():        
            solution = marxanconpy.read_csv_tsv(self.postHoc_custom_file.GetPath())
        elif self.postHoc_output_choice.GetStringSelection()=="Selection Frequency":
            for line in open(self.project['filepaths']['marxan_input']):
                if line.startswith('NUMREPS'):
                    NUMREPS = int(line.replace('NUMREPS ', '').replace('\n', ''))
                    
            solution = marxanconpy.manipulation.get_marxan_output(self.project['filepaths']['marxan_input'],
                                                              self.postHoc_output_choice.GetStringSelection())
            solution.iloc[:,1] = (solution.iloc[:,1]>(NUMREPS/100*self.postHoc_percentage_slider.GetValue())).astype(int)
        else:
            solution = marxanconpy.manipulation.get_marxan_output(self.project['filepaths']['marxan_input'],
                                                              self.postHoc_output_choice.GetStringSelection())
        
        pu = gpd.GeoDataFrame.from_file(self.project['filepaths']['pu_filepath']).to_crs('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
        self.project["postHoc"]["min_dist"] = marxanconpy.posthoc.calc_postHoc_dist(pu,
                                                         filename,
                                                         format,
                                                         IDs=solution.iloc[:,0].values,
                                                         selectionIDs=solution[(solution.iloc[:,1].astype("str")=="1").values].iloc[:,0].values)
        self.project["postHoc"]["clusters"] = marxanconpy.posthoc.calc_postHoc_clusters(pu,
                                                               filename,
                                                               format,
                                                               IDs=solution.iloc[:,0].values,
                                                               selectionIDs=solution[(solution.iloc[:,1].astype("str")=="1").values].iloc[:,0].values)
        self.project["postHoc"]["areas"] = self.project["postHoc"]["clusters"].area
        self.project["postHoc"]["fragmentation"] = marxanconpy.posthoc.calc_postHoc_frag(self.project["postHoc"]["clusters"])
        
        
        # sum data
        for line in open(self.project['filepaths']['marxan_input']):
            if line.startswith('SCENNAME'):
                SCENNAME = line.replace('SCENNAME ', '').replace('\n', '')
            elif line.startswith('NUMREPS'):
                NUMREPS = int(line.replace('NUMREPS ', '').replace('\n', ''))
            elif line.startswith('OUTPUTDIR'):
                OUTPUTDIR = line.replace('OUTPUTDIR ', '').replace('\n', '')

        if not os.path.isdir(OUTPUTDIR):
            OUTPUTDIR = os.path.join(os.path.dirname(self.project['filepaths']['marxan_input']),OUTPUTDIR)
            
            
        fn = os.path.join(OUTPUTDIR, SCENNAME + "_sum")
        if os.path.isfile(fn + '.csv'):
            file = marxanconpy.read_csv_tsv(fn + '.csv')
        elif os.path.isfile(fn + '.txt'):
            file = marxanconpy.read_csv_tsv(fn + '.txt')
        else:
            print('WARNING: ' + fn + ' not found')
        
        self.project["postHoc"]["sum_data"] = file.iloc[int(file[["Score"]].idxmin())]
        
        postHoc = marxanconpy.posthoc.calc_postHoc(pu,
                                                   filename,
                                                   format,
                                                   IDs=solution.iloc[:,0].values,
                                                   selectionIDs=solution[(solution.iloc[:,1].astype("str")=="1").values].iloc[:,0].values,
                                                   sum_data=self.project["postHoc"]["sum_data"],
                                                   min_dist=self.project["postHoc"]["min_dist"],
                                                   fragmentation=self.project["postHoc"]["fragmentation"],
                                                   postHoc_areas=self.project["postHoc"]["areas"])
        Cols = self.postHoc_grid.GetNumberCols()
        Rows = self.postHoc_grid.GetNumberRows()
        if Cols > 0 or Rows > 0:
            self.postHoc_grid.DeleteCols(0, Cols, True)
            self.postHoc_grid.DeleteRows(0, Rows, True)
        for col, label in enumerate(postHoc.columns):
            if not col == 0:
                self.postHoc_grid.AppendCols()
                self.postHoc_grid.SetColLabelValue(col-1, label)
            for index in postHoc.index:
                if col == 0:
                    self.postHoc_grid.AppendRows()
                    self.postHoc_grid.SetRowLabelValue(index, str(postHoc.iloc[index, col]))
                elif label == "Type":
                    self.postHoc_grid.SetCellValue(index, col - 1, str(postHoc.iloc[index, col]))
                elif label == "Percent":
                    if index > 0 and index < 11:
                        self.postHoc_grid.SetCellValue(index, col-1, "")
                    else:
                        self.postHoc_grid.SetCellValue(index, col - 1, str(round(postHoc.iloc[index, col], 2)))
                elif label == "Planning Area" and index > 0 and index < 11:
                            self.postHoc_grid.SetCellValue(index, col-1, "")
                else:
                    if postHoc["Metric"][index] in ("Planning Units","Connections","Clusters","Marxan Score"):
                        self.postHoc_grid.SetCellValue(index, col-1, str(int(postHoc.iloc[index, col])))
                    elif postHoc["Metric"][index] in ("Graph Density"):
                        self.postHoc_grid.SetCellValue(index, col-1, str(round(postHoc.iloc[index, col], 6)))
                    else:
                        self.postHoc_grid.SetCellValue(index, col-1, str(round(postHoc.iloc[index, col], 2)))

        self.postHoc_grid.SetRowLabelSize(145)
        self.postHoc_grid.SetColLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.postHoc_grid.AutoSize()
        self.Layout()
        x,y = self.postHoc_grid.GetSize()
        winx,winy = self.GetSize()
        if winy-y < 280:
            self.postHoc_grid.SetSize(x+20,winy-280)
        self.project["postHoc"]["summary"] = postHoc.to_json(orient='split')
        self.enable_postHoc()

    def on_export_postHoc( self, event ):
        pandas.read_json(self.project["postHoc"]["summary"], orient='split').to_csv(self.project['filepaths']['posthoc'], index=0)
        
    def on_export_postHoc_shp( self, event ):
        self.temp = {}
        self.temp['clusters'] = self.project["postHoc"]["clusters"]
        if 'areas' in self.project['postHoc']:
            self.temp['clusters'] = pandas.concat(
                [self.temp['clusters'], pandas.DataFrame.from_dict(self.project['postHoc']['areas'])],
                axis=1)
            print(self.temp['clusters'].columns)
            self.temp['clusters'].rename(columns={0:'areas'},inplace=True)
            print(self.temp['clusters'].columns)
        if 'min_dist' in self.project['postHoc']:
            self.temp['clusters'] = pandas.concat(
                [self.temp['clusters'], pandas.DataFrame.from_dict(self.project['postHoc']['min_dist'].min(axis=1))],
                axis=1)
            print(self.temp['clusters'].columns)
            self.temp['clusters'].rename(columns={0:'min_dist'},inplace=True)
            print(self.temp['clusters'].columns)
        
        print(self.temp['clusters'])
        self.temp['clusters'].to_file(self.project['filepaths']['posthoc_shp'])

    def set_postHoc_output_choice(self):
        if self.postHoc_output_choice.GetSelection()==-1:
            selection=0
        else:
            selection=self.postHoc_output_choice.GetSelection()
        if os.path.isfile(self.project['filepaths']['marxan_input']):
            for line in open(self.project['filepaths']['marxan_input']):
                if line.startswith('SCENNAME'):
                    SCENNAME = line.replace('SCENNAME ', '').replace('\n', '')
                if line.startswith('NUMREPS'):
                    NUMREPS = int(line.replace('NUMREPS ', '').replace('\n', ''))
                elif line.startswith('OUTPUTDIR'):
                    OUTPUTDIR = line.replace('OUTPUTDIR ', '').replace('\n', '')
                    
            if not os.path.isdir(OUTPUTDIR):
                OUTPUTDIR = os.path.join(os.path.dirname(self.project['filepaths']['marxan_input']),OUTPUTDIR)

            fn = os.path.join(OUTPUTDIR, SCENNAME + "_best")
            
            if os.path.isfile(fn + '.csv') or os.path.isfile(fn + '.txt'):
                if self.postHoc_custom_choice.GetValue():
                    self.postHoc_output_choice.SetItems(['Custom Solution'])
                    self.postHoc_output_choice_txt.SetLabel("Output")
                    self.postHoc_output_choice.SetSelection(selection)
                else:    
                    self.postHoc_output_choice.SetItems(['Best Solution'] + 
                                                        ['Selection Frequency'] +
                                                        ["r" + "%05d" % t for t in range(NUMREPS+1)])
                    self.postHoc_output_choice_txt.SetLabel("Output: " + SCENNAME)
                    self.postHoc_output_choice.SetSelection(selection)
            else:
                self.postHoc_output_choice.SetItems(['No Output Available'])
                
                        
            

    def on_postHoc_file(self,event):
        self.project['filepaths']['posthoc'] = self.postHoc_file.GetPath()
        
    def on_postHoc_shp_file(self,event):
        self.project['filepaths']['posthoc_shp'] = self.postHoc_shp_file.GetPath()
        
    def on_plot_postHoc_spacing( self, event ):
        metric_type = "Distance to nearest cluster (km)"
        self.on_plot_freq(numpy.array(self.project["postHoc"]["min_dist"]).min(axis=1)/1000,metric_type)
        
    def on_plot_postHoc_sizes( self, event ):
        metric_type = "Cluster areas (km^2)"
        self.on_plot_freq(numpy.array(self.project["postHoc"]["areas"])/1000000,metric_type)
        
    def on_postHoc_custom_choice( self, event):
        self.postHoc_enable_custom()
        self.set_postHoc_output_choice()
        
    def postHoc_enable_custom(self):
        if self.postHoc_custom_choice.GetValue():
            self.postHoc_custom_file.Enable(True)
            self.postHoc_category_choice.Enable(False)
            self.postHoc_output_choice.Enable(False)
        else:
            self.postHoc_custom_file.Enable(False)
            self.postHoc_category_choice.Enable(True)
            self.postHoc_output_choice.Enable(True)


# ###########################  spec grid popup functions ###############################################################
    def on_customize_spec(self, event):
        if self.calc_metrics_pu.GetValue() & self.project['options']['metricsCalculated']:
            if hasattr(self,'spec_frame') and bool(self.spec_frame):
                self.spec_frame.Show()
            else:
                self.on_new_spec()
                self.spec_frame.Show()
        else:
            marxanconpy.warn_dialog(message="'Planning Units' not selected for metric calculations.")

    def on_new_spec(self):
        self.spec_frame = spec_customizer(parent=self)
        if self.project['options']['spec_set'] == "Proportion":
            self.spec_frame.spec_grid.SetColLabelValue(1,"prop")
        elif self.project['options']['spec_set'] == "Target":
            self.spec_frame.spec_grid.SetColLabelValue(1, "target")

        self.all_types = []
        if self.calc_metrics_pu.GetValue():
            if os.path.isfile(self.project['filepaths']['demo_pu_cm_filepath']):
                self.all_types += ['demo_pu']
            if os.path.isfile(self.project['filepaths']['land_pu_cm_filepath']):
                self.all_types += ['land_pu']
        else:
            marxanconpy.warn_dialog(message="'Planning Units' not selected for metric calculations.")
            return

        for self.type in self.all_types:
            metrics = list(self.project['connectivityMetrics']['spec_' + self.type])
            approved = ['discrete']
            metrics[:] = [m for m in metrics if any(a in m for a in approved)]

            self.spec_frame.keys = metrics

            targets = self.project['options']['targets'].split(',')
            if len(targets) < len(metrics):
                targets = numpy.resize(targets,len(metrics))
                # marxanconpy.warn_dialog(
                #     "There are more connectivity based conservation features than targets. Repeating given targets")
            elif len(targets) > len(metrics):
                targets = numpy.resize(targets, len(metrics))
                # marxanconpy.warn_dialog(
                #     "There are fewer connectivity based conservation features than targets. Selecting only first targets")

            for j in range(len(self.spec_frame.keys)):
                if j != self.spec_frame.spec_grid.GetNumberRows():
                    i = self.spec_frame.spec_grid.GetNumberRows()
                else:
                    i=j
                self.spec_frame.spec_grid.InsertRows(i)
                self.spec_frame.spec_grid.SetCellValue(i, 0, str(i + 1))
                self.spec_frame.spec_grid.SetCellValue(i, 1, str(float(targets[i])))
                self.spec_frame.spec_grid.SetCellValue(i, 2, str(1000))
                self.spec_frame.spec_grid.SetCellValue(i, 3, self.spec_frame.keys[j])

        self.spec_frame.spec_grid.AutoSize()
        w, h = self.spec_frame.spec_grid.GetSize()
        self.spec_frame.SetSize((w+16,h+75))

        self.project['spec_dat'] = pandas.DataFrame(
            numpy.full((self.spec_frame.spec_grid.GetNumberRows(), self.spec_frame.spec_grid.GetNumberCols()), None))

        if self.project['options']['spec_set'] == "Proportion":
            self.project['spec_dat'].columns = ["id", "prop", "spf", "name"]
        elif self.project['options']['spec_set'] == "Target":
            self.project['spec_dat'].columns = ["id", "target", "spf", "name"]


        for c in range(self.spec_frame.spec_grid.GetNumberCols()):
            for r in range(self.spec_frame.spec_grid.GetNumberRows()):
                self.project['spec_dat'].iloc[r, c] = self.spec_frame.spec_grid.GetCellValue(r, c)

        self.project['spec_dat'] = self.project['spec_dat'].to_json(orient='split')

class spec_customizer(gui.spec_customizer):
    def __init__(self, parent):
        gui.spec_customizer.__init__(self, parent)
        self.parent = parent
        # set the icon
        parent.set_icon(frame=self, rootpath=MCPATH)
        self.SetWindowStyle(wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT | wx.TAB_TRAVERSAL)

    def on_spec_ok(self, event):
        self.parent.project['spec_dat'] = pandas.DataFrame(
            numpy.full((self.spec_grid.GetNumberRows(),
                        self.spec_grid.GetNumberCols()), None))
        if self.parent.project['options']['spec_set'] == "Proportion":
            self.parent.project['spec_dat'].columns = ["id", "prop", "spf", "name"]
        elif self.parent.project['options']['spec_set'] == "Target":
            self.parent.project['spec_dat'].columns = ["id", "target", "spf", "name"]

        for c in range(self.spec_grid.GetNumberCols()):
            for r in range(self.spec_grid.GetNumberRows()):
                self.parent.project['spec_dat'].iloc[r, c] = self.spec_grid.GetCellValue(r, c)

        spec_copy = self.parent.project['spec_dat'].copy()
        self.parent.project['spec_dat'] = self.parent.project[
            'spec_dat'].to_json(orient='split')
        if self.parent.project['options']['spec_set'] == "Proportion":
            self.parent.project['options']['targets'] = ','.join(map(str,spec_copy['prop'].values))
        elif self.parent.project['options']['spec_set'] == "Target":
            self.parent.project['options']['targets'] = ','.join(map(str,spec_copy['target'].values))

        if not self.parent.project['options']['targets'] == self.parent.targets.GetValue():
            self.parent.targets.SetValue(self.parent.project['options']['targets'])

        self.Hide()

    def on_spec_cancel(self, event):
        self.Hide()

# ###########################  getting started popup functions #########################################################
class GettingStarted (gui.GettingStarted):
    def __init__(self, parent):
        gui.GettingStarted.__init__(self, parent)
        self.parent = parent
        # set the icon
        parent.set_icon(frame=self, rootpath=MCPATH)
        self.SetWindowStyle(wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT|wx.TAB_TRAVERSAL)

    def on_tutorial_button(self, event):
        self.parent.on_tutorial(event=None)

    def on_glossary_button(self, event):
        self.parent.on_glossary(event=None)

    def on_issue_button(self, event):
        self.parent.on_github(event=None)


# ########################### file popup viewer #####################################################################

class file_viewer(wx.Dialog):
    def __init__(self, parent, file, title):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=title, pos=wx.DefaultPosition,
                           size=wx.Size(-1, -1), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        file_mainsizer = wx.FlexGridSizer(0, 1, 0, 0)
        file_mainsizer.SetFlexibleDirection(wx.BOTH)
        file_mainsizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.file_grid = wx.grid.Grid(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)

        # Load file
        df = marxanconpy.read_csv_tsv(file)

        # Grid
        self.file_grid.CreateGrid(df.shape[0], df.shape[1])
        self.file_grid.EnableEditing(False)
        self.file_grid.EnableGridLines(True)
        self.file_grid.EnableDragGridSize(False)
        self.file_grid.SetMargins(0, 0)

        # Columns
        self.file_grid.EnableDragColMove(False)
        self.file_grid.EnableDragColSize(True)
        self.file_grid.SetColLabelSize(30)
        for col, label in enumerate(df.columns):
            self.file_grid.SetColLabelValue(col,label)
            for index in df.index:
                self.file_grid.SetCellValue(index, col, str(df.iloc[index, col]))
        self.file_grid.AutoSizeColumns()
        self.file_grid.SetColLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # Rows
        self.file_grid.EnableDragRowSize(True)
        self.file_grid.SetRowLabelSize(80)
        self.file_grid.SetRowLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # Cell Defaults
        self.file_grid.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        file_mainsizer.Add(self.file_grid, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 5)

        file_button_sizer = wx.FlexGridSizer(0, 3, 0, 0)
        file_button_sizer.AddGrowableCol(0)
        file_button_sizer.SetFlexibleDirection(wx.BOTH)
        file_button_sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.spacer_text = wx.StaticText(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        self.spacer_text.Wrap(-1)
        file_button_sizer.Add(self.spacer_text, 0, wx.ALL, 5)

        self.file_ok = wx.Button(self, wx.ID_ANY, u"OK", wx.DefaultPosition, wx.DefaultSize, 0)
        file_button_sizer.Add(self.file_ok, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        file_mainsizer.Add(file_button_sizer, 1, wx.EXPAND, 5)

        self.SetSizer(file_mainsizer)
        self.Layout()
        file_mainsizer.Fit(self)

        self.Centre(wx.BOTH)

        # Connect Events
        self.file_ok.Bind(wx.EVT_BUTTON, self.on_file_ok)

        self.Show()

    def on_file_ok(self,event):
        self.Hide()

# ######################################################################################################################

# ########################## debug mode ################################################################################

class RedirectText(object):
    def __init__(self, aWxTextCtrl):
        self.out = aWxTextCtrl
        self.stdout = sys.stdout
        self.stderr = sys.stderr

    def write(self, string):
        print(string, file=self.stdout)
        wx.CallAfter(self.out.WriteText, string)

    def flush(self):
        # do nothing...
       None

class LogForm(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, wx.ID_ANY, "Debbuging Console")
        self.Bind(wx.EVT_CLOSE, self.__close)
        parent.set_icon(frame=self, rootpath=MCPATH)

        # Add a panel
        panel = wx.Panel(self, wx.ID_ANY)
        log = wx.TextCtrl(panel, wx.ID_ANY, size=(350, 350), style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)

        # Add widgets to a sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(log, 1, wx.ALL | wx.EXPAND, 5)
        panel.SetSizer(sizer)

        # redirect text here
        redir = RedirectText(log)
        sys.stdout = redir
        sys.stderr = redir

    def __close(self, event):
        self.Hide()

# ##########################  run the GUI ##############################################################################
app = wx.App(False)

# create an object of CalcFrame
frame = MarxanConnectGUI(None)
# show the frame
frame.Show(True)
# start the applications
app.MainLoop()

# stop the app
app.Destroy()

