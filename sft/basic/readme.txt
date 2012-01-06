Naming conventions
--------------------

This section describes how to decipher the file names under this directory. 
All of them follow the rule of:

    [actions][OBJECTS][decors].py
    
[actions] can be a combination of the following charactors:

    c: create
    u: update (implies c)
    m: move (implies c)
    d: delete (implies c)
    
[OBJECTS] can be a combination of the following charactors:

    F: file
    D: directory
    
[decors] can be a combination of the following charactors:

    r: act on randomly selected systems (otherwise the systems will be selected
       in an numerical order)
    t: with significant programmed delays (e.g. greater than 10 min.)
    l: with loops or recursions
       
For example, 'cDr.py' means to create a directory on a random selected system.