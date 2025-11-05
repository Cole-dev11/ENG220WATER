clear;

%Importing water level data
raw_wl_data = readtable("water_level.csv");
% Keeping only the columns we need
cut_wl_data = raw_wl_data(:,[2,4,5]);

%Importing well data
well_data = readtable("well_data.csv");
cut_well_data = well_data(:,[3,4,6,7,8]);

% Merging tables with 'Well_Name' key
T_combined = innerjoin(cut_wl_data, cut_well_data, 'Keys', 'Well_Name');

% Remove the WellName column 
T_combined.Well_Name = [];

% Writing output to file
writetable(T_combined, 'combined_data.csv');