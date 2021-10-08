# ftp-himawari8-hsd
Python package to ftp download of himawari8 real-time full disk satellite image files from JAXA server for the specified date range(Himawari standard data will be provided only for the latest 30 days).  </br> </br>

<h2>Pre-requisites:</h2></br>
<b>User Registration </b> </br>
<ol>
   Make an User Account request for the data use of JAXA p-Tree system: </br></li>
         <li> Apply for a user account by clicking the user registration button on top of the website https://www.eorc.jaxa.jp/ptree/index_j.html.  </br></li>
         <li> Enter the user information according the procedure described. Application acceptance email will be sent from the P-Tree secretariat.</br></li>
         <li> Download the python package from pip.</br>
         <li> pip install ftp-himawari8-hsd </br>
</li></ol>
<b>Software needed</b></br>
<ol>
  <li> Install Anaconda framework(Opensource) from website  https://www.anaconda.com/products/individual to your local machine.</li>
  <li> Install Python(version >= 3.7) from website https://www.python.org/downloads/</li>  
  <li> After successfully installing Python, Create virtual or conda environment and install the package from pypi  </br>
    </li>
</ol>
<b>Python Dependencies:</b> </br>
ftp_himawari8_hsd depends on the python packages as listed in requirements.txt file of this repository. They will automatically be installed with the pip install.</br> </br>

    
<h2>Usage</h2>  
<h3>Downloading Satellite Imagery from JAXA server</h3></br> 
Execute ftp_himawari8_hsd</br>
Example:</br>
<b> > <strong><i> ftp_himawari8_hsd </i></strong> </b> </br>
      
    import ftp_himawari8_hsd as ftp
    hsd=ftp.downloader()
    hsd.start_date="2021/07/25 00:00" By default it will retrive the last 10 minutes files
    hsd.end_date="2021/07/25 00:00"
    hsd.username="foo" Enter your username here
    hsd.password="bar" Enter your password here
    hsd.download_path="C:/ftp" Enter your download path here, by default it is C:/ftp
    hsd.MAX_WORKERS=8 Enter the number of workers to download here
    hsd.run()

    By default it will download files from the last 10 minutes. 
    Necessary inputs are username and password for the function to work
    You can use ftp.downloader().help() to get this information printed.

This will download the full-disk Himawari8 Standard Data as zipped files (*.bz2) and then automatically unzipped (*.DAT).The general HSD file name format is: HS\_aaa\_yyyymmdd\_hhnn\_Bbb\_FLDK\_Rjj\_Skkll.DAT. Letters indicate different information. "HS" means Himawari Standard Data. "aaa" means satellite name and can be H08 (Himawari-8) or H09(Himawati-9). "hhnn" indicates hour and minute (every 10 minute). "bb" indicates band number from 01 to 16. "FLDK" means full-disk. "jj" indicates the spatial resolution in which 05 means 0.5 km, 10 means 1 km and 20 means 2 km."kkll" indicates information on the segment division of HSD. "kk" means segment number from 01 to ll. "ll" means total number of segments ranges between 01 and 99. </br>

Examples of download period
Date and Time should be in UTC

<ol> 
  <li> download for given range of timestamps. Output file timestamps are every 10-minute timestamps from "2021/07/25 00:00" to "2021/07/25 23:50".</li>
  
    Enter start datetime yyyy/mm/dd hh:mm: 2021/07/25 00:00
    Enter end datetime yyyy/mm/dd hh:mm : 2021/07/25 23:50    

  <li> download for given time range of current date. Output file timestamps are current day's "01:00", "01:10" and "01:20".</li>
  
    Enter start datetime yyyy/mm/dd hh:mm: 01:00 
    Enter end datetime yyyy/mm/dd hh:mm : 01:20     
  
  <li> download for given range of dates. Output file timestamps are every 10-minute timestamps from "2021/07/25 00:00" to "2021/07/25 23:50". </li>
    
    Enter start datetime yyyy/mm/dd hh:mm: 2021/7/25 
    Enter end datetime yyyy/mm/dd hh:mm : 2021/7/25       
</li></ol>
</br>
  
<h3>How to use downloaded Satellite Imagery</h3></br>
Refer to 'Processing_Satellite_Imagery.ipynb' file of this Github repository \url{https://github.com/gSasikala/ftp-himawari8-hsd/tree/main/examples} for how to open the downloaded files and make use of it. Detailed usage include but not limited to open, process, crop, save Satellite Imagery and generate Composites. </br>
Download atleast 10 minutes (e.g. 2:00 to 2:10) data of a date to work on this processing. </br>

#### Example 1: AHI Himawari8 Full Disk image for Band 1 
<img src='https://raw.githubusercontent.com/gSasikala/Python_JAXA_Himawari8_Imagery_Downloader/main/examples/earth_fldk.png' width="100%" height="80%" />

#### Example 2: Generate composite "airmass". To generate Satpy Composites needs all bands B01-B16 for at least 10 minutes timeframe of a date.
<img src='https://raw.githubusercontent.com/gSasikala/Python_JAXA_Himawari8_Imagery_Downloader/main/examples/airmass.png' width="100%" height="100%" /></br>



