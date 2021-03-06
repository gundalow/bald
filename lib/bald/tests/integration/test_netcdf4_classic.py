import unittest

import h5py
import netCDF4
import numpy as np

import bald
from bald.tests import BaldTestCase

def _fattrs(f):
    f.bald__ = 'http://binary-array-ld.net/latest/'
    f.rdf__ = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
    f.rdf__type =  'bald__Container'
    return f

def _create_parent_child(f, pshape, cshape):
    for i, pdimsize in enumerate(pshape):
        f.createDimension("pdim{}".format(str(i)), pdimsize)
    for i, cdimsize in enumerate(cshape):
        f.createDimension("cdim{}".format(str(i)), cdimsize)
    varp = f.createVariable("parent_variable", 'i4', tuple(["pdim{}".format(str(i)) for i, _ in enumerate(pshape)]))
    varc = f.createVariable("child_variable", 'i4', tuple(["cdim{}".format(str(i)) for i, _ in enumerate(cshape)]))
    varp.rdf__type = 'bald__Array'
    varp.bald__references = "child_variable"
    varc.rdf__type = 'bald__Array'
    varc.rdf__type = 'bald__Reference'
    varc.bald__array = "child_variable"
    return f


class Test(BaldTestCase):
        
    def test_valid_uri(self):
        with self.temp_filename('.nc') as tfile:
            f = netCDF4.Dataset(tfile, "w", format="NETCDF4_CLASSIC")

            f = _fattrs(f)
            f.close()
            validation = bald.validate_netcdf(tfile)
            self.assertTrue(validation.is_valid())

    def test_invalid_uri(self):
        with self.temp_filename('.nc') as tfile:
            f = netCDF4.Dataset(tfile, "w", format="NETCDF4_CLASSIC")

            f = _fattrs(f)
            setattr(f, 'bald__turtle', 'bald__walnut')
            f.close()
            validation = bald.validate_netcdf(tfile)
            self.assertFalse(validation.is_valid())


class TestArrayReference(BaldTestCase):
    def test_match(self):
        with self.temp_filename('.nc') as tfile:
            f = netCDF4.Dataset(tfile, "w", format="NETCDF4_CLASSIC")
            f = _fattrs(f)
            f = _create_parent_child(f, (11, 17), (11, 17))
            f.close()
            validation = bald.validate_netcdf(tfile)
            self.assertTrue(validation.is_valid())

    def test_mismatch_zeroth(self):
        with self.temp_filename('.nc') as tfile:
            f = netCDF4.Dataset(tfile, "w", format="NETCDF4_CLASSIC")
            f = _fattrs(f)
            f = _create_parent_child(f, (11, 17), (11, 13))
            f.close()
            validation = bald.validate_netcdf(tfile)
            self.assertFalse(validation.is_valid())


if __name__ == '__main__':
    unittest.main()




