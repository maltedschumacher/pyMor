# This file is part of the pyMor project (http://www.pymor.org).
# Copyright Holders: Felix Albrecht, Rene Milk, Stephan Rave
# License: BSD 2-Clause License (http://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function

import numpy as np

import pymor.core as core
from pymor.core.cache import Cachable, cached
from pymor.domaindescriptions import BoundaryType
from pymor.grids.defaultimpl import (ConformalTopologicalGridDefaultImplementations,
                                     SimpleReferenceElementDefaultImplementations,
                                     AffineGridDefaultImplementations,)


class ConformalTopologicalGridInterface(ConformalTopologicalGridDefaultImplementations, core.BasicInterface):
    '''Desribes a conformal topological grid.

    The grid is determined via the subentity relation given by `subentities(codim, subentity_codim)`.

    All results in the default implementations are cached for the next evaluation.
    Note that parts of the current default implementations are very slow and should be moved to C code.

    Attributes
    ----------
    dim
        The dimension of the grid.
    '''

    @core.interfaces.abstractmethod
    def size(self, codim):
        '''The number of entities of codimension `codim`.'''
        pass

    @core.interfaces.abstractmethod
    def subentities(self, codim, subentity_codim=None):
        '''`retval[e,s]` is the global index of the `s`-th codim-`subentity_codim`
        subentity of the codim-`codim` entity with global index `e`.

        If `subentity_codim == None`, it is set to `codim + 1`.

        Only `subentities(codim, None)` has to be implemented; by default,
        `subentities(codim, subentity_codim)` is computed by calculating the
        transitive closure of `subentities(codim, None)`
        '''
        return self._subentities(codim, subentity_codim)

    def superentities(self, codim, superentity_codim=None):
        '''`retval[e,s]` is the global index of the `s`-th codim-`superentity_codim`
        superentity of the codim-`codim` entity with global index `e`.

        `retval[e]` is sorted by global index.

        If `superentity_codim == None`, it is set to `codim - 1`.

        The default implementation is to compute the result from
        `subentities(superentity_codim, codim)`.
        '''
        return self._superentities(codim, superentity_codim)

    def superentity_indices(self, codim, superentity_codim=None):
        '''`retval[e,s]` is the local index of the codim-`codim` entity `e`
        in the codim-`superentity_codim` superentity `superentities(codim, superentity_codim)[e,s].`
        '''
        return self._superentity_indices(codim, superentity_codim)

    def neighbours(self, codim, neighbour_codim, intersection_codim=None):
        '''`retval[e,n]` is the global index of the `n`-th codim-`neighbour_codim` entitiy of the
        codim-`codim` entity `e` that shares with `e` a subentity of codimension `intersection_codim`.

        If `intersection_codim == None`, it is set to
            `codim` if `codim == neighbour_codim` and to
            `min(codim, neighbour_codim)` otherwise.

        The default implementation is to compute the result from
        `subentities(codim, intersection_codim)` and
        `superentities(intersection_codim, neihbour_codim)`.
        '''
        return self._neighbours(codim, neighbour_codim, intersection_codim)

    def boundary_mask(self, codim):
        '''`retval[e] is true iff the codim-`codim` entity with global index
        `e` is a boundary entity.

        By definition, a codim-1 entity is a boundary entity if it has only one
        codim-0 superentity. For `codim != 1`, a codim-`codim` entity is a
        boundary entity if it has a codim-1 sub/super-entity.
        '''
        return self._boundary_mask(codim)

    def boundaries(self, codim):
        '''Returns the global indices of all codim-`codim` boundary entities.

        By definition, a codim-1 entity is a boundary entity if it has only one
        codim-0 superentity. For `codim != 1`, a codim-`codim` entity is a
        boundary entity if it has a codim-1 sub/super-entity.
        '''
        return self._boundaries(codim)

    @core.interfaces.abstractstaticmethod
    def test_instances():
        '''Returns a list of Grid instances suitable to be run through our test cases.'''
        pass


