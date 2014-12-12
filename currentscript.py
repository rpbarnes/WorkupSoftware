import os
from h5nmr import *
import nmrfit
import csv

close('all')
fl = figlistl()
# DNP path and file name
# The sample name should be date_sample_site_concentration_bindingPartner
header = '/Users/StupidRobot/exp_data/'
path = 'ryan_cnsi/nmr/'
name = '140724_CheY_CtermC_400uM_ODNP'
fullPath = header + path + name
dnpExps = r_[5:35]
t1Exp = r_[36:46,304]
integrationWidth = 1.5e2
saveData = True
deleteOldSaveNew = True
# Data Hierarchy Make sure you change this or you going to be sad face
# Structured like so
# h5FileName ->> enhancement(labels=expNum), t1Series(labels=expNum), t1Integrals ### Just save the enhancement integrals and the T1 series ad integrals
h5FileName = name + '.h5' # write to file named after the experiment


#{{{ Index Files
files = listdir(fullPath)
### Just weed out the power files from the titles, we already know what they are
for index,item in enumerate(files):
    if item == 't1_powers.mat':
        files.pop(index)
for index,item in enumerate(files):
    if item == 'power.mat':
        files.pop(index)
files = [double(i) for i in files]
files.sort()
expTitles = []
for i in files:
    expTitles.append([load_title(fullPath + '/' + str(i).split('.')[0]),str(i).split('.')[0]])
#}}}

#{{{ Enhancement Power and Integration
### EnhancementSeries
fl.figurelist.append({'print_string':r'\subparagraph{Enhancement Series}' + '\n\n'})
enhancementSeries,fl.figurelist = integrate(fullPath,dnpExps,integration_width = integrationWidth,phchannel = [-1],phnum = [4],first_figure = fl.figurelist)
enhancementSeries.rename('power','expNum').labels(['expNum'],[dnpExps])
### Fit and plot the Enhancement
enhancementSeries = enhancementSeries.runcopy(real)
fl.figurelist = nextfigure(fl.figurelist,'EnhancementSeries')
ax = gca()
plot(enhancementSeries.copy().set_error(None),'b',alpha = 0.5)
title('NMR Enhancement')
#}}}

#{{{ T1 Power and Integration
### The T1 of Power Series
# Power File
t1SeriesList = []
t1DataList = []
t1ErrList = []
print "Running your T1 series"
fl.figurelist.append({'print_string':r'\subparagraph{T_1 Series}' + '\n\n'})
for count,expNum in enumerate(t1Exp):
    print "integrating data from expno %0.2f"%expNum
    fl.figurelist.append({'print_string':r'$T_1$ experiment %d'%expNum + '\n\n'})
    rawT1,fl.figurelist = integrate(fullPath,expNum,integration_width = integrationWidth,phchannel = [-1],phnum = [4],first_figure = fl.figurelist,pdfstring = 't1Expno_%d'%(expNum))
    rawT1.rename('power','delay')
    print "pulling delay from expno %0.2f"%expNum
    delay = bruker_load_vdlist(fullPath + '/%d/' %expNum)
    rawT1.labels(['delay'],[delay])
    rawT1 = nmrfit.t1curve(rawT1.runcopy(real),verbose = False)
    s2 = float(rawT1['delay',-1].data)
    s1 = -s2
    t1g = 1.14 ### this needs to change relatively frequently, need to put something here to better guess the T1 value
    rawT1.starting_guesses.insert(0,array([s1,s2,t1g]))
    rawT1.fit()
    fl.figurelist = nextfigure(fl.figurelist,'t1RawDataExp%d'%(expNum))
    ax = gca()
    title('T1 Exp %0.2f'%(expNum))
    text(0.5,0.75,rawT1.latex(),transform = ax.transAxes,size = 'x-large', horizontalalignment = 'center',color = 'k')
    plot(rawT1,'r.')
    plot(rawT1.eval(100))
    plot(rawT1 - rawT1.eval(100).interp('delay',rawT1.getaxis('delay')).runcopy(real),'g.')
    t1DataList.append(rawT1.output(r'T_1'))
    t1ErrList.append(sqrt(rawT1.covar(r'T_1')))
    t1SeriesList.append(rawT1)
