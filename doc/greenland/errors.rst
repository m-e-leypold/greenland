.. Copyright (c)  2016, 2017, M E Leypold.
   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
   A copy of the license is included in the section entitled "GNU
   Free Documentation License".



:mod:`greenland.errors` -- Human readable error messages
========================================================

.. automodule:: greenland.errors

Intro
-----

The general idea behind the class :py:class:`Error` is, that runtime
errors of applications often consist of parts: The type of an error
and information about the circumstances when this error occcured.

An example would be an error when opening some file: `FileOpenError`
would be the type of the error and the information about the
circumstance would be (at least) the path of the file
(e.g. `"/foo/baz.db"`) and the error code provided by the operating
system (e.g. `EACCESS`).

Ideally client code would be able to extract various informational
texts from errors once they have been raised, without having to bother
to format them itself. Depending on the circumstances of error
processing those could be:

- A short one line message to indicate which error occured where.
- A full dump of the complete circumstance under which the error
  occured (all instance specific data).  
- Some help text to the user or administrator explaining the meaning
  of the error: If it is a program bug, a configuration error or a
  user error.

The form of these informational texts is specific to the error type,
apart from the aforementioned information about the instance specific
circumstances which needs to be filled in. As such, the texts are
rather templates that are defined as class attributes that are then
expanded with the additional information when the instance texts are
retrieved.

All this is demonstrated in the following example.

:class:`greenland.errors.Error`
       
  
Examples
--------

.. code-block:: python

   from greenland.errors  import Error

   class SomeError(Error):

       message = "Some error happened, severity={baz}"

       help    = """
		 This message is raised when some error happens.
		 The value of baz (here: {baz}) indicates the
		 level of severity.
		 """

       info    = """
		 foo: {foo}
		 baz: {baz}
		 """



This is how a client defines an error type. The one line message, the
help text and the per instance information text are given as
templates, the field names need to be passed to the constructor as
keyword parameters at the place where the error is raise (see :py:meth:`Error.__init__`).

It is not necessary to write formatting procedures or even to provide
a constructor.
       
.. code-block:: python
		
   raise SomeError(foo=123,baz=456)

When instantiating :py:class:`Error`, the template fields need to be
supplied as keyword parameters.
   
The output when the exception is not caught, will be
  
.. code-block:: console

   $ ./basic

   Traceback (most recent call last):
   File "./basic", line 19, in <module>
     raise SomeError(foo=123,baz=456)
   __main__.SomeError: Some error happened, severity=456

   ./basic:19: SomeError: Some error happened, severity=456
   
   foo: 123
   baz: 456

   This message is raised when some error happens.
   The value of baz (here: 456) indicates the
   level of severity.

When an exception `e` is raised, Python prints first the backtrace,
then `str(e)`. Normally the latter is one line of text, but  :py:class:`Error`
implements :py:meth:`Error.__str__` to print the
following pieces of text on multiple lines:

- In the first line (which will be output immediately after the class
  name): The :py:attr:`~Error.message` template formatted with the
  parameters to the constructor.

- Separated by one empty line the file and the line number where
  the :py:class:`Error` object was constructed and again
  the :py:attr:`~Error.message` as above. This format is especially
  useful with the emacs compile buffer (and though most programming
  editors, including Emacs, can interpret the stack trace, this line
  is easier to the eye and does not require to find out which
  stackframe is the relevant one, albeit at the price of less
  information).

- Then the info template filled with construction arguments.

- And finally the complete help page, also with the construction
  arguments filled in.


Two variables -- :py:data:`errors_with_info` and :py:data:`errors_with_help`
-- which are `True` by default --
can be set to `False` to turn off some of the verbosity.

Reference
---------

.. autoclass:: Error

   Derive from this class, to define new error types. Provide the
   following attributes to define the error message, the instance
   information text (circumstance in which the error occured) and the
   help page:

   .. autoattribute:: message
		      		      
   .. autoattribute:: info
		      
   .. autoattribute:: help
		      
   .. automethod:: __init__

   .. automethod:: __str__

   .. automethod:: raise_here		   
	      
   .. automethod:: get_message

   .. automethod:: get_info

   .. automethod:: get_help		   

   .. automethod:: get_oneline		 
		   
The verbosity of error messages can be controlled by the following
switches. All of them are not protected by any locks. The idea is to
set them once and for all during program startup while there is still
only the main thread running.

.. autodata:: errors_with_info

.. autodata:: errors_with_help
		   
	       

