# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.
"""\
Basic classes with predefined properties

Example usage:
    class Article(Gdtstruct):
        "A basic Article class"
        # fields and types are dynamically set by the initializer
        gdtstruct_properties([('title', Gdtstr, "The Title of the Article"),
                              ('page', Gdtlist, "List of pages in the Article")
                              ])

        def __init__(self, *args):
            super(Article, self).__init__(*args)
            self.title = Gdtstr("")
            self.page = Gdtlist()         

    class Page(Gdtstruct):
        # fields and types are dynamically set by the initializer
        gdtstruct_properties([('text', Gdtstr, "The text of the page"),
                              ])

        def __init__(self, *args):            
            super(Page, self).__init__(*args)
            self.text = Gdtstr(args[0] if len(args) else "")
            

    a = Article()
    print Article.title.__doc__
    print
    a.title = "My title"
    a.page.append(Page("page 1"))
    a.page.append(Page("page 2"))
    a.commit()
    print a
    print
    a.title = "My bad title"
    a.page[1].text = "bad page 2"
    a.page.append(Page("bad page 3"))
    print a
    print
    a.page.rollback()
    print a
    print
    a.rollback()
    print a

Output of the example:

    The Title of the Article

    Article.title=My title
    Article.page.1.Page.text=page 1
    Article.page.2.Page.text=page 2
    
    
    Article.title=My bad title
    Article.page.1.Page.text=page 1
    Article.page.2.Page.text=bad page 2
    Article.page.3.Page.text=bad page 3
    
    
    Article.title=My bad title
    Article.page.1.Page.text=page 1
    Article.page.2.Page.text=page 2
    
    
    Article.title=My title
    Article.page.1.Page.text=page 1
    Article.page.2.Page.text=page 2
"""
import sys
# pylint: disable-msg=W0403
from .transaction import Transaction, Transactionlist 

# pylint: disable-msg=W0142, W0212

def _classinitializer(proc):
    "basic idea stolen from zope.interface.advice, P.J. Eby"
    def _newproc(*args, **kwargs):
        frame = sys._getframe(1)
        if '__module__' in frame.f_locals and not \
            '__module__' in frame.f_code.co_varnames: # we are in a class
            if '__metaclass__' in frame.f_locals:
                raise SyntaxError("Don't use two class initializers or\n"
                                  "a class initializer together with a "
                                  "__metaclass__ hook")
            def _makecls(name, bases, dic):
                "create the class"
                try:
                    cls = type(name, bases, dic)
                except TypeError, e:
                    if "can't have only classic bases" in str(e):
                        cls = type(name, bases + (object,), dic)
                    else:  # other strange errs, e.g. __slots__ conflicts
                        raise
                proc(cls, *args, **kwargs)
                return cls
            frame.f_locals["__metaclass__"] = _makecls
        else:
            proc(*args, **kwargs)

    # pylint: disable-msg=W0621
    _newproc.__name__ = proc.__name__
    _newproc.__module__ = proc.__module__
    _newproc.__doc__ = proc.__doc__
    _newproc.__dict__ = proc.__dict__
    return _newproc

@_classinitializer
def gdtstruct_properties(cls, schema):
    """
    Add properties to cls, according to the schema, which is a list
    of pairs (fieldname, Gdtobject_subclass, docstring).
    A Gdtobject_subclass is a callable converting the field value 
    into the Gdtobject_subclass.
    Instances of cls are expected to have private attributes 
    with names determined by the field names.
    """
#    from netconfpkg.gdt import Gdtstruct, Gdtobject
#    if not issubclass(cls, Gdtstruct) and (type(cls) != Gdtobject):
#        raise AttributeError('Class %s must be subclass of Gdtstruct!' 
#                             % cls.__name__ )

    for name, typecast, docstring in schema:        
        #if not issubclass(typecast, Gdtobject):
        #    raise AttributeError('Class %s must be subclass of Gdtobject!' 
        #                         %  typecast.__name__ )
        
        if hasattr(cls, name): # avoid accidental overriding
            raise AttributeError('You are overriding %s!' % name)
                
#        def _getter(self, name=name, typecast = typecast):
        def _getter(self, name=name):
            "get the property 'name'"
            if not hasattr(self, '_' + name):
                return None
#                return typecast()
            return getattr(self, '_' + name)
          
        def _setter(self, value, name=name, typecast=typecast):
            "set the property 'name'"
            if value == None:
                setattr(self, '_' + name, None)
            else:
                if hasattr(typecast, "apply"):
                    nval = typecast()
                    #print >> sys.stderr, typecast 
                    nval.apply(value)
                else:
                    nval = typecast(value)
                setattr(self, '_' + name, nval)
        
        def _deler(self, name=name):
            setattr(self, '_' + name, None)
            
        setattr(cls, name, property(_getter, _setter, _deler, doc=docstring))
        cls._fields.add(name)
        #cls._fields.sort()
        cls._types[name]=typecast

