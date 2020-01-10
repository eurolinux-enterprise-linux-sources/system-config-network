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

"""
    Transactions of attributes by inheriting the Transaction class

    Basic Usage:
    
    class Test(Transaction):
        pass
        
    a = Test()
    a.test = "old state"
    a.commit()
    a.test = "bad state, roll me back"
    a.rollback()
    assert(a.test == "old state")
    
 See also: http://www.harald-hoyer.de/linux/pythontransactionclass
 
 Copyright (C) 2008 Harald Hoyer <harald@redhat.com>
 Copyright (C) 2008 Red Hat, Inc.
"""
import copy
import logging


#_debuglevel = logging.DEBUG
_debuglevel = 0

def _checksetseen(what, seen):
    "checks and sets the obj id in seen"
    if what in seen:
        return True
    seen.add(what)
    return False

class Transaction(object):
    """
    This class allows sub-classes to commit changes to an instance to a 
    history, and rollback to previous states.
        
    Because the class only stores attributes in self.__dict__ sub-classes
    need to use the methods __getstate__ and __setstate__ to provide additional
    state information. See the Transactionlist below for an example usage.    
    """        
    def commit(self, **kwargs):
        """
        Commit the object state.
        
        If the optional argument "deep" is set to False,
        objects of class Transaction stored in this object will
        not be committed.
        """
        logging.log(_debuglevel, "Transaction.commit() %s",
                    self.__class__.__name__)
        seen = kwargs.get("_commit_seen", set())
        if _checksetseen(id(self), seen): 
            return
        deep = kwargs.get("deep", True)
        
        # Do not deepcopy the Transaction objects. We want to keep the 
        # reference. Instead commit() them.     
        state = dict()
        for key, val in self.__dict__.items():
            if isinstance(val, Transaction):
                state[key] = val
                if deep:
                    val.commit(_commit_seen = seen)
            elif key == "__l":
                # do not deepcopy our old state
                state[key] = val
            elif key == "__orig":
                state[key] = val
            else:
                state[key] = copy.deepcopy(val)
                
        if hasattr(self, '__getstate__'):            
            state = (state, getattr(self, '__getstate__')())

        self.__dict__["__l"] = state
                        
    def rollback(self, **kwargs):
        """
        Rollback the last committed object state.
        
        If the optional argument "deep" is set to False,
        objects of class Transaction stored in this object will
        not be rolled back.
        """
        logging.log(_debuglevel, "Transaction.rollback() %s",
                    self.__class__.__name__)
        seen = kwargs.get("_rollback_seen", set())
        if _checksetseen(id(self), seen):
            return
        
        deep = kwargs.get("deep", True)
        state = None
        extrastate = None
        gotstate = False
        gotextrastate = False
        if "__l" in self.__dict__:
            state = self.__dict__["__l"]
            gotstate = True
            if type(state) is tuple:
                gotextrastate = True
                (state, extrastate) = state

        # rollback our childs, then ourselves
        for child in self.__dict__.values():
            if isinstance(child, Transaction):
                if deep:
                    child.rollback(_rollback_seen = seen)
 
        if gotstate:
            self.__dict__.clear()
            self.__dict__.update(state)
            
        if gotextrastate and hasattr(self, '__setstate__'):
            getattr(self, '__setstate__')(extrastate)

    def setunmodified(self):
        "set the changed state of the object"
        logging.log(_debuglevel, "Transaction.setunmodified() %s",
                    self.__class__.__name__)        
        state = dict()
        for key, val in self.__dict__.items():
            if isinstance(val, Transaction):
                val.setunmodified()
                state[key] = val
            elif key != "__orig" and key != "__l" and key != "changed":
                state[key] = copy.deepcopy(val)
                
        if hasattr(self, '__getstate__'):            
            state = (state, getattr(self, '__getstate__')())

        self.__dict__["__orig"] = state

    
    def modified(self):
        logging.log(_debuglevel, "Transaction.modified() %s",
                    self.__class__.__name__)
        
        if "__orig" not in self.__dict__:
            logging.log(_debuglevel, '"__orig" not in self.__dict__')
            return True
        
        state = self.__dict__["__orig"]
        gotextrastate = False
        if type(state) is tuple:
            gotextrastate = True
            (state, extrastate) = state
        
        for key in state:
            if (key not in self.__dict__):
                logging.log(_debuglevel, "%s  not in self.__dict__" % key)
                return True
                
            if(self.__dict__[key] != state[key]):
                logging.log(_debuglevel, "%s %s != %s" % (key,
                             self.__dict__[key], state[key]))
                return True

            if isinstance(state[key],  Transaction):
                if state[key].modified():
                    return True

        for key in self.__dict__:
            if (key != "__orig" 
                and key != "__l" 
                and (key not in state) 
                and self.__dict__[key] != None):
                logging.log(_debuglevel, 
                            "%s is a new key in self.__dict__=%s" 
                              % (key, self.__dict__))
                return True
                
        if gotextrastate:            
            if hasattr(self, '__getstate__'):            
                state = getattr(self, '__getstate__')()
            else:
                logging.log(_debuglevel, "not hasattr(self, '__getstate__')")
                return True
            
            if extrastate != state:
                logging.log(_debuglevel, 
                            "state: %s != %s" % (extrastate, state))
                return True

        return False

class Transactionlist(list, Transaction):
    """
    An example subclass of list, which inherits transactions.
    
    Due to the special list implementation, we need the 
    __getstate__ and __setstate__ methods.
    
    See the code for the implementation.
    """
    def commit(self, **kwargs):
        """
        Commit the object state.
        
        If the optional argument "deep" is set to False,
        objects of class Transaction stored in this object will
        not be committed.
        """
        # make a local copy of the recursive marker
        seen = set(kwargs.get("_commit_seen", set()))
        
        super(Transactionlist, 
              self).commit(**kwargs) # pylint: disable-msg=W0142

        if _checksetseen(id(self), seen): 
            return
        
        deep = kwargs.get("deep", True)
        if deep:
            for val in self:
                if isinstance(val, Transaction):
                    val.commit()
        
    def rollback(self, **kwargs):
        """
        Rollback the last committed object state.
        
        If the optional argument "deep" is set to False,
        objects of class Transaction stored in this object will
        not be rolled back.
        """
        # make a local copy of the recursive marker
        seen = set(kwargs.get("_rollback_seen", set()))

        super(Transactionlist, 
              self).rollback(**kwargs) # pylint: disable-msg=W0142

        if _checksetseen(id(self), seen):
            return
        
        deep = kwargs.get("deep", True)
        if deep:
            for val in self:
                if isinstance(val, Transaction):
                    val.rollback()


    def modified(self):       
        for val in self:
            if isinstance(val, Transaction):
                if val.modified():
                    logging.log(_debuglevel, "List val.modified() == True")
                    return True
                    
        return super(Transactionlist, self).modified()

    def setunmodified(self):
        "set the changed state of the object"
        for val in self:
            if isinstance(val, Transaction):
                val.setunmodified()
        return super(Transactionlist, self).setunmodified()

    def __getstate__(self):
        """
        return a deepcopy of all non Transaction class objects in our list, 
        and a reference for the committed Transaction objects.
        
        """
        state  = []
        for val in self:
            if isinstance(val, Transaction):
                state.append(val)
            else:
                state.append(copy.deepcopy(val))
                
        return state        

    def __setstate__(self, state):
        "clear the list and restore all objects from the state"
        del self[:]
        self.extend(state)

__author__ = "Harald Hoyer <harald@redhat.com>"
