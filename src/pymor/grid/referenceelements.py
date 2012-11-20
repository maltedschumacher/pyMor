from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
from pymor.core.exceptions import CodimError
from .interfaces import ISimpleReferenceElement


class Point(ISimpleReferenceElement):

    dim = 0
    volume = 1

    def size(self, codim=1):
        assert codim == 0, CodimError('Invalid codimension (must be 0 but was {})'.format(codim))
        return 1

    def subentities(self, codim, subentity_codim):
        assert codim == 0, CodimError('Invalid codimension (must be 0 but was {})'.format(codim))
        assert subentity_codim == 0, CodimError('Invalid subentity codimension (must be 0 but was {})'.format(subentity_codim))
        return np.array([0])

    def subentity_embedding(self, subentity_codim):
        assert subentity_codim == 0, CodimError('Invalid codimension (must be 0 but was {})'.format(codim))
        return np.zeros((0,0)), np.zeros((0))

    def sub_reference_element(self, codim=1):
        assert codim == 0, CodimError('Invalid codimension (must be 0 but was {})'.format(codim))
        return self

    def unit_outer_normals(self):
        return np.zeros((0))

    def center(self):
        return np.zeros((0))

    def mapped_diameter(self, A):
        return np.ones(A.shape[:-2])

point = Point()


class Line(ISimpleReferenceElement):

    dim = 1
    volume = 1

    def size(self, codim=1):
        assert 0 <= codim <= 1, CodimError('Invalid codimension (must be 0 or 1 but was {})'.format(codim))
        if codim == 0:
            return 1
        else:
            return 2

    def subentities(self, codim, subentity_codim):
        assert 0 <= codim <= 1, CodimError('Invalid codimension (must be 0 or 1 but was {})'.format(codim))
        assert codim <= subentity_codim <= 1,\
               CodimError('Invalid codimension (must be between {} and 1 but was {})'.format(codim, subentity_codim))
        if codim == 0:
            return np.arange(self.size(subentity_codim))
        else:
            return np.array(([0], [1]))

    def subentity_embedding(self, subentity_codim):
        assert 0 <= subentity_codim <= 1,\
               CodimError('Invalid codimension (must be 0 or 1 but was {})'.format(subentity_codim))
        if subentity_codim == 0:
            return np.array([1.]), np.array([0.])
        else:
            return np.array((np.zeros((1,0)), np.zeros((1,0)))), np.array(([0.], [1.]))

    def sub_reference_element(self, codim=1):
        assert 0 <= codim <= 1, CodimError('Invalid codimension (must be 0 or 1 but was {})'.format(codim))
        if codim == 0:
            return self
        else:
            return point

    def unit_outer_normals(self):
        return np.array([-1.], [1.])

    def center(self):
        return np.array([0.5])

    def mapped_diameter(self, A):
        return np.apply_along_axis(np.linalg.norm, -2, A)

line = Line()


class Square(ISimpleReferenceElement):

    dim = 2
    volume = 1

    def size(self, codim=1):
        assert 0 <= codim <= 2, CodimError('Invalid codimension (must be between 0 and 2 but was {})'.format(codim))
        if codim == 0:
            return 1
        elif codim == 1:
            return 4
        elif codim == 2:
            return 4

    def subentities(self, codim, subentity_codim):
        assert 0 <= codim <= 2, CodimError('Invalid codimension (must be between 0 and 2 but was {})'.format(codim))
        assert codim <= subentity_codim <= 2,\
               CodimError('Invalid codimension (must be between {} and 2 but was {})'.format(codim, subentity_codim))
        if codim == 0:
            return np.arange(self.size(subentity_codim))
        elif codim == 1:
            if subentity_codim == 1:
                return np.array(([0], [1], [2], [3]))
            else:
                return np.array(([0, 1], [1, 2], [2, 3], [3, 0]))
        elif codim == 2:
            return np.array(([0], [1], [2], [3]))

    def subentity_embedding(self, subentity_codim):
        assert 0 <= subentity_codim <= 2,\
                CodimError('Invalid codimension (must betwen 0 and 2 but was {})'.format(subentity_codim))
        if subentity_codim == 0:
            return np.eye(2), np.zeros(2)
        elif subentity_codim == 1:
            A = np.array((np.array(([1.], [0.])), np.array(([0.], [1.])),
                          np.array(([-1.], [0.])), np.array(([0.], [-1.]))))
            B = np.array((np.array([0., 0.]), np.array([1., 0.]),
                          np.array([1., 1.]), np.array([0., 1.])))
            return A, B
        else:
            return super(Square, self).subentity_embedding(subentity_codim)

    def sub_reference_element(self, codim=1):
        assert 0 <= codim <= 2, CodimError('Invalid codimension (must be between 0 and 2 but was {})'.format(codim))
        if codim == 0:
            return self
        elif codim == 1:
            return line
        else:
            return point

    def unit_outer_normals(self):
        return np.array(([0., -1.], [1., 0.], [0., 1], [-1., 0.]))

    def center(self):
        return np.array([0.5, 0.5])

    def mapped_diameter(self, A):
        V0 = np.dot(A, np.array([1., 1.]))
        V1 = np.dot(A, np.array([1., -1]))
        VN0 = np.apply_along_axis(np.linalg.norm, -1, V0)
        VN1 = np.apply_along_axis(np.linalg.norm, -1, V1)
        return np.max((VN0, VN1), axis=0)



square = Square()