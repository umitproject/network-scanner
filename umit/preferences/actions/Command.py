# Copyright (C) 2007 Insecure.Com LLC.
# Copyright (C) 2008 Adriano Monteiro Marques.
#
# Author: Luis A. Bastiao Silva <luis.kop@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA



###################################################################
# This module is imported from InterfaceEditor Project!
###################################################################



import gobject


'''
Contains the system of Undo Redo 

Tricks: 
- Have a general Command with a trivial methods that not should be implemented
here
- Have a Stack of Commands
- Have a Manager of the all commands that emit a signal when something changes

'''


class Command(object):
    def __init__(self, description=''):
        self._description = description 
    
    def get_description(self):
        return self._description
    def execute(self):
        pass
    def undo(self):
        pass
    def redo(self):
        pass
    



class TwiceCommand(object):
    ''' 
    command twice states 
    
    '''
    def __init__(self, value = True ):
        self._state = value 
    #PRIVATE API 
    def _execute_1(self):
        ''' 
        subclass
        '''
    
    def _execute_2(self):
        '''
        subclass
        '''
    #Public API 
    def execute(self):
        if self._state: 
            self._execute_1()
        else:
            self._execute_2()
        self._state = not self._state