class ReferenceElementInterface(SimpleReferenceElementDefaultImplementations, core.BasicInterface):
    '''Defines a reference element with the property that each of its subentities is of the same type.

    I.e. a three-dimensional reference element cannot have triangles and rectangles as faces at the
    same time.

    Attributes
    ----------
    dim
        The dimension of the reference element
    volume
        The volume of the reference element
    '''

    dim = None
    volume = None

    @core.interfaces.abstractmethod
    def size(self, codim):
        'Number of subentites of codimension `codim`.'

    @core.interfaces.abstractmethod
    def subentities(self, codim, subentity_codim):
        '''`subentities(c,sc)[i,j]` is, with respect to the indexing inside the
        reference element, the index of the `j`-th codim-`subentity_codim`
        subentity of the `i`-th codim-`codim` subentity of the reference element.
        '''
        pass

    @core.interfaces.abstractmethod
    def subentity_embedding(self, subentity_codim):
        '''Returns a tuple `(A, B)` which defines the embedding of the codim-`subentity_codim`
        subentities into the reference element.

        For `subentity_codim > 1', the embedding is by default given recursively via
        `subentity_embedding(subentity_codim - 1)` and
        `sub_reference_element(subentity_codim - 1).subentity_embedding(1)` choosing always
        the superentity with smallest index.
        '''
        return self._subentity_embedding(subentity_codim)

    @core.interfaces.abstractmethod
    def sub_reference_element(self, codim):
        '''Returns the reference relement of the codim-`codim` subentities.'''
        return self._sub_reference_element(codim)

    def __call__(self, codim):
        '''Returns the reference relement of the codim-`codim` subentities.'''
        return self.sub_reference_element(codim)

    @core.interfaces.abstractmethod
    def unit_outer_normals(self):
        '''`retval[e]` is the unit outer-normal vector to the codim-1 subentity
        with index `e`.
        '''
        pass

    @core.interfaces.abstractmethod
    def center(self):
        '''Coordinates of the barycenter.'''
        pass

    @core.interfaces.abstractmethod
    def mapped_diameter(self, A):
        '''The diameter of the reference element after tranforming it with the
        matrix `A` (vectorized).
        '''
        pass

    @core.interfaces.abstractmethod
    def quadrature(self, order=None, npoints=None, quadrature_type='default'):
        '''Returns tuple `(P, W)` where P is an array of quadrature points with
        corresponding weights `W`.

        The quadrature is of order `order` or has `npoints` integration points.
        '''
        pass

    @core.interfaces.abstractmethod
    def quadrature_info(self):
        '''Returns a tuple of dicts `(O, N)` where O[quadrature_type] is a list
        of orders which are implemented for `quadrature_type` and N[quadrature_type]
        is a list of the corrsponding numbers of integration points.
        '''
        pass

    def quadrature_types(self):
        o, _ = self.quadrature_info()
        return set(o.keys())