#{{{ Save the T1 set
    if saveData: # here we want to save the data sets to an h5 file with the name expname
        ### Things to save are the kSigma(power) and T1(power) series
        filename = h5FileName + '/Integral/'
        try:
            rawT1Name = '%d'%expNum
            rawT1.name(rawT1Name)
            rawT1.hdf5_write(filename)
            print "saved the t1 exp %d"%expNum
        except:
            print "There is an old data set saved"
            if deleteOldSaveNew:
                h5file,childnode = h5nodebypath(filename +'/'+ rawT1Name,check_only = True)
                h5file.removeNode(childnode,recursive = True)
                h5file.close()
                rawT1.name(rawT1Name)
                rawT1.hdf5_write(filename)
                print "I've deleted the old T1 data set and saved the new one"
#}}}

# The t1 of experiment series
t1Series = nddata(array(t1DataList)).rename('value','expNum').labels(['expNum'],[t1Exp]).set_error(array(t1ErrList))

#{{{ Save the enhancement and T1 series
if saveData: # here we want to save the data sets to an h5 file with the name expname
    ### Things to save are the kSigma(power) and T1(power) series
    filename = h5FileName + '/'
    # Save the enhancement Series
    try:
        enhancementName = 'enhancementSeries'
        enhancementSeries.name(enhancementName)
        enhancementSeries.hdf5_write(filename)
        print "saved the enhancement series"
    except:
        print "There is an old data set saved"
        if deleteOldSaveNew:
            h5file,childnode = h5nodebypath(filename +'/'+ enhancementName,check_only = True)
            h5file.removeNode(childnode,recursive = True)
            h5file.close()
            enhancementSeries.name(enhancementName)
            enhancementSeries.hdf5_write(filename)
            print "I've deleted the old enhancement Series data set and saved the new one"
    # save the t1 of experiment series
    try:
        t1SeriesName = 't1Series'
        t1Series.name(t1SeriesName)
        t1Series.hdf5_write(filename)
        print "saved the t1 series"
    except:
        print "There is an old data set saved"
        if deleteOldSaveNew:
            h5file,childnode = h5nodebypath(filename +'/'+ t1SeriesName,check_only = True)
            h5file.removeNode(childnode,recursive = True)
            h5file.close()
            t1Series.name(t1SeriesName)
            t1Series.hdf5_write(filename)
            print "I've deleted the old t1 Series data set and saved the new one"
#}}}

### Write everything to a csv file as well
try:
    os.mkdir(name)
except:
    print "file exists"
    pass

### Write the t1 series
t1SeriesWriter = [('t1Val (s)','error','expNum')] + zip(list(t1Series.data),list(t1Series.get_error()),list(t1Series.getaxis('expNum')))
with open(name + '/t1Series.csv','wb') as csvFile:
    writer = csv.writer(csvFile,delimiter =',')
    writer.writerows(t1SeriesWriter)

### Write the enhancement series
enhancementSeriesWriter = [('integrationVal','error','expNum')] + zip(list(enhancementSeries.data),list(enhancementSeries.get_error()),list(enhancementSeries.getaxis('expNum')))
with open(name + '/enhancementSeries.csv','wb') as csvFile:
    writer = csv.writer(csvFile,delimiter =',')
    writer.writerows(enhancementSeriesWriter)

for count,t1Set in enumerate(t1SeriesList):
    t1SetWriter = [('integrationVal','error','delay')] + zip(list(t1Set.data),list(t1Set.get_error()),list(t1Set.getaxis('delay')))
    with open(name + '/t1Integral%d.csv'%t1Exp[count],'wb') as csvFile:
        writer = csv.writer(csvFile,delimiter =',')
        writer.writerows(t1SetWriter)




fl.show(name + '.pdf')






