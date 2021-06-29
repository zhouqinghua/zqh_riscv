global env
fsdbDumpfile "$env(FSDB_FN)"
fsdbDumpvars 0 "$env(FSDB_TOP)" "+all"
fsdbDumpSVA 0 "$env(FSDB_TOP)"
run   