@_classinitializer
def gdtlist_properties(cls, typecast):
    """
    Add properties to cls, according to the schema, which is a list
    of pairs (fieldname, Gdtobject_subclass, docstring).
    A Gdtobject_subclass is a callable converting the field value 
    into the Gdtobject_subclass.
    Instances of cls are expected to have private attributes 
    with names determined by the field names.
    """
    cls._type=typecast


class Gdtobject(Transaction):
    "The base of all Gdtobjects"
    keyid = None

    def tostr(self, prefix_string = None):
        "returns a string in gdt representation"
        raise NotImplementedError

    def __str__(self):
        return self.tostr()

    def test(self):
        "test on integrity, to be implemented by sub-classes"
        return True


class Gdtcontainer(Gdtobject):
    "A base container class, which contains several Gdtobjects"
    
    def apply(self, other):
        "copy from another object"
        raise NotImplementedError
        
class Gdtstruct(Gdtcontainer):
    "A base class, which can be used with gdtstruct_properties"    
    _fields = set()
    _types = dict()

    def test(self):
        all_ok = True
        for field in self._fields:
            if hasattr(self, "test" + field):
                tm = getattr(self, "test" + field)
                if type(tm) == type(self.test):
                    try:
                        all_ok &= tm()
                    except NotImplementedError: # pylint: disable-msg=W0704
                        # ignore not implemented test methods
                        pass
                        
            elif hasattr(self, "_" + field):
                val = getattr(self, "_" + field)
                if hasattr(val, "test"):
                    tm = getattr(val, "test")
                    if type(tm) == type(self.test):
                        try:
                            all_ok &= tm()
                        except NotImplementedError: # pylint: disable-msg=W0704
                            # ignore not implemented test methods
                            pass
        return all_ok
    
    def tostr(self, prefix_string = None):
        "returns a string in gdt representation"
        if prefix_string == None:
            prefix_string = self.__class__.__name__
        mstr = ""
        fields = list(self._fields)
        fields.sort()
        for name in fields:
            if hasattr(self, name):
                val = getattr(self, name)
                if val == None:
                    continue
                if isinstance(val, Gdtcontainer):
                    mstr += val.tostr("%s.%s" % (prefix_string, name))
                else:
                    mstr += "%s.%s=%s\n" % (prefix_string, name, str(val))
        return mstr

    def fromstr(self, vals, value):
        name=vals[0]

        if name in self._fields:
            if len(vals) > 1:
                o = getattr(self, name)
                if o == None:
                    o = self._types[name]()
                o.fromstr(vals[1:], value)
                setattr(self, name, o)
            else:
                if self._types[name] == bool:
                    setattr(self, name, value == "True" or False)
                else:
                    setattr(self, name, self._types[name](value))
        else:
            raise KeyError

    def apply(self, other):
        "copy from another object"
        for field in self._fields:
            if hasattr(other, field):
                setattr(self, field, getattr(other, field))
            
class Gdtlist(Transactionlist, Gdtcontainer):
    "A list base class, which can hold Gdtobjects in a list."
    _type=None

    def tostr(self, prefix_string = None):
        "returns a string in gdt representation"
        if prefix_string == None:
            prefix_string = self.__class__.__name__
        mstr = ""
        i = 0
        for value in self:
            i += 1
            if isinstance(value, Gdtobject):
                kid = value.keyid
                if kid:
                    kid = getattr(value, kid)
                else:
                    kid = str(i)
#                mstr += value.tostr("%s.%s.%s" 
#                                    % (prefix_string, kid, 
#                                       value.__class__.__name__))
                mstr += value.tostr("%s.%s" 
                                    % (prefix_string, kid))
            else:
                mstr += "%s.%d=%s\n" % (prefix_string, i, value)
                
        return mstr


    def fromstr(self, vals, value):
        if vals[0] == self._type.__name__:
            del vals[0]
        
        index = int(vals[0])
        
        if index > len(self):
            for i in range(0, index - len(self)):
                self.append(self._type())

        child = self[index-1]

        if isinstance(child, Gdtobject):
            child.fromstr(vals[1:], value)
        else:
            self[index-1] = self._type(value)

    def test(self):
        all_ok = True
        for val in self:
            if hasattr(val, "test"):
                tm = getattr(val, "test")
                if type(tm) == type(self.test):
                    try:
                        all_ok &= tm()
                    except NotImplementedError: # pylint: disable-msg=W0704
                        # ignore not implemented test methods
                        pass
                    
        return all_ok
    
    def apply(self, value):
        del self[:]
        self.extend(value)

Gdtstr = str
Gdtbool = bool
Gdtint = int
