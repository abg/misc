config4py api
=============

Config objects
++++++++++++++

.. class:: Config
   .. classmethod:: parse(iterable)
      
      Parse a sequence of lines and return the resulting ``Config`` instance.
      ``iterable`` can be one of multiple sources that, when iterates over, 
      yield lines.  This is commonly files, but can also include sequences
      such as those derived from str.split().

   .. classmethod:: read(filenames, encoding='utf8')
      
      Attempt to read and parse a list of filenames.  Each config is merged
      against the one before it so later config files override earlier ones
      in the provided list.

   .. method:: merge(src_config)
  
      Merge one config instance with another.  This modifies the config 
      instance the merge method is called on. Merging copies all options and 
      subsections from the source config to the target instance. Any options
      that exist in both config objects are overwritten by those values from 
      the source config.

   .. method:: meld(config)
 
      Meld on config instance with another. Melding is much like merging except
      that options that exist in the target config are never overwritten by
      options in the source config.

   .. method write(filename, encoding='utf8')
  
      Write a representaton of the config to the specified filename. The target
      filename will be written with the specified encoding (default utf8).
      ``filename`` can also be any file-like object with a ``write()`` method.

Configspec objects
++++++++++++++++++
Configspec instances are configs that describe and can validate other configs.
Configspec instances have the following methods:

.. class:: Configspec
   .. method:: validate(config)
  
      Validate a ``Config`` instance based on an existing ``Configspec``.
      This method modifies ``config`` replacing option values with the conversion
      provided by the associated check.

CheckParser objects
+++++++++++++++++++
Parse the check DSL supported by ``Configspec``

.. class:: CheckParser

   .. classmethod:: parse(check)
      
      Parse a check and return a 3-tuple (check_name, args, kwargs)
      This is primarily used implicitly by ``Configspec`` to lookup checks by name
      in its own registry.
