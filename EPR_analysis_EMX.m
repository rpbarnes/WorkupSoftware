function EPR_analysis_EMX
 %Batch EPR analysis accepts input of a spectrum as an ascii file
 %performs double integration and normalizes the spectra by 2nd integral
 %and intensity of the central line two new ascii files are generated for
 %each spectrum.
 %Summurizes the following outputs in an excel file:
 % central field, p2p width of central line, 
 % intensity of the mobile and slow peaks on both left and right sides of
 % the spectra and their positions.
 %Currently works with any number of files in a given folder
 
 %ver 1.0 written by Ilia Kaminker Feb-2015
clear all
close all
%% User input section

FolderName = '/Users/StupidRobot/exp_data/ryan_cnsi/epr/150404_ProbeTestV2-1/';

FileNames{1} ='150402_200uM_4OHT_ProbeV2-1BeforeExpoxyAndAirFlowConnector';
FileNames{2} ='AfterMovingStuff';
FileNames{3} ='AfterscrapingEpoxyOff';
FileNames{4} ='SomethingChanged';
% FileNames{5} ='CheY_N62C_None_350uM_13-4mm_NoUrea';
% FileNames{6} ='CheY_N121C_None_363uM_14-8mm_NoUrea';
% FileNames{7} ='140922_CheY_E37C_FliM_241uM_RT_EPR';
% FileNames{8} ='140922_CheY_E37C_10mMFliM_241uM_RT_EPR';
% FileNames{9} ='140921_CheY_E37C_P2_241uM_RT_EPR';

% FileNames{1} ='CheY_D41C_FliM_217uM_14mm_10dB';
% FileNames{2} ='CheY_D41C_None_217uM_13-8mm_10dB';
% FileNames{3} ='CheY_D41C_P2_217uM_14-4mm_10dB';
% FileNames{4} ='CheY_M17C_FliM_202uM_14-4mm_10dB';
% FileNames{5} ='CheY_M17C_None_202uM_14-3mm_10dB';
% FileNames{6} ='CheY_M17C_P2_202uM_14mm_10db';
% FileNames{7} ='CheY_N121C_FliM_218uM_12-5mm_10dB';
% FileNames{8} ='CheY_N121C_None_218uM_13-5mm_10dB';
% FileNames{9} ='CheY_N121C_P2_218uM_13mm_10dB';

% FileNames{1} = '150206-ODNP1-0mM-NaCl_100mM_AcA_pH3';
% FileNames{2} ='150206-ODNP1-300mM-NaCl_100mM_AcA_pH3';
% FileNames{3} = '150206-ODNP1-600mM-NaCl_100mM_AcA_pH3_10scans';
% FileNames{4} ='150206-ODNP1-900mM-NaCl_100mM_AcA_pH3_10scans';

Summary_FileName = 'test.xls';


% FolderName = 'C:\Users\Ilia\Dropbox\Work\Song-I\Nikki Batch EPR analysis\';
% FileNames{1} = '2014-08-06_WT-A2a-H-SL-NL_IMAC-XAC_No_Ligand_166uM_6 days 4C';
% FileNames{2} = '2014-09-03_WT-A2a-H-SL-NECA_IMAC-XAC_DMSO_Y50._BC';
% FileNames{3} = '2014-09-03_WT-A2a-H-SL-XAC_IMAC-XAC_DMSO_Y95_BC';
% FileNames{4} = '2014-11-22_C394S-A2a-H-SL-NECA_DMSO_Y30_BC';
% FileNames{5} = '2014-11-22_C394S-A2a-H-SL-NL_NECA_Y20_BC';
% FileNames{6} = '2014-06-04_C394S-A2a-H-SL-NL_IMAC-XAC_CGS21680_basecorr';
% FileNames{7} = '2014-06-04_C394S-A2a-H-SL-NL_IMAC-XAC_NECA_basecorr';
% FileNames{8} = '2014-06-04_C394S-A2a-H-SL-NL_IMAC-XAC_NoLig_bascorr';
% FileNames{9} = '2014-06-04_C394S-A2a-H-SL-NL_IMAC-XAC_XAC_basecorr';
% FileNames{10} = '2014-06-04_WT-A2a-H-SL-5min_IMAC-XAC_NoLig_basecorr';
% FileNames{11} = '2014-06-04_WT-A2a-H-SL-10min_IMAC-XAC_NoLig._basecorr';
% FileNames{12} = '2014-06-04_WT-A2a-H-SL-30min_IMAC-XAC_NECA_basecorr';
% FileNames{13} = '2014-06-04_WT-A2a-H-SL-30min_IMAC-XAC_NoLig_basecorr';


