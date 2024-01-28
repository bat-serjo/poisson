Install:
```commandline
python -m pip install -r requirements.txt
```

Run: 
```commandline
python main.py
```
Test:
```commandline
curl -d '{"data": "c3RvcHMgcG9wIHBhc3QuYXJyZXN0cyBwcmVjaW5jdCBldGggY3JpbWUKNzUgMTcyMCAxOTEgMSAxIDEKMzYgMTcyMCA1NyAxIDEgMgo3NCAxNzIwIDU5OSAxIDEgMwoxNyAxNzIwIDEzMyAxIDEgNAozNyAxMzY4IDYyIDEgMiAxCjM5IDEzNjggMjcgMSAyIDIKMjMgMTM2OCAxNDkgMSAyIDMKMyAxMzY4IDU3IDEgMiA0CjI2IDIzODU0IDEzNSAxIDMgMQozMiAyMzg1NCAxNiAxIDMgMgoxMCAyMzg1NCAxMDcgMSAzIDMKMTMgMjM4NTQgMTIzIDEgMyA0CjczIDI1OTYgMjI3IDIgMSAxCg=="}' 127.0.0.1:8888
```

Result:
```commandline
                 Generalized Linear Model Regression Results                  
==============================================================================
Dep. Variable:                  stops   No. Observations:                    4
Model:                            GLM   Df Residuals:                        1
Model Family:                 Poisson   Df Model:                            2
Link Function:                    Log   Scale:                          1.0000
Method:                          IRLS   Log-Likelihood:                -17.913
Date:                Sun, 28 Jan 2024   Deviance:                       9.8505
Time:                        20:42:17   Pearson chi2:                     10.8
No. Iterations:                     5   Pseudo R-squ. (CS):             0.9698
Covariance Type:            nonrobust                                         
==============================================================================
                 coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------
intercept     -1.4791      0.060    -24.528      0.000      -1.597      -1.361
eth_2          0.4171      0.116      3.598      0.000       0.190       0.644
eth_3         -0.0692      0.126     -0.548      0.584      -0.317       0.179
==============================================================================
```

Run as service:
 * edit poisson.service file and replace the </full/path/to/>main.py with the full path to the file
 * copy poisson.service to /etc/systemd/system folder
 * run ```sudo systemctl daemon-reload``` in order to force systemd to recognise the service
 * ```sudo systemctl enable poisson.service``` to make the service run on startup
 * now you can use systemd as usual to control the service like 
   * ```sudo systemctl start poisson.service``` to start it
   * ```sudo systemctl stop poisson.service``` to stop it etc...