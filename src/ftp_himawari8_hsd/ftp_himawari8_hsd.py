import bz2
import concurrent.futures
import ftplib
import logging
import os
import sys
import time as t
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
import dateparser
import pandas as pd
import wget
from pandas.core.common import flatten
import pytz


class downloader:
    """
    author: Sasikala Gnanmuthu
    co-autor: Nilesh zagade
    
    A class for downloading JAXA full-disk HSD
    
    Parameters
    ----------
    start_date : string, optional, start date time of target time range in UTC (Coordinated Universal Time, same as the 
                JAXA P-Tree system); follows format ``yyyy/MM/dd hh:mm''. ``yyyy'', ``MM'', ``dd'', ``hh'' and ``mm'' 
                denote year, month, day, hour and minute, respectively. ``MM'', ``dd'', ``hh'' and ``mm'' can work with
                and without the leading zeros. Noted that HSD files are only available for the latest 30 days. Start 
                time should be within the 30 days range. Default start time is 15 minutes from the present time. 
    end_date : string, optional, end date time of target time range in UTC; follows format ``yyyy/MM/dd hh:mm''. Default
              end time is the present time.
    username : string, compulsory, username of JAXA P-Tree system.
    password : string, compulsory, password of JAXA P-Tree system.
    download_path : String & Path, compulsory, the location of downloaded HSD files.
    MAX_WORKERS : integer, optional, number of threads used to parallel download data. Range from 1 to 61 for Windows. 
                  Default max workers is 4. 
    """
    
    # Introduce parameters
    start_date=None
    end_date=None
    password=None
    username=None
    MAX_WORKERS=None
    download_path=None
    
    def __init__(self):
        """Default values for parameters"""
        self.start_date=None
        self.end_date=None
        self.password=None
        self.username=None
        self.MAX_WORKERS=4
        self.download_path=None

        
    def help(self):
        """Help documentation."""
        help="""How to execute this ftp_himawari8_hsd

        import ftp_himawari8_hsd as ftp
        hsd=ftp.downloader()
        # set following parameters
        # Time range to download
        # By default retrieves the last 15 minutes files
        hsd.start_date = "yyyy/MM/dd hh:mm"
        hsd.end_date = "yyyy/MM/dd hh:mm"
        # P-Tree system user credentials
        hsd.username = "USERNAME"
        hsd.password = "PASSWORD"
        # Download path to save data
        hsd.download_path = "PATH"
        # Choose the number of workers to download (1-MAX(CPU))
        hsd.MAX_WORKERS = NUMBER
        # Run ftp_himawari8_ftp.downloader
        hsd.run()

        By default it will download files from the last 15 minutes. Necessary inputs are username,
        password and download path for the function to work.

        Follow the below format for user inputs as follows.
        this script can accept date/month without leading zeros.
        yyyy: year (4 digits), mm : month (2 digits), dd : day(2 digits)
        Time should be in UTC

        1. "yyyy/MM/dd hh:mm".
           For example, start date time is "2021/07/25 00:00" and end date time is "2021/07/25 23:50".
           Output file timestamps are every 10-minute timestamps from "2021/07/25 00:00" to "2021/07/25 23:50".
        2. "yyyy/MM/dd".
           For example, start and end date time both are "2021/07/25". Output file timestamps are every 
           10-minute timestamps from "2021/07/25 00:00" to "2021/07/25 23:50", same as the first way.
        3. "hh:mm".
           It only supports downloading data of current dat. For example, start date time is "01:00" and end 
           date time is "01:20". Output file timestamps are current day's "01:00", "01:10" and "01:20".
        4. No assigned download periods.
           Default values are used for start date and end date. Output is the available HSD files in the past 
           15 minutes.

        To stop execution: Press cntrl + C

        about downloadfiles function
        helps user to download the geostationary satellite Himawari Standard Data
        provided by the Japan Meteorological Agency (JMA) as well as the geophysical parameter data
        produced by JAXA using the Himawari Standard Data via FTP
        JAXA p-Tree FTP server only allows to download: before 30 days from current date

        User Inputs parameters:
            start_date : string, optional, start date time of target time range in UTC (Coordinated Universal Time, same as the 
                         JAXA P-Tree system); follows format ``yyyy/MM/dd hh:mm''. ``yyyy'', ``MM'', ``dd'', ``hh'' and ``mm'' 
                         denote year, month, day, hour and minute, respectively. ``MM'', ``dd'', ``hh'' and ``mm'' can work with
                         and without the leading zeros. Noted that HSD files are only available for the latest 30 days. Start 
                         time should be within the 30 days range. Default start time is 15 minutes from the present time. 
            end_date : string, optional, end date time of target time range in UTC; follows format ``yyyy/MM/dd hh:mm''. Default
                       end time is the present time.
            username : string, compulsory, username of JAXA P-Tree system.
            password : string, compulsory, password of JAXA P-Tree system.
            download_path : String & Path, compulsory, the location of downloaded HSD files.
            MAX_WORKERS : integer, optional, number of threads used to parallel download data. Range from 1 to 61 for Windows. 
                           Default max workers is 4. 

        for a day(24 hrs) JAXA server provides approximately 22,720 files in zipped format(*.bz2).
        bz2 file size can be more than 50MB also
        when a file is downloaded its size is also displayed to the user along with the filename."""
        print(help)


    def run(self):
        """
        Excute the download in mutiple threads.
                
        Returns
        -------
        Himawari Standard Data in DAT format
        """
        try:
            # format user input to date format
            if(self.start_date==None and self.end_date==None):
                sdate=datetime.now(timezone.utc)-timedelta(minutes=15)
                print(sdate)
                edate=datetime.now(timezone.utc)
                print(edate)
            else:
                utc=pytz.UTC
                sdate = dateparser.parse(self.start_date)
                sdate=utc.localize(sdate)
                edate = dateparser.parse(self.end_date)
                edate=utc.localize(edate)
                
            if (self.download_path==None):
               raise Exception("Please enter a download path")
            
            #check date validity
            if (edate < sdate) or (sdate > datetime.now(timezone.utc)):
                print('Please enter valid date range...')
                sys.exit()

            # indicates the log file creation
            logging.basicConfig(level=logging.DEBUG, filename='ftp_Himawari8_hsd.log',
                                format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S',
                                )

            # access to JAXA p-Tree FTP site
            server = 'ftp.ptree.jaxa.jp'
            directory = 'jma/hsd/'
            
            # print current processing step
            print("Hello", self.username + "!")
            print("Connecting to JAXA p-Tree FTP server")
            
            # specify the login user credentials provided by JAXA's p-Tree system
            ftp = ftplib.FTP(server)
            ftp.login(self.username, self.password)
            logging.info('Login successful')

            # print current processing step
            print("Changing to directory: {}".format(directory))
            ftp.cwd(directory)

            # JAXA ftp server folder hierarchy is as follows
            # /jma/hsd/yyyymm/dd/hh/filename
            # ex: /jma/hsd/202107/20/00/HS_H08_20210720_1200_B01_FLDK_R10_S0110.DAT.bz2

            # Step 1: Prepare the list of dates - user input date range
            print('1. Preparing list of dates')
            df_daterange = pd.DataFrame(pd.date_range(sdate.date(), edate.date() - timedelta(days=0), freq='1d'),
                                        columns=['daterange'])

            df_daterange['yyyymm/dd'] = df_daterange['daterange'].astype(str).str.split('-').str[0] + \
                df_daterange['daterange'].astype(str).str.split('-').str[1] + '/' + \
                df_daterange['daterange'].astype(str).str.split('-').str[2]
            daywise_list = [ftp.nlst(x) for x in list(df_daterange['yyyymm/dd'])]
            df_daywise = pd.DataFrame(sorted(list(flatten(daywise_list))), columns=['daywise'])

            # Step 2: Navigate to the date range folders of JAXA ftp filepath and extract files
            print('2. Extracting data files for the date range. Please wait......')
            userdaterange_filelists = [ftp.nlst(fldr) for fldr in sorted(df_daywise['daywise'])]

            df_filelist = pd.DataFrame(sorted(list(flatten(userdaterange_filelists))),
                                    columns=['ftp_file_path'])

            # Step 3: Extract the scan time from the filename to a new dataframe column
            df_filelist['scandatetime'] = pd.to_datetime(
                df_filelist['ftp_file_path'].str.split('/').str[0] +
                df_filelist['ftp_file_path'].str.split('/').str[1] +
                df_filelist['ftp_file_path'].str.split('_').str[3])

            # if user has keyed-in only dates
            if edate.hour == 0 and edate.minute == 0:
                edate = datetime.combine(edate, time.max)

            start_timestamp = str(sdate.year) + str(sdate.month).zfill(2) + str(sdate.day).zfill(2) + \
                str(sdate.hour).zfill(2) + str(sdate.minute).zfill(2)
            end_timestamp = str(edate.year) + str(edate.month).zfill(2) + str(edate.day).zfill(2) + \
                str(edate.hour).zfill(2) + str(edate.minute).zfill(2)

            # Step 4: Filter files based on user input time range
            print('3. Filtering files for user input time range')
            mask = (df_filelist['scandatetime'] >= start_timestamp) & (df_filelist['scandatetime'] <= end_timestamp)
            df_filelist = df_filelist.loc[mask]

            # Step 5: Filter only AHI full disk data files
            df_filelist = df_filelist.loc[(df_filelist['ftp_file_path'].str.contains('_FLDK_'))]
            df_filelist = df_filelist.loc[(df_filelist['ftp_file_path'].str.contains('.bz2'))]
            
            #check date validity
            if len(df_filelist) > 0:
                filelist = list(df_filelist['ftp_file_path'])
                print("Total files downloadable: " + str(len(filelist)))

                # Step 6: start to unpack *.bz2 and download the *.dat files from fileslist
                cnt = 0
                for i in range(len(filelist)):
                    file = filelist[i]
                    fileurl = 'ftp://' + self.username + ':' + self.password + '@ftp.ptree.jaxa.jp/jma/hsd/' + file

                    downloadfilename = file.split('/')  # '202107/25/12/HS_H08_20210725_1250_B08_FLDK_R20_S0810.DAT.bz2'
                    fullfilename = downloadfilename[3].split('.')  # HS_H08_20210725_1250_B08_FLDK_R20_S0810.DAT.bz2

                    # for detailed information on filename refer to below url link, page number 10
                    # https://www.data.jma.go.jp/mscweb/en/himawari89/space_segment/hsd_sample/HS_D_users_guide_en_v13.pdf

                    # ex:  HS_H08_20210612_0030_B01_JP02_R10_S0101 himawari standard(HS)_satellitename(
                    # H08)_YYYYMMDD_observation starttime(hhmm)_bandnumber(B01)_Japanareaand number(
                    # JP02)_Region/landmarkarea(R10)_spatialresoultion(S0101)
                    file_name = fullfilename[0]

                    # Check if file is not yet downloaded(file in *.bz2 format)
                    # or partial downloading state(file in *.dat format).
                    if not (os.path.exists(os.path.join(self.download_path,
                                                        file_name + ".DAT"))):
                        # This avoids repeated downloading of
                        # same file from JAXA ftp server

                        srcfile = wget.download(fileurl, out=self.download_path)  # download file *.bz2
                        outfile_path = os.path.join(self.download_path, downloadfilename[3].split('.bz2')[0])

                        with open(srcfile, 'rb') as source, open(outfile_path, 'wb') as dest:
                            dest.write(bz2.decompress(source.read()))  # unzip *.dat file

                        t.sleep(2)
                        os.remove(srcfile)  # remove *.bz2 file
                    cnt += 1
                    print(str(cnt) + '. ' + str(file_name))
                print(str(cnt) + ' files downloaded.')
                logging.info(str(cnt) + ' Files downloaded for date range ' + str(sdate) + ' to ' + str(edate))
                sys.exit()
            else:
                print('No data files available at JAXA ftp server. Try another datetime range!')
                sys.exit()
        except Exception as ex:
            print('Error has occured !.', ex)
            logging.error('Error has occured !', ex)
            sys.exit()

            
    def download(self):
        """
        Excute the download in single thread.
        
        Returns
        -------
        Himawari Standard Data in DAT format
        """
        # executes calls asynchronously. For windows max_workers must be less than or equal to 61.
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            futures = {executor.submit(self.run())}
            for fut in concurrent.futures.as_completed(futures):
                print(fut.result())
                logging.info(fut.result())
