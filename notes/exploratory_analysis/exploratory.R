# Doesn't get the whole file malleably available
# rather, produces a matrix
# First leftmost column is the time stamps (1)
# The rest to the right are EEG channel inputs (2:112)
eeg_meda <- function(inputpath, outname, start_elec, end_elec, start_time, end_time) {
    
    # first install required package to handle
    # hdf5 format used in the files provided
    if(suppressWarnings(!require("h5"))) {
        install.packages("h5");
        library(h5);
    }
    require(devtools)
    devtools::install_github("neurodata/meda")
    #require(meda)
    require(ggplot2)
    
    file <- h5file(inputpath, "r");
    outFile <- paste0("~/hopkins/orange-panda/notes/exploratory_analysis/",
                      inputpath, "/", outname)
    
    resultdata <- data.matrix(data.frame(file["result/data"][]))
    #timeseries <- data.matrix(data.frame(file["result/times"][], file["result/data"][]));
    #colnames(timeseries) <- c("Time", colnames(timeseries)[2:112]);
    #return(timeseries);
    if(end_time == 0) {
        end_time = nrow(resultdata)
    }
    sample_dat <- resultdata[seq(from=start_time,to=end_time,by=30), start_elec:end_elec]
    bool <- !apply(sample_dat, 2, function(x) sd(x) == 0)
    sample_dat <- sample_dat[, bool]
    meda::genHTML(sample_dat, outFile)
}

run_meda <- function(file_name, start_elec, end_elec, start_time, end_time) {
    eeg_meda(paste0(file_name, ".mat"), 
             paste0("nicolas_", file_name, "_elec",start_elec,"s",
                    end_elec,"e", "_time", start_time, "s", end_time, "e.html"),
             start_elec, end_elec, start_time, end_time)
}

run_scripts <- function() {
    patients = c(
        "gp_A00051826001",
        "bip_A00053375001",
        "gip_A00051826005",
        "gip_A00051955001",
        "gip_A00053440001",
        "gp_A00051886001",
        "oip_A00053398_part2001",
        "gip_A00054417001",
        "bip_A00054215001",
        "gip_A00054207001",
        "gp_A00054039001",
        "gp_A00054023001",
        "gp_A00053990001",
        "oip_A00053909001",
        "gp_A00053597001",
        "oip_A00053480001",
        "gip_A00053460001"
    ) 
    
    for(patient in patients) {
        run_meda(patient,start_elec=0,end_elec=40,
                 start_time=0,end_time=8000)
        run_meda(patient,start_elec=40,end_elec=80,
                 start_time=0,end_time=8000)
        run_meda(patient,start_elec=80,end_elec=111,
                 start_time=0,end_time=8000)
    }
}

run_scripts()
traceback()
