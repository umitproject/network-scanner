#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007 Adriano Monteiro Marques
#
# Author: Luís A. Bastião Silva <luis.kop@gmail.com>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA



import gobject


'''
Contains the system of Undo Redo 
of the UIE project

Tricks: 
- Have a general Command with a trivial methods that not should be implemented
here
- Have a Stack of Commands
- Have a Manager of the all commands that emit a signal when something changes

'''

MAX_STACK = 10

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
        
class CommandContainer(TwiceCommand, Command):
    def __init__(self, description, state, commands):
        Command.__init__(self, description)
        TwiceCommand.__init__(self, state)
        self._commands = commands
        self._reverse = False 
    def _execute_1(self):
        if self._reverse:
            self._commands.reverse()
        for i in self._commands:
            i.execute()
        self._reverse = True
    def _execute_2(self):
        #XXX: Later should be fix because it's only work in state = TRUE!
        self._commands.reverse()
        for i in self._commands:
            i.execute()
    
        
        
    
    
class CommandManager(gobject.GObject):
    __gsignals__ = {
        'changed':  (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, 
                     (gobject.TYPE_STRING,))
        }
    def __init__(self):
        gobject.GObject.__init__(self)
        self._progress = True 
        self._stack = Stack()
    
    # Public API
    def can_undo(self):
        return self._stack.can_undo()
    def can_redo(self):
        return self._stack.can_redo()
    def peek_undo(self):
        '''
        @return: description undo
        @rtype: str
        '''
        return self._stack.peek_undo()
    def peek_redo(self):
        '''
        @return: description redo
        @rtype: str
        '''
        return self._stack.peek_redo()
    def do_undo(self):
        cmd = self._stack.pop_undo()
        cmd.execute()
        self.emit('changed',None )
        #from umitInterfaceEditor.BugDiff import BugDiff
        #BugDiff.plist(self._stack._commands)
        #print self._stack._current_command
    
    def do_redo(self):
        cmd = self._stack.pop_redo()
        cmd.execute()
        self.emit('changed',None )
        #from umitInterfaceEditor import BugDiff
        #BugDiff.plist(self._stack._commands)
        #print self._stack._current_command

    def add_command(self, command):
        self._stack.push(command)
        command.execute()
        self.emit('changed',None )

    
command_manager = CommandManager()    