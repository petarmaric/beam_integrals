About
=====

Console app and Python API for determining beam integrals of all 6 supported
beam types, as described in [Milasinovic1997]_. This is a reengineered, advanced
version of our `previous work`_.

This work is a part of the investigation within the research projects:
[ON174027]_ and [TR36017]_, supported by the Ministry for Science and
Technology, Republic of Serbia. This support is gratefully acknowledged.

`Continuous integration`_ is powered by `Jenkins`_.

.. image:: http://ci.petarmaric.com/job/beam_integrals/badge/icon
   :target: http://ci.petarmaric.com/job/beam_integrals/

References
----------

.. [Milasinovic1997]
   Milašinović, D.D. "The Finite Strip Method in Computational Mechanics".
   Faculties of Civil Engineering: University of Novi Sad, Technical University
   of Budapest and University of Belgrade: Subotica, Budapest, Belgrade. (1997)
.. [ON174027]
   "Computational Mechanics in Structural Engineering"
.. [TR36017]
   "Utilization of by-products and recycled waste materials in concrete
   composites in the scope of sustainable construction development in Serbia:
   investigation and environmental assessment of possible applications"

.. _`previous work`: https://bitbucket.org/losmi83/mktn5
.. _`Continuous integration`: http://ci.petarmaric.com/job/beam_integrals/
.. _`Jenkins`: https://jenkins-ci.org/


Installation
============

To install beam_integrals run::

    $ pip install beam_integrals

It's strongly recommended to install `gmpy`_. Without it code will still run
correctly, but much slower at high precision.

.. _`gmpy`: http://pypi.python.org/pypi/gmpy


Console app usage
=================

Quick start::

    $ beam_integrals <subcomand> ...

Show help::

    $ beam_integrals help


Python API usage
================

Quick start::

    >>> from beam_integrals.beam_types import FreeFreeBeam
    >>> from beam_integrals.integrals import I1, integrate
    >>> integrate(I1(), FreeFreeBeam(), a=1., m=1, n=1, error=True)


Contribute
==========

If you find any bugs, or wish to propose new features `please let us know`_. 

If you'd like to contribute, simply fork `the repository`_, commit your changes
and send a pull request. Make sure you add yourself to `AUTHORS`_.

.. _`please let us know`: https://bitbucket.org/petar/beam_integrals/issues/new
.. _`the repository`: http://bitbucket.org/petar/beam_integrals
.. _`AUTHORS`: https://bitbucket.org/petar/beam_integrals/src/default/AUTHORS


New in beam_integrals 1.1.0
===========================

Feature additions
-----------------

    * Added a heuristic to help guessing the scale function/factor, as per the
      section 3.4 of my PhD thesis.
