''' Unit tests for twdb_datasource

'''
import unittest
import numpy as np

from twdb_datasource import WaterDataSource


class WaterDataSourceTestCase(unittest.TestCase):

    def setUp(self):
        self.source = WaterDataSource()

    def test__get_coresample_pts(self):
        # check coresample_pts is an Nx2 numpy array
        corepts = self.source.coresample_pts
        shape = np.array(zip(range(10),range(10))).shape
        self.assertEqual(len(shape), 2,
            'incorrect dimensions: shape is {}'.format(shape))
        self.assertEqual(corepts.shape[1], shape[1],
            'incorrect dimension size : shape is {}'.format(shape))


if __name__ == "__main__":
    # from package use "python -m unittest discover -v -s ./tests/"
    unittest.main()
