# JNR Risk Mapping Tool

The Jurisdictional and Nested REDD+ (JNR) Risk Mapping Tool allows you to create a risk map of deforestation, created by a geometric classification of distance from the forest edge. 





## Requirement

- [Python](https://www.python.org/) 3.8+
- [numpy](https://github.com/numpy/numpy) 
- [gdel](https://github.com/OSGeo/gdal) 3.61+



## Methodology

The tool provides a simple benchmark risk mapping methodology based on a series of case studies that were conducted by the Clark Labs/TerraCarbon team in:
- Ucayali Department, Peru
- Brazil, State of Acre
- Cambodia
- Tanzania, Makame Savannah
- US, State of Rhode Island
- US, State of Delaware

In all of the case studies examined, that deforestation was most intense adjacent to the forest edge with a rapid decline in frequency as distance from the forest edge increases. Information Theory (Cover and Thomas, 1991) suggests that the bins should be narrower closer to the forest edge where the frequency of deforestation is highest. A common classification scheme for skewed data is a geometric classification, which is what we recommend as a simple benchmark risk assessment using ordinal bins.

To create a geometric series classification, we need to establish the common ratio(r). Using any two values in the series and the number of classes that should exist between them, the common ratio can be determined.The lower limit of the highest risk class (LL) is imagery spatial resolution  (the minimum distance possible without being in non-forest) and the upper limit of the lowest risk class (UL) is the Negligible Risk Threshold(NRT).

```
r = (LL / UL)**1/n_classes
LLc = UL * r**c
```


## Usage/Examples
The methodology requires a minimum of three wall-to-wall Forest Cover Benchmark Maps (FCBM) at moderate resolution (e.g., 30 m) or finer. Take the case of Acre, Brazil over the period 2014-2020 as an example. 

FCBM spatial resolution is 30m. 99.5% of deforestation occurred within a distance of 2460 m. The NRT was therefore set at 2460 (the right-hand limit of the figure). We would like to create a risk map with up to 30 non-zero classes plus a 0-risk class that includes areas of negligible risk plus areas of planned deforestation.

### Step one
- Prepare your Forest Cover Benchmark Maps (FCBM) imagery. The raster file format can be *.tif* or *.rst*. The output file format will be the same as input raster format.
- Run *risk_map.py*

### Step two
- Input the *Negligible Risk Threshold (NRT) distance*, *number of non-zero classes*, *output filename* and  *working direstory*. 

```
Please Enter NRT (Negligible Risk Threshold) Distance: 2460
Please Enter Number of non-zero classes: 30
Filename for the output image: risk30
Current working directory: C:/Document/ClarkLab/automation team/TerraCarbon/Risk_Map/data
```

### Result

![Risk Map Result](https://raw.github.com/Clark-Labs/Risk_Map/main/map.png)
