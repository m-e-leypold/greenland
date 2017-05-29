.. Copyright (c)  2016, 2017, M E Leypold.
   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
   A copy of the license is included in the section entitled "GNU
   Free Documentation License".


:mod:`greenland.testing.expectations` -- Vocabulary for test assertions
=======================================================================


.. automodule:: greenland.testing.expectations

	    
.. currentmodule:: greenland.testing.expectations

Intro
-----



Example
-------
		
Reference
---------

.. autoclass:: Expectee

   .. automethod:: __init__

   .. automethod:: returns ( expected )

   .. automethod:: returning ( table )

   .. automethod:: raises  ( expected, satisfying = lambda: True )	
		   
   .. automethod:: raising ( table )	   

		   
.. autoclass:: TestFailure	       

.. autoclass:: Recorder

   .. automethod:: __init__

   .. automethod:: report

   .. autoattribute::   stop_on_error
		   
   .. autoattribute::   errors

   .. autoattribute::   logfile

XXX re

		   
Failures for :py:meth:`~Expectee.returns` Expectations
......................................................

.. autoclass:: UnexpectedException (expected, actual)

.. autoclass:: UnexpectedResult (expected, actual)

Failures for :py:meth:`~Expectee.raises` Expectations
.....................................................	       
	       
.. autoclass:: WrongException (expected, actual)
   
.. autoclass:: MissingException (expected, actual)

.. autoclass:: ExceptionConstraintViolation (expected, actual, constraint ) 
	       