%Summary_FileName = 'test_summary.xls';

verbosity = ones(1,length(FileNames));

%to get more info for a given spectrum set verbosity for the same index
%equal to 1

%verbosity(6:13) = ones(1,8);

%% here the program starts

if exist(Summary_FileName,'file') == 2
    promt = ['The dataset "', Summary_FileName,'" already exists! overwrite? press "y" to continue.'];
    str = input(promt,'s');
    if ~strcmp(str,'y')
        disp('aborting');
        return
    else
        disp('owerwriting');    
    end
end
    
Analysed = cell(length(FileNames),1);
Output_summary = cell(1,1);

for l=1:length(FileNames)
    FileName = [FolderName, FileNames{l},'.spc'];
    [Data.data(:,1), Data.data(:,2)] = eprload(FileName); %automatic loading of ascii files. "Data.data" contains the actual 1024x2 dataset
    Analysed{l} = spectrum_analysis(Data.data(:,1),Data.data(:,2),1,FileNames{l},verbosity(l));
    Filename_output = [FolderName, FileNames{l}];
    [Output_summary] = generate_output(Analysed{l},Output_summary,Filename_output);

end

disp(['saving summary as: ' Summary_FileName]);
% csvwrite(Summary_FileName,Output_summary); % saving summary in excel format

f=1; %figure counter
figure(f); f=f+1;
plot(1:length(FileNames),for_plot(Analysed,'integral2'),'s');
title('Integrated Intensity vs entry index');

%% plotting overlay
figure(f); f=f+1;
hold on

colors = ['b', 'g', 'r', 'm', 'c', 'y', 'k'];
for l=1:length(FileNames)
    plot(Analysed{l}.x_data,Analysed{l}.corrected./Analysed{l}.integral2,colors(mod(l-1,7)+1));
end

hold off
xlabel('Magnetic Field / G');
ylabel('Signal Intensity / a.u.');
title('Spectral Overlay');
legend(FileNames);

end

function [Data] = spectrum_analysis(x_data,Y_data,Corr_order,FileName,verbosity)
%% Processing

% this will be changed to a sepatate function for batch processing

%% baseline correction

Y_data = Y_data(10:end-10); %cropping firts and last 10 points since they often contain glitches

x_data = x_data(10:end-10); %cropping firts and last 10 points since they often contain glitches

lD = length(Y_data); %length of dataset (usually 1024)
BL_window = [1:1:round(lD/10) lD-round(lD/10):1:lD]; % window for baseline correstion I assume that first 10% and last 10% of data are signal free

BL_P = polyfit(x_data(BL_window,1),Y_data(BL_window),Corr_order); %obtaining coefficients of polynomial used for baseline correction

BL = polyval(BL_P,x_data); %evaluating the polynomial over the whole x-axis

f = 1; %figure counter


Data.corrected = Y_data-BL; %baseline subtraction

if verbosity
    figure(f); f = f+1;
    plot(x_data,Y_data,x_data,BL,x_data,Data.corrected);
    xlabel('magnetic field / G');
    ylabel('signal intensity / a.u.');
    title('baseline correction');
    legend('original data','baseline','corrected data');
end


Data.integral1=cumtrapz(x_data, Data.corrected); %generating curve for 1st integral


BL_P_int = polyfit(x_data(BL_window),Data.integral1(BL_window),Corr_order); %%obtaining coefficients of polynomial used for baseline correction

BL_int = polyval(BL_P_int,x_data);%evaluating polynomial over the whole magnetic field range

Data.int1_corrected = Data.integral1-BL_int; %Subtarcting baseline from integral


if verbosity
    figure(f); f = f+1;
    plot(x_data,Data.integral1,x_data,BL_int,x_data,Data.int1_corrected);
    xlabel('magnetic field / G');
    ylabel('signal intensity / a.u.');
    title('1st integral');
    legend('1st integrtal','baseline','corrected 1st integral');

end


%% Data smoothing

Data.smoothed = smooth(Data.corrected,5,'savgol');


