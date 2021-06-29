verdiWindowResize -win $_Verdi_1 "65" "24" "1855" "1056"
debImport "-notice" "-line" "+lint=all,noVCDE,noONGS,noUI,noNS,noVNGS" \
          "-error=noIOPCWM" "+v2k" "+vcs+lic+wait" "-sverilog" \
          "-timescale=1ns/10ps" "+define+sg125" "+define+den1024Mb" \
          "+define+x8" "-pvalue+MEM_BITS=12" "-pvalue+DEBUG=1" "+incdir+./" \
          "./ddr3.v" "./tb.v" "-P" \
          "/home/zqh/verdi/K-2015.09-SP1-1/share/PLI/VCS/LINUX64/novas.tab" \
          "/home/zqh/verdi/K-2015.09-SP1-1/share/PLI/VCS/LINUX64/pli.a" "-l" \
          "./cmp.log" "-debug_pp"
wvCreateWindow
wvSetPosition -win $_nWave2 {("G1" 0)}
wvOpenFile -win $_nWave2 \
           {/home/zqh/risc-v/zqh_riscv/verif/common/vips/DDR3_model/zqh_ddr3.fsdb}
wvRestoreSignal -win $_nWave2 \
           "/home/zqh/risc-v/zqh_riscv/verif/common/vips/DDR3_model/aaa.rc" \
           -overWriteAutoAlias on
verdiDockWidgetMaximize -dock windowDock_nWave_2
wvZoomAll -win $_nWave2
wvSelectSignal -win $_nWave2 {( "G4" 5 )} 
wvZoom -win $_nWave2 8780.026865 41580.881946
wvZoom -win $_nWave2 32092.355289 39290.547926
wvZoom -win $_nWave2 36017.554266 36849.265635
wvZoom -win $_nWave2 36363.236464 36767.684636
wvZoom -win $_nWave2 36561.930454 36623.791189
wvZoom -win $_nWave2 36586.870152 36601.268328
wvSelectSignal -win $_nWave2 {( "G1" 2 )} 
wvScrollDown -win $_nWave2 0
wvScrollDown -win $_nWave2 0
wvScrollDown -win $_nWave2 0
wvScrollDown -win $_nWave2 0
wvScrollDown -win $_nWave2 0
wvScrollDown -win $_nWave2 0
wvSelectSignal -win $_nWave2 {( "G3" 6 )} 
wvZoomOut -win $_nWave2
wvZoomOut -win $_nWave2
wvZoom -win $_nWave2 36585.810934 36603.668024
wvZoomOut -win $_nWave2
wvZoomOut -win $_nWave2
wvZoomOut -win $_nWave2
verdiDockWidgetRestore -dock windowDock_nWave_2
srcDeselectAll -win $_nTrace1
debReload
verdiDockWidgetMaximize -dock windowDock_nWave_2
wvZoomOut -win $_nWave2
wvZoom -win $_nWave2 36577.520672 36683.446017
wvSetCursor -win $_nWave2 36604.376225 -snap {("G3" 4)}
wvZoom -win $_nWave2 36598.652911 36657.735127
wvSelectSignal -win $_nWave2 {( "G1" 2 )} 
wvZoomOut -win $_nWave2
wvSelectSignal -win $_nWave2 {( "G3" 4 )} 
wvSetMarker -win $_nWave2 36608.125000
wvSetMarker -win $_nWave2 36615.625000
wvSetMarker -win $_nWave2 36628.750000
wvZoom -win $_nWave2 36620.778047 36647.396967
verdiWindowResize -win $_Verdi_1 "65" "24" "1549" "824"
verdiWindowResize -win $_Verdi_1 "65" "24" "1553" "828"
verdiWindowResize -win $_Verdi_1 "65" "24" "1855" "1056"
wvZoomOut -win $_nWave2
wvZoomOut -win $_nWave2
wvZoomOut -win $_nWave2
wvZoom -win $_nWave2 36580.893920 36610.278730
wvSetCursor -win $_nWave2 36591.348366 -snap {("G4" 3)}
wvZoomOut -win $_nWave2
wvZoomOut -win $_nWave2
wvZoomOut -win $_nWave2
wvZoom -win $_nWave2 36581.614495 36618.547025
wvSelectSignal -win $_nWave2 {( "G4" 3 )} 
wvSelectSignal -win $_nWave2 {( "G1" 2 )} 
wvZoomOut -win $_nWave2
wvZoomOut -win $_nWave2
wvZoomOut -win $_nWave2
wvZoom -win $_nWave2 36617.886967 36647.604912
wvZoom -win $_nWave2 36628.459935 36635.648565
wvSetCursor -win $_nWave2 36630.168953 -snap {("G4" 3)}
wvSelectSignal -win $_nWave2 {( "G4" 3 )} 
wvSelectSignal -win $_nWave2 {( "G1" 2 )} 
wvZoomOut -win $_nWave2
wvZoomOut -win $_nWave2
wvZoom -win $_nWave2 36627.261830 36638.233006
wvSelectSignal -win $_nWave2 {( "G4" 2 )} 
wvSelectSignal -win $_nWave2 {( "G4" 3 )} 
wvSelectSignal -win $_nWave2 {( "G4" 2 )} 
wvSelectSignal -win $_nWave2 {( "G4" 2 )} 
wvSelectSignal -win $_nWave2 {( "G4" 3 )} 
wvSelectSignal -win $_nWave2 {( "G4" 2 )} 
verdiWindowResize -win $_Verdi_1 "65" "24" "1549" "824"
verdiWindowResize -win $_Verdi_1 "65" "24" "1855" "1056"
verdiDockWidgetRestore -dock windowDock_nWave_2
srcDeselectAll -win $_nTrace1
debReload
verdiWindowResize -win $_Verdi_1 "65" "24" "1549" "824"
verdiWindowResize -win $_Verdi_1 "65" "24" "1553" "828"
verdiWindowResize -win $_Verdi_1 "65" "24" "1855" "1056"
verdiDockWidgetMaximize -dock windowDock_nWave_2
wvScrollDown -win $_nWave2 1
wvScrollDown -win $_nWave2 1
wvScrollDown -win $_nWave2 1
wvScrollDown -win $_nWave2 1
wvScrollDown -win $_nWave2 1
wvScrollUp -win $_nWave2 5
wvZoomOut -win $_nWave2
wvZoomOut -win $_nWave2
wvZoomOut -win $_nWave2
wvZoomOut -win $_nWave2
wvSetCursor -win $_nWave2 36603.345031 -snap {("G3" 4)}
wvZoom -win $_nWave2 36592.984885 36673.531374
wvSetCursor -win $_nWave2 36635.501111 -snap {("G4" 3)}
wvSelectSignal -win $_nWave2 {( "G1" 1 )} 
wvZoomOut -win $_nWave2
wvZoomOut -win $_nWave2
verdiWindowResize -win $_Verdi_1 "65" "24" "1549" "824"
verdiWindowResize -win $_Verdi_1 "65" "24" "1553" "828"
verdiWindowResize -win $_Verdi_1 "65" "24" "1855" "1056"
debExit
