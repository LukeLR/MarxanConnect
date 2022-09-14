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

### `tutorial.MarCon`
JSON file: Marxan Connect project
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
