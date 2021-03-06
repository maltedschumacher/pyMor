# This file is part of the pyMor project (http://www.pymor.org).
# Copyright Holders: Felix Albrecht, Rene Milk, Stephan Rave
# License: BSD 2-Clause License (http://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function

import numpy as np

from pymor.core.exceptions import CodimError
from pymor.grids.interfaces import AffineGridInterface
from pymor.grids.referenceelements import square


class RectGrid(AffineGridInterface):
    '''Ad-hoc implementation of a rectangular grid.

    The global face, edge and vertex indices are given as follows

                 6--10---7--11---8
                 |       |       |
                 3   2   4   3   5
                 |       |       |
                 3---8---4---9---5
                 |       |       |
                 0   0   1   1   2
                 |       |       |
                 0---6---1---7---2

    Parameters
    ----------
    num_intervals
        Tuple (n0, n1) determining a grid with n0 x n1 codim-0 entities.
    domain
        Tuple (ll, ur) where ll defines the lower left and ur the upper right
        corner of the domain.
    '''

    dim = 2
    dim_outer = 2
    reference_element = square

    def __init__(self, num_intervals=(2, 2), domain=[[0, 0], [1, 1]]):
        super(RectGrid, self).__init__()
        self.num_intervals = num_intervals
        self.domain = np.array(domain)

        self.x0_num_intervals = num_intervals[0]
        self.x1_num_intervals = num_intervals[1]
        self.x0_range = self.domain[:, 0]
        self.x1_range = self.domain[:, 1]
        self.x0_width = self.x0_range[1] - self.x0_range[0]
        self.x1_width = self.x1_range[1] - self.x1_range[0]
        self.x0_diameter = self.x0_width / self.x0_num_intervals
        self.x1_diameter = self.x1_width / self.x1_num_intervals
        self.diameter_max = max(self.x0_diameter, self.x1_diameter)
        self.diameter_min = min(self.x0_diameter, self.x1_diameter)
        n_elements = self.x0_num_intervals * self.x1_num_intervals

        # TOPOLOGY
        self.__sizes = (n_elements,
                        ((self.x0_num_intervals + 1) * self.x1_num_intervals +
                         (self.x1_num_intervals + 1) * self.x0_num_intervals),
                        (self.x0_num_intervals + 1) * (self.x1_num_intervals + 1))

        # calculate subentities -- codim-0
        EVL = ((np.arange(self.x1_num_intervals, dtype=np.int32) * (self.x0_num_intervals + 1))[:, np.newaxis] +
               np.arange(self.x0_num_intervals, dtype=np.int32)).ravel()
        EVR = EVL + 1
        EHB = np.arange(n_elements, dtype=np.int32) + (self.x0_num_intervals + 1) * self.x1_num_intervals
        EHT = EHB + self.x0_num_intervals
        codim0_subentities = np.array((EHB, EVR, EHT, EVL)).T

        # calculate subentities -- codim-1
        codim1_subentities = (np.tile(EVL[:, np.newaxis], 4) +
                              np.array([0, 1, self.x0_num_intervals + 2, self.x0_num_intervals + 1], dtype=np.int32))
        self.__subentities = (codim0_subentities, codim1_subentities)

        # GEOMETRY

        # embeddings
        x0_shifts = np.arange(self.x0_num_intervals) * self.x0_diameter + self.x0_range[0]
        x1_shifts = np.arange(self.x1_num_intervals) * self.x1_diameter + self.x1_range[0]
        shifts = np.array(np.meshgrid(x0_shifts, x1_shifts)).reshape((2, -1))
        A = np.tile(np.diag([self.x0_diameter, self.x1_diameter]), (n_elements, 1, 1))
        B = shifts.T
        self.__embeddings = (A, B)

    def __str__(self):
        return ('Rect-Grid on domain [{xmin},{xmax}] x [{ymin},{ymax}]\n' +
                'x0-intervals: {x0ni}, x1-intervals: {x1ni}\n' +
                'faces: {faces}, edges: {edges}, verticies: {verticies}').format(
                    xmin=self.x0_range[0], xmax=self.x0_range[1],
                    ymin=self.x1_range[0], ymax=self.x1_range[1],
                    x0ni=self.x0_num_intervals, x1ni=self.x1_num_intervals,
                    faces=self.size(0), edges=self.size(1), verticies=self.size(2))

    def size(self, codim=0):
        assert 0 <= codim <= 2, CodimError('Invalid codimension')
        return self.__sizes[codim]

    def subentities(self, codim=0, subentity_codim=None):
        assert 0 <= codim <= 2, CodimError('Invalid codimension')
        if subentity_codim is None:
            subentity_codim = codim + 1
        assert codim <= subentity_codim <= self.dim, CodimError('Invalid subentity codimensoin')
        if codim == 0:
            if subentity_codim == 0:
                return np.arange(self.size(0), dtype='int32')[:, np.newaxis]
            else:
                return self.__subentities[subentity_codim - 1]
        else:
            return super(RectGrid, self).subentities(codim, subentity_codim)

    def embeddings(self, codim=0):
        if codim == 0:
            return self.__embeddings
        else:
            return super(RectGrid, self).embeddings(codim)

    def visualize(self, dofs):
        import matplotlib.pyplot as plt
        import matplotlib.cm as cm
        assert dofs.size == self.size(0), ValueError('DOF-vector has the wrong size')
        im = plt.imshow(dofs.reshape((self.x1_num_intervals, self.x0_num_intervals)), cmap=cm.jet,
                        aspect=self.x1_diameter / self.x0_diameter, extent=self.domain.T.ravel(),
                        interpolation='none')

        # make sure, the colorbar has the right height: (from mpl documentation)
        from mpl_toolkits.axes_grid1 import make_axes_locatable
        divider = make_axes_locatable(plt.gca())
        cax = divider.append_axes("right", "5%", pad="3%")
        plt.colorbar(im, cax=cax)
        plt.show()

    @staticmethod
    def test_instances():
        '''Used for unit testing.'''
        return [RectGrid((2, 4)), RectGrid((1, 1)), RectGrid((42, 42))]
