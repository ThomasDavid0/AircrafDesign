import urllib.request
from urllib.error import HTTPError
from geometry import Point, PX, PY
import numpy as np
from scipy.interpolate import interp1d


class Airfoil:
    def __init__(self, name, points: Point):
        self.name = name
        self.points = points

    @staticmethod
    def parse_selig(file):      
                
        with open(file) as f:
            lines = [l.strip()  for l in f.readlines()]
        name = lines[0]
        lines = lines[1:]

        if lines[1] == "":
            npoints = np.array([float(v) for v in lines[0].split()]).astype("int")

            lines = lines[2:]
            
            d1 = lines[:npoints[0]]            
            d2 = lines[npoints[0]+1:]
            if d1[0] == d2[0]:
                d1 = d1[1:]
            lines = list(reversed(d1)) + d2

        data = np.array([l.split()  for l in lines]).astype(float)

        return Airfoil(
            name, 
            Point(
                np.append(data, np.zeros((len(data), 1)), axis=1) 
            )
        )

    @staticmethod
    def download(airfoiltoolsname):
        #https://m-selig.ae.illinois.edu/ads/coord_updates/la5055.dat
        if airfoiltoolsname[-3:] == "-il":
            airfoiltoolsname = airfoiltoolsname[:-3]
#            _file = urllib.request.urlretrieve("http://airfoiltools.com/airfoil/seligdatfile?airfoil=" + airfoiltoolsname)            

 #       else:
        _file = urllib.request.urlretrieve(f"https://m-selig.ae.illinois.edu/ads/coord/{airfoiltoolsname}.dat")
        return Airfoil.parse_selig(_file[0])

    @property
    def le_point(self):
        return self.points[int(self.points.minloc().x)]

    @property
    def te_point(self):
        return 0.5 * (self.points[0] + self.points[-1])

    @property
    def te_thickness(self):
        return (self.points[0].y - self.points[-1].y)[0]

    @property
    def chord(self):
        return self.points.x[0]

    @property
    def thickness(self):
        return max(self.points.y) - min(self.points.y)

    def set_te_thickness(self, thick:float):        
        surfaces = -np.sign(np.gradient(self.points.x))

        xunit = self.points.x / self.chord

        te_diff = PY(
            0.5 * (thick - self.te_thickness),
            len(self.points)
        ) * xunit * surfaces

        return Airfoil(self.name, self.points + te_diff)

    def set_chord(self, chord):
        return Airfoil(self.name, self.points * chord / self.chord)

    @property
    def top_surface(self) -> Point:
        return self.points[:self.points.minloc().x[0] + 1]
    
    @property
    def btm_surface(self) -> Point:
        return self.points[self.points.minloc().x[0]:]

    def top_func(self):
        return interp1d(self.top_surface.x, self.top_surface.y, "cubic", fill_value="extrapolate")

    def btm_func(self):
        return interp1d(self.top_surface.x, self.top_surface.y, "cubic", fill_value="extrapolate")

    def mean_camber(self):
        btms = self.btm_surface

        tops = Point(btms.x, self.top_func()(btms.x), btms.z)

        return 0.5 * (btms + tops)






