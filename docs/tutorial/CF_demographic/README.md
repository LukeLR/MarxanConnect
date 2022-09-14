# CF_demographic tutorial files
Some explaination on the files contained in this tutorial folder

## Project root
`DebugTraceFile_MarOpt.txt`: Marxan debug output

`hexFlow.csv`: 653x653 Matrix
- probably containing connectivity values for each pair of planning units?

`hex_planning_units.dbf`: 21x653 Matrix
- contains metadata for each planning unit
- also present in the shapefile

`hex_planning_units.prj`: sidecar file for `.shp`-file
- contains information on the coordinate projection used in the shapefile
- `.shp` doesn't support such information

`hex_planning_units.shp`: shapefile containing coordinates of planning units and metadata

`hex_planning_units.shx`: index file for `.shp`-file

`input_connect.dat`: Input file for annealing program, contains parameters

`input_no_connect.dat`: Identical to `input_connect.dat`, only `_connect` stripped from filename parameters

`MarOptTotalAreas.csv`: Metadata for each species:
- `spname`, `spindex` , `totalarea`, `reservedarea`, `excludedarea`, `targetarea`, `totalocc`, `reservedocc`, `excludedocc`, `targetocc`

### Marxan Connect project files
`tutorial.MarCon`: JSON file: Marxan Connect project
- `connectivityMetrics`
	- `best_solution`: list of 653 binary values
	- `boundary`: empty dict
	- `select_freq`: list of 653 integer values
	- `spec_demo_pu`
		- `google_demo_pu`: list of 653 float values
		- `google_demo_pu_discrete_median_to_maximum`: list of 653 float values
	- `status`: list of 653 binary values, all zero
- `filepaths`, `operating_system`
- `options`: parameters for Marxan (and Marxan Connect?), e.g. number of runs
- `postHoc`: small table containing postHoc data
	- `Planning Area`, `Solution`, `Percent` for metrics `Planning Units`, `Connections`, `Graph Density`, `Eigenvalue`
	- tab `7) Post-Hoc Evaluation` in Marxan Connect
- `spec_dat`: single-row table
	- contains list of connectivity-based conservation features available for export (tab `4) Pre-Evaluation` in Marxan Connect)
	- `google_demo_pu_discrete_median_to_maximum`:
		- `prop`: 0.25
		- `spf`: 1000
- `version`: version information for `MarxanConnect` and `marxanconpy`

`tutorial_no_connect.MarCon`: Marxan Connect project without connectivity (?)
- same information with different values, file paths and some parameters changed

## input folder
`bound.dat`: 3601 pairs of planning units and a boolean variable (always one)
- Probably whether they share a common boundary?

`pu.dat`: information on the planning units
- `cost`: always 1
- `status`: always 0
- `xloc` and `yloc`: float values

`puvspr_connect.dat`: Amount of species per planning unit
- May contain multiple rows per planning unit (different species)

`puvspr.dat`: Same thing but without connectivity metrics applied

`spec_connect.dat`: Information on each species
- `prop`: Float in [0,1]
- `spf`: Always 1000
- `name`

`spec.dat`: Same thing but without `google_demo_pu_discrete_median_to_maximum` (that apparently is treated as a species?)

## output folder

### `connect_*`-files
`connect_r*.txt`: CSV file holding binary variables whether each planning unit is part of the solution of the corresponding run

`connect_best.txt`: copy of the `connect_r*.txt` file corresponding to the best solution

`connect_log.dat`: Log output of Marxan containing information on each run
- `Tinit`
- `Tcool`
- Value
- Cost
- PUs
- Connection
- Missing
- Shortfall
- Penalty
- MPM

`connect_mv*.txt`: CSV file on each species for each run's solution
- Conservation Feature
- Feature Name
- Target
- Amount Held
- Occurrence Target
- Occurrences Held
- Separation Target
- Separation Archieved
- Target Met
- MPM

`connect_mvbest.txt`: copy of the `connect_mv*.txt` file corresponding to the best solution

`connect_sen.dat`: Some debug output / parameter information from Marxan (?)

`connect_ssoln.txt`: CSV holding integers for each planning unit
- might be frequencies how often a planning unit was part of a solution

`connect_sum.txt`: CSV with aggregated information on each run:
- run number
- score
- cost
- planning units
- connectivity
- connectivity total
- connectivity in
- connectivity edge
- connectivity out
- connectivity in fraction
- penalty
- shortfall
- missing values
- MPM

`pu_connect_best_solution.png`: PNG plot of PUs on basemap with selected PUs highlighted

`pu_connect_selection_frequency.png`: PNG plot of PUs on basemap with color scale indicating selection frequency

`pu_connect.cpg`: File containing which text encoding is used

`pu_connect.csv`: CSV file containing for each PU:
- value for each species
- polygon coordinates
- `google_demo_pu_discrete_median_to_maximum`: binary variable
- `best_solution` (binary)
- selection frequency (float)
- status (always 0)

`pu_connect.dbf`: Same information in FoxBase+/dBase III format

`pu_connect.prj`: Information on coordinate projection used in shapefile

`pu_connect.shp`: Same information as ESRi shapefile

`pu_connect.shx`: shapefile index

### `no_connect_*`-files
A copy of this file structure exists for the non-connectivity version (?)