class AffineGridInterface(AffineGridDefaultImplementations, ConformalTopologicalGridInterface):
    '''Describes a geometric grid where each codim-0 entity has the same
    `ReferenceElementInterface` reference element to which it is affinely
    mapped.

    Attributes
    ----------
    dim_outer
        The dimension of the space into which the grid is embedded.
    '''

    dim_outer = None

    @core.interfaces.abstractmethod
    def reference_element(self, codim):
        '''The reference element of all codim-`codim` entities.'''
        pass

    @core.interfaces.abstractmethod
    def subentities(self, codim, subentity_codim=None):
        '''`retval[e,s]` is the global index of the `s`-th codim-`subentity_codim`
        subentity of the codim-`codim` entity with global index `e`.

        The ordering of subentities(0, subentity_codim)[e] has to correspond under
        the embedding of `e` with the local ordering inside the reference element.

        If `subentity_codim == None`, it is set to `codim + 1`.

        For `codim > 0`, we provide a default implementation by calculating the
        subentites of `e` as follows:

        1. Find the codim - 1 parent entity `e_0` of `e` with minimal global index
        2. Lookup the local indicies of the subentites of `e` inside `e_0` using the reference element.
        3. Map these local indicies to global indicies using `subentities(codim - 1, subentity_codim)`.

        This procedures assures that `subentities(codim, subentity_codim)[e]`
        has the right ordering w.r.t. the embedding determined by `e_0`, which
        agrees with what is returned by `embeddings(codim)`
        '''
        return self._subentities(codim, subentity_codim)

    @core.interfaces.abstractmethod
    def embeddings(self, codim):
        '''Returns tuple `(A, B)` where `A[e]` and `B[e]` are the linear part
        and the translation part of the map from the reference element of `e`
        to `e`.

        For `codim > 0`, we provide a default implementation by
        taking the embedding of the codim-1 parent entity `e_0` of `e` with
        lowest global index and composing it with the subentity_embedding of `e`
        into `e_0` determined by the reference element.
        '''
        return self._embeddings(codim)

    def jacobian_inverse_transposed(self, codim):
        '''`retval[e]` is the transposed (pseudo-)inverse of the jacobian of `embeddings(codim)[e]`.
        '''
        return self._jacobian_inverse_transposed(codim)

    def integration_elements(self, codim):
        '''`retval[e]` is given as `sqrt(det(A^T*A))`, where `A = embeddings(codim)[0][e]`.'''
        return self._integration_elements(codim)

    def volumes(self, codim):
        '''`retval[e]` is the (dim-codim)-dimensional volume of the codim-`codim` entity with global index `e`.'''
        return self._volumes(codim)

    def volumes_inverse(self, codim):
        '''`retval[e] = 1 / volumes(codim)[e]`.'''
        return self._volumes_inverse(codim)

    def unit_outer_normals(self):
        '''`retval[e,i]` is the unit outer normal to the i-th codim-1 subentity
        of the codim-0 entitiy with global index `e`.
        '''
        return self._unit_outer_normals()

    def centers(self, codim):
        '''`retval[e]` is the barycenter of the codim-`codim` entity with global index `e`.'''
        return self._centers(codim)

    def diameters(self, codim):
        '''`retval[e]` is the diameter of the codim-`codim` entity with global index `e`.'''
        return self._diameters(codim)

    def quadrature_points(self, codim, order=None, npoints=None, quadrature_type='default'):
        '''`retval[e]` is an array of quadrature points in global coordinates
        for the codim-`codim` entity with global index `e`.

        The quadrature is of order `order` or has `npoints` integration points. To
        integrate a function `f` over `e` one has to form

        ``np.dot(f(quadrature_points(codim, order)[e]), reference_element(codim).quadrature(order)[1]) * integration_elements(codim)[e]``.  # NOPEP8
        '''
        return self._quadrature_points(codim, order, npoints, quadrature_type)


# Is one entity allowed to have mor than one boundary type?
class BoundaryInfoInterface(core.BasicInterface, Cachable):
    '''Describes boundary types associated to a grid.

    For every boundary type and codimension a mask is provided, marking grid entities
    of the respective type and codimension by their global index.

    Attributes
    ----------
    boundary_types
        set of all `BoundaryTypes` the grid has.
    '''

    boundary_types = set()

    def mask(self, boundary_type, codim):
        '''retval[i] is True iff the codim-`codim` entity of global index `i` is
        associated to the boundary type `boundary_type`.
        '''
        raise ValueError('Has no boundary_type "{}"'.format(boundary_type))

    @property
    def has_dirichlet(self):
        return BoundaryType('dirichlet') in self.boundary_types

    @property
    def has_neumann(self):
        return BoundaryType('neumann') in self.boundary_types

    @property
    def has_only_dirichlet(self):
        return self.boundary_types == set((BoundaryType('dirichlet'),))

    @property
    def has_only_neumann(self):
        return self.boundary_types == set((BoundaryType('neumann'),))

    @property
    def has_only_dirichletneumann(self):
        return self.boundary_types <= set((BoundaryType('dirichlet'), BoundaryType('neumann')))

    def dirichlet_mask(self, codim):
        return self.mask(BoundaryType('dirichlet'), codim)

    def neumann_mask(self, codim):
        return self.mask(BoundaryType('neumann'), codim)

    @cached
    def _dirichlet_boundaries(self, codim):
        return np.where(self.dirichlet_mask(codim))[0].astype('int32')

    def dirichlet_boundaries(self, codim):
        return self._dirichlet_boundaries(codim)

    @cached
    def _neumann_boundaries(self, codim):
        return np.where(self.neumann_mask(codim))[0].astype('int32')

    def neumann_boundaries(self, codim):
        return self._neumann_boundaries(codim)