if verbosity
    figure(f); f = f+1;
    plot(x_data,Data.corrected, x_data,Data.smoothed );
    xlabel('magnetic field / G');
    ylabel('signal intensity / a.u.');
    title('center field adjustment');
    legend('original','smoothed');
end


%% parameters for output

Data.integral2 = trapz(x_data,Data.int1_corrected); %second integral

[Data.max_intens, max_ind] = max(Data.smoothed(400:end-400)); %maximum intensity I assume it is for the central line
max_ind = max_ind + 399;

[Data.min_intens, min_ind] = min(Data.smoothed(400:end-400)); %minimun intensity again I assume this will be for the central line
min_ind = min_ind + 399;

Data.center_int = Data.max_intens - Data.min_intens; %Total intensity of the central line

[~, ind_center_field] = min(abs(Data.corrected(max_ind:min_ind))); %finding the index of the center field position rlative to the maximum of the central line

ind_center_field = ind_center_field+max_ind; %index of the center field position relaitve to the whole spectrum

Data.center_field = x_data(ind_center_field); %Value of the central field in G

Data.center_p2p = x_data(min_ind)-x_data(max_ind); %width of the central line in G

Data.x_data = x_data - Data.center_field; %correcting the x-axis to make center field position to be equal 0

%% finding mobile and immobile components positions and intensity

[Data.mobile_max, Data.mobile_max_position, Data.mobile_min, Data.mobile_min_position] = find_mobile(Data.x_data, Data.smoothed);
[Data.slow_max, Data.slow_max_position, Data.slow_min, Data.slow_min_position] = find_slow(Data.x_data, Data.smoothed);

if Data.mobile_max_position+Data.mobile_min_position > 1
    disp(['warning mobile component is ill defined for:', FileName]); % checking consistensy between two peaks
end

n_level = noise_level(Data.x_data, Data.corrected);

if Data.mobile_max < Data.slow_max+0.5*n_level % assuming that if mobile peak is smaller thatn slow motion component it is negligible.
    disp(['no mobile component found for:', FileName]);
    Data.mobile_max = [];
    Data.mobile_max_position = [];
    Data.mobile_min = [];
    Data.mobile_min_position = [];
    
end



if Data.slow_max < n_level*3 %assuming that if immobile peak is less than two time higher than the std noise level in is negligible
    Data.slow_max = [];
    Data.slow_max_position = [];
    Data.slow_min = [];
    Data.slow_min_position =[];
end

  
if verbosity
    figure(f); f = f+1;
    hold on
    % raw and smoothed data
    plot(Data.x_data,Data.corrected,Data.x_data,Data.smoothed);
    y1=get(gca,'ylim');
    
    %vertical lines for the max and min of the central line
    x1 = Data.x_data(max_ind);
    plot([x1 x1],y1,'r');
    x1 = Data.x_data(min_ind);    
    plot([x1 x1],y1,'r');
    
    %horizontal lines for the max and min of the central line 
    plot(Data.x_data,Data.smoothed(max_ind),'m');
    plot(Data.x_data,Data.smoothed(min_ind),'m');  
    
    if ~isempty(Data.mobile_max)
        %vertical and horizonatl lines for the mobile peak max position
        x1 = Data.mobile_max_position;    
        plot([x1 x1],y1,'c');
        plot(Data.x_data,Data.mobile_max,'c');  

        %vertical and horizonatl lines for the mobile peak min position
        x1 = Data.mobile_min_position;    
        plot([x1 x1],y1,'c');
        plot(Data.x_data,Data.mobile_min,'c');  
    end
    
    if ~isempty(Data.slow_max)
        %vertical and horizonatl lines for the slow peak max position
        x1 = Data.slow_max_position;    
        plot([x1 x1],y1,'k');
        plot(Data.x_data,Data.slow_max,'k');  

        %vertical and horizonatl lines for the slow peak min position
        x1 = Data.slow_min_position;    
        plot([x1 x1],y1,'k');
        plot(Data.x_data,Data.slow_min,'k');  
    end
    
    xlabel('magnetic field / G');
    ylabel('signal intensity / a.u.');
    title('center field adjustment');
end
 
Data.data = [];

if verbosity
    pause
    close all
end


%% Normalizing mobile / slow data for output  

Data.mobile_max = Data.mobile_max/Data.max_intens; 

Data.mobile_min = Data.mobile_min/Data.max_intens;

Data.slow_max = Data.slow_max/Data.max_intens; 

