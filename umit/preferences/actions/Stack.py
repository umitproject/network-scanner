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


MAX_STACK = 10

class Stack(object):
    '''
    Stack of Undo and Redo Commands 
    '''
    def __init__(self):
        
        
        # List of Commands
        self._commands = [] 
        self._current_command = -1 
    def can_undo(self):
        return self._current_command != -1 
    
    def can_redo(self):
        return self._current_command +1 != len(self._commands)
    def peek_redo(self):
        '''
        Peek the next redo if has. 
        @return : A string with description or None if not can redo 
        @rtype: str or None 
        '''
        if self.can_redo():
            return self._commands[self._current_command+1].get_description()
        return None 
    def peek_undo(self):
        '''
        Peek the previews undo if has. 
        @return: A string with a description or None if not can undo 
        @rtype: str or None 
        '''
        
        if self.can_undo():
            return self._commands[self._current_command+1].get_description()
        return None 
    def push(self, command):
        '''
        put only a command on the list 
        
        ''' 
        num  = len(self._commands)
        if num  == self._current_command:
            self._current_command += 1 
        else:
            old = self._current_command 
            self._current_command = num
            tmp = num - old
            if num % tmp != 0:
                tmp = tmp -1 
                
            for i in range(1, tmp):
                x = self._commands[old + i] 
                self._commands[old+i] = self._commands[num-i]
                self._commands[num-i] = x 
                
                
            
        self._commands.append(command)   
        
        
        #self._current_command += 1 
        #self._commands.append(command)     
        
    def push_undo(self, command):
        '''
        @param command: A subclass of Command that contains a command to execute 
        @type: Command or subclass
        
        '''
        self._commands.append(command)
        
        
        
    def pop_undo(self):
        '''
        @return: A command that it's in the list of commands 
        @rtype: Command or a subclass of Command
        '''
        if (self.can_undo()):
            cmd = self._commands[self._current_command]
            self._current_command -= 1
            return cmd 
        return None 
    def pop_redo(self):
        if (self.can_redo()):
            cmd = self._commands[self._current_command+1]
            self._current_command += 1
            return cmd 
        return None 
    
    
    