Data.slow_min = Data.slow_min/Data.max_intens;


%% output format
% Filename ; 2nd integral;center field; central line p2p windth; central line p2p intensity; mobile peak
% intensity; immobile peak intensity; 

%NOrmalized spectra by 2nd integral 
%Normalized by central line intensity
end

function [Output_array] = generate_output(Data,Data_Array,Filename)

%% saving ascii file normalized by the 2nd integral

New_filename = [Filename,'_norm_2nd_int.asc'];
data(:,1) = Data.x_data;
data(:,2) = Data.corrected/Data.integral2;
save(New_filename,'data','-ascii');

%% saving ascii file normalized by the maximum intensity

New_filename = [Filename,'_norm_max_intens.asc'];
data(:,1) = Data.x_data;
data(:,2) = Data.corrected/Data.max_intens;
save(New_filename,'data','-ascii');

%% Generating data to add to the summary output format:
% Filename ; 2nd integral;center field; central line p2p windth; central line p2p intensity; mobile peak
% intensity; immobile peak intensity; 

Output_data{1} = [Filename,'.asc'];
Output_data{2} = Data.integral2;
Output_data{3} = Data.center_field;
Output_data{4} = Data.center_p2p;
Output_data{5} = Data.mobile_max;
Output_data{6} = Data.mobile_max_position;
Output_data{9} = Data.mobile_min;
Output_data{10} = Data.mobile_min_position;
Output_data{7} = Data.slow_max;
Output_data{8} = Data.slow_max_position;
Output_data{11} = Data.slow_min;
Output_data{12} = Data.slow_min_position;

if isempty(Data_Array{1,1}) %if the data array was not created yet
    Output_array(1,:) = {'Filename' '2nd integral' 'center field' 'center line peak to peak'...
        'intens. mobile pos.' 'field mobile pos.' 'intens. slow. pos.' 'field slow pos.'...
        'intens. mobile neg.' 'field mobile neg.' 'intens. slow. neg.' 'field slow neg.'};%Column headers
    Output_array(2,:) = Output_data;%outputing the newly created data array
else
    [rows,~] = size(Data_Array); %number of rows in existing array
    Data_Array(rows+1,:) = Output_data; %Adding data to a new row
    Output_array = Data_Array; %outputing the whole new array
end
    

%disp(Output_array);


end

function [data] = for_plot(Data,field_name)

% Data is a cell array of structures
% field_name is one of the inpouts in the structure that has a scalar value
%data - output matrix n x 1 where n=lenbgth(Data);
data = zeros(1,length(Data));
for l=1:length(Data);
   eval(['data(l) = Data{l}.',field_name,';']);
end

end

function [mobile_max, mobile_max_position, mobile_min, mobile_min_position] = find_mobile(x_data, y_data)


ind_mobile_1 =  find((x_data>16) & (x_data<20)); %defining positive region to look for mobile component
ind_mobile_2 =  find((x_data>-20) & (x_data<-16)); %defining negative region to look for mobile component


[mobile_max, mobile_max_ind]= max(y_data(ind_mobile_2)); %looking for the  maximum in the negative region
[mobile_min, mobile_min_ind]= min(y_data(ind_mobile_1)); %looking for the  minimum in the positive region

mobile_max_position = x_data(mobile_max_ind+ind_mobile_2(1));
mobile_min_position = x_data(mobile_min_ind+ind_mobile_1(1));

end

function [slow_max, slow_max_position, slow_min, slow_min_position] = find_slow(x_data, y_data)


ind_slow_1 =  find((x_data>35) & (x_data<42)); %defining positive region to look for slow component
ind_slow_2 =  find((x_data>-32) & (x_data<-25)); %defining negative region to look for slow component


[slow_max, slow_max_ind]= max(y_data(ind_slow_2)); %looking for the  maximum in the negative region
[slow_min, slow_min_ind]= min(y_data(ind_slow_1)); %looking for the  minimum in the positive region

slow_max_position = x_data(slow_max_ind+ind_slow_2(1));
slow_min_position = x_data(slow_min_ind+ind_slow_1(1));

end

function [n_level] = noise_level(x_data, y_data)
ind_baseline =  ((x_data>-70) & (x_data<-50)) | ((x_data>50) & (x_data<70)); %defining positive region to look for mobile component
n_level = std(y_data(ind_baseline));
